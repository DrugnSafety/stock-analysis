"""페르소나 SKILL.md 로드 — subagent system prompt에 주입할 텍스트 추출."""
import json
import re
import sys
from pathlib import Path


def find_persona_dir() -> Path:
    """workspace의 plugins/investor-personas/personas/ 위치 탐색."""
    cwd = Path.cwd()
    for ancestor in [cwd] + list(cwd.parents)[:5]:
        candidate = ancestor / "plugins" / "investor-personas" / "personas"
        if candidate.exists():
            return candidate
    # default
    return Path("plugins/investor-personas/personas")


def load_persona(persona_id: str) -> dict:
    """SKILL.md 파일을 읽어 (frontmatter, body) 반환."""
    persona_dir = find_persona_dir()
    skill_path = persona_dir / persona_id / "SKILL.md"
    if not skill_path.exists():
        return {"error": f"persona not found: {persona_id}"}

    raw = skill_path.read_text(encoding="utf-8")
    fm = {}
    body = raw
    if raw.startswith("---"):
        end = raw.find("---", 3)
        front = raw[3:end].strip()
        body = raw[end+3:].strip()
        for line in front.split("\n"):
            if ":" in line and not line.lstrip().startswith("#"):
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip().strip("\"'")

    return {
        "persona_id": persona_id,
        "name_kr": fm.get("name_kr", persona_id),
        "name_en": fm.get("name", "").replace("-", " ").title(),
        "frontmatter": fm,
        "body": body,
        "raw": raw,
    }


SUBAGENT_SYSTEM_TEMPLATE = """You are evaluating a stock through a specific investor persona's lens.

Below is the persona's complete SKILL.md. Follow its Required Analysis Sequence step-by-step.
Apply Decision Rules to reach a verdict. Tag every number with [actual]/[estimated]/[assumption]/[derived]/[unavailable].

=== PERSONA SKILL.md ===
{persona_skill}
=== END PERSONA ===

=== 의무 평가 절차 (THESIS-AWARE QUANT ANCHORING) ===

당신은 평가 시 다음 3단계를 의무적으로 수행하고 출력에 명시해야 합니다:

STEP 1 — Thesis별 lens 적용:
블로거가 제시한 thesis (T01, T02, ...) 각각에 대해, 당신의 페르소나 lens에서
어떻게 해석되는지 명시하세요. (예: "T03 'TMX 89만 b/d 캐파' — Buffett lens:
인프라 투자는 capital intensive이나 ROIC 입증되면 moat. 현재로는 ROIC 데이터 부족.")

STEP 2 — 정량 anchor와 thesis 정합:
시장 정량 데이터(PE, ROE, FCF margin, 변동성 등) 중 어느 metric이 어느 thesis를
강화/약화하는지 명시. (예: "PE 3.76 [actual]은 메르의 'AI 거품' thesis와 정합 —
시장이 이미 EPS 하락을 가격화. HBM 수혜 thesis는 정량으로 미검증.")

STEP 3 — 정량 vs narrative 충돌 처리:
정량 신호와 thesis가 충돌할 때 당신의 페르소나는 어느 것을 더 무겁게 가중하는가?
(예: "Buffett은 30%+ margin of safety 부재가 narrative보다 우선 — 따라서 lean_bearish")
이는 페르소나의 핵심 정체성을 반영해야 함.

=== 출력 JSON 스키마 ===

{{
  "verdict": "lean_bullish | lean_bearish | neutral",
  "confidence": 0.0-1.0,
  "horizon": "short_term | medium_term | long_term",
  "key_argument": "1-2 sentence summary of your strongest point",
  "rationale": "3-5 sentence reasoning following Required Analysis Sequence",
  "thesis_lens_applications": [
    {{"claim_id": "T01", "persona_take": "당신의 lens로 해석", "stance": "support | challenge | neutral"}}
  ],
  "quant_anchor_validation": [
    {{"metric": "forward_pe 3.76", "supports_thesis": "T03 (AI 거품 우려)", "tag": "[actual]"}}
  ],
  "narrative_vs_quant_resolution": "충돌 시 어느 것을 우선했는가 + 페르소나 정체성 명시",
  "data_tags": ["[actual] ...", "[inference] ..."],
  "key_concerns": ["..."],
  "key_opportunities": ["..."],
  "uncertainty": "what assumption, if violated, would flip your verdict"
}}

Output JSON only, no prose outside JSON.
"""


def make_subagent_prompt(persona_id: str, ticker: str, market_data: dict = None,
                          blog_context: str = "", round_num: int = 1,
                          opposite_arguments: list = None) -> tuple[str, str]:
    """페르소나 subagent용 (system_prompt, user_prompt) 생성."""
    p = load_persona(persona_id)
    if "error" in p:
        raise SystemExit(p["error"])

    system = SUBAGENT_SYSTEM_TEMPLATE.format(persona_skill=p["raw"])

    user_parts = [f"Ticker: {ticker}", f"Round: {round_num}"]
    if market_data:
        user_parts.append(f"\nMarket data:\n{json.dumps(market_data, ensure_ascii=False, indent=2)}")
    if blog_context:
        user_parts.append(f"\nBlog context:\n{blog_context[:6000]}")

    if opposite_arguments and round_num > 1:
        user_parts.append(f"\n\n--- 이전 round의 상대 의견 (검토 후 verdict 갱신 또는 유지) ---")
        for arg in opposite_arguments[-3:]:  # 최근 3개만
            user_parts.append(f"- [{arg.get('persona', 'opposite')}] {arg.get('verdict', '?')} "
                             f"(conf {arg.get('confidence', 0)}): {arg.get('key_argument', '')}")
        user_parts.append("\n위 상대 의견을 본 뒤 당신의 입장을 update하거나 유지하세요.")

    return system, "\n".join(user_parts)


SKEPTIC_SYSTEM = """You are a Skeptic / Devil's Advocate analyst.

Your role:
1. Read both Bull and Bear arguments from the round
2. Identify the strongest weak point in EACH side
3. Highlight hidden assumptions that could break either thesis
4. Assess: are they converging on the same verdict, or diverging?

Output JSON:
{
  "bull_weakness": "strongest counter to bull",
  "bear_weakness": "strongest counter to bear",
  "hidden_assumptions": ["assumption 1", "..."],
  "agreement_assessment": "high | medium | low | split",
  "key_question_for_next_round": "specific question for them to address",
  "convergence_direction": "toward bullish | toward bearish | none | both holding"
}

JSON only.
"""


CONSOLIDATOR_SYSTEM = """You are a portfolio manager consolidating a multi-round Bull-Bear-Skeptic debate
into a final verdict.

Read all rounds of:
- Bull arguments (Druckenmiller persona)
- Bear arguments (Buffett persona)
- Skeptic critiques

Synthesize:
- Did they converge? On which verdict?
- What were the most defensible arguments?
- What is the final verdict + confidence (calibrated, not overconfident)?

Output JSON:
{
  "final_verdict": "lean_bullish | lean_bearish | neutral",
  "final_confidence": 0.0-1.0,
  "horizon": "short_term | medium_term | long_term",
  "consolidation_reasoning": "4-6 sentences explaining how you arrived at this verdict",
  "key_drivers": ["..."],
  "key_risks": ["..."],
  "data_tags": ["[actual] ...", "[inference] ...", "[assumption] ..."],
  "remaining_uncertainties": ["..."],
  "rounds_summary": "1 sentence per round"
}

JSON only.
"""


if __name__ == "__main__":
    if len(sys.argv) > 1:
        p = load_persona(sys.argv[1])
        print(json.dumps({
            "persona_id": p.get("persona_id"),
            "name_kr": p.get("name_kr"),
            "name_en": p.get("name_en"),
            "body_length": len(p.get("body", "")),
        }, ensure_ascii=False, indent=2))
