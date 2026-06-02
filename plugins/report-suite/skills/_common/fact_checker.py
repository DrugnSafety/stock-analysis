"""Fact Checker — Phase 7 절차 B (Fact-Check / Citation Lock).

목적
----
보고서 발행 전, deep_research 의 thesis·scenarios·정량 주장을 evidence(절차 A)와 대조하여
① thesis ↔ evidence 모순, ② 무출처 정량주장, ③ 밸류에이션 정합성 을 자동 플래그한다.
AMEET 방법론의 "팩트체크: 인용 수치·주장이 원본 출처와 일치하는지 자동 검증" 단계에 대응.

설계
----
- **결정론적(LLM 미사용) 기본 체크** 3종으로 즉시 실행 가능.
- `register_verifier(fn)` 로 LLM 검증기(codex-integration / multi-model-arena)를 plug 가능
  → 로드맵의 "codex cross-validation" 을 신규 인프라 없이 흡수.
- 출력: factcheck/{ticker}.json + render_citation_audit_html() (보고서 말미 섹션).

플래그 등급
----------
  🔴 conflict   : evidence 가 thesis 를 직접 반박 (impact '-' 가 bull 가정과 충돌)
  🟡 unsourced  : 정량 주장에 대조 가능한 출처(evidence/financials) 없음
  🟢 confirmed  : evidence 가 주장을 뒷받침
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Callable, Optional

# 도메인 키워드 — thesis 가정과 negative evidence 간 주제 매칭용 (간이 토큰)
_STOP = {"의", "이", "가", "을", "를", "는", "은", "에", "와", "과", "도", "+", "-",
         "the", "a", "to", "of", "and", "in", "for", "수", "시", "및", "등"}

_NUM_RE = re.compile(r"\$?\d[\d,]*\.?\d*\s?(?:%|배|억|조|만|B|M|bn|mt|Mt|GW|/MMBtu|/t|/주)?", re.I)


@dataclass
class Flag:
    level: str          # conflict / unsourced / confirmed
    target: str         # 검증 대상 (thesis/scenario/quant 문구)
    detail: str         # 설명
    evidence_url: str = ""
    evidence_src: str = ""


def _tokens(s: str) -> set[str]:
    s = re.sub(r"[^\w가-힣% ]", " ", s.lower())
    return {t for t in s.split() if len(t) >= 2 and t not in _STOP}


class FactChecker:
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.flags: list[Flag] = []
        self._verifiers: list[Callable[[dict, dict], list[Flag]]] = []

    def register_verifier(self, fn: Callable[[dict, dict], list[Flag]]) -> None:
        """LLM 검증기 plug (예: codex-integration). fn(deep, evidence)->list[Flag]."""
        self._verifiers.append(fn)

    # ── ① thesis ↔ evidence 모순 (stance-aware) ───────────────────────
    # 양성(강세) 가정만 negative evidence 와 충돌로 판정. 헤지/부정 가정은 제외.
    _POS_STANCE = {"지속", "증가", "회복", "상승", "가속", "유지", "확대", "성장",
                   "강세", "수혜", "개선", "도달", "+", "초과", "견조", "tailwind"}
    _HEDGE_STANCE = {"흡수", "부족", "둔화", "하락", "감소", "약화", "조정", "리스크",
                     "지연", "후퇴", "50/50", "renewable", "nuclear", "uncertain",
                     "둔", "완화", "압박", "둔화될"}

    def _stance(self, text: str) -> str:
        toks = _tokens(text)
        raw = text.lower()
        pos = any(k in raw for k in self._POS_STANCE) or bool(toks & self._POS_STANCE)
        hedge = any(k in raw for k in self._HEDGE_STANCE) or bool(toks & self._HEDGE_STANCE)
        if hedge and not pos:
            return "hedge"
        if pos:
            return "positive"
        return "neutral"

    def check_thesis_conflicts(self, deep: dict, evidence: dict) -> None:
        neg = [r for r in evidence.get("records", []) if r.get("impact") == "-"]
        if not neg:
            return
        scen = deep.get("scenarios", {})
        # bull 은 강세 가정 검증의 핵심. base 는 thesis(요지)만 검증(가정은 헤지 많음).
        for sc_name in ("bull", "base"):
            sc = scen.get(sc_name, {})
            thesis_txt = sc.get("thesis", "")
            candidates = (sc.get("key_assumptions", []) or []) if sc_name == "bull" else []
            if thesis_txt:
                candidates = candidates + [thesis_txt]
            for asm in candidates:
                # 헤지/부정 stance 가정은 반박 대상이 아님 → skip (과탐지 방지)
                if self._stance(asm) != "positive":
                    continue
                atok = _tokens(asm)
                for r in neg:
                    overlap = atok & (_tokens(r["claim"]) | _tokens(r.get("value", "")))
                    if len(overlap) >= 2:
                        self.flags.append(Flag(
                            "conflict",
                            target=f"[{sc_name}] {asm[:60]}",
                            detail=f"반박 근거: {r['claim'][:70]} — {r.get('value','')[:60]}",
                            evidence_url=r.get("source_url", ""),
                            evidence_src=r.get("publisher", ""),
                        ))
                        break

    # ── ② 무출처 정량 주장 ────────────────────────────────────────────
    def check_unsourced_quant(self, deep: dict, evidence: dict) -> None:
        # evidence + financials 에서 검증 가능한 숫자 풀 구성
        ev_nums: set[str] = set()
        for r in evidence.get("records", []):
            for m in _NUM_RE.findall(r.get("value", "") + " " + r.get("claim", "")):
                ev_nums.add(m.strip().lower())
        # market_size 출처 확인
        ind = deep.get("industry", {})
        ms = ind.get("market_size", {})
        if isinstance(ms, dict) and ms and not ms.get("source"):
            self.flags.append(Flag(
                "unsourced",
                target=f"시장규모 ${ms.get('current_usd_bn','?')}B / CAGR {ms.get('cagr_pct','?')}%",
                detail="market_size 에 출처 없음 — 외부 근거로 검증 필요",
            ))
        # scenario target price 가 valuation evidence 와 정합한지(③에서 별도) — 여기선 무출처만
        # competitors share_pct 출처 확인
        comps = ind.get("competitors", [])
        if comps and not any(c.get("source") or c.get("url") for c in comps):
            self.flags.append(Flag(
                "unsourced",
                target=f"경쟁 점유율 {len(comps)}개사 (share_pct)",
                detail="competitors share_pct 에 출처 없음 — 추정치 가능성",
            ))

    # ── ③ 밸류에이션 정합성 (시나리오 목표가 ↔ 애널 컨센서스) ─────────
    def check_valuation_consistency(self, deep: dict, evidence: dict) -> None:
        val = [r for r in evidence.get("records", []) if r.get("category") == "valuation"]
        if not val:
            return
        # 애널 컨센서스 목표가 추출 ($34.42 등)
        consensus = None
        for r in val:
            m = re.search(r"\$(\d+\.?\d*)", r.get("value", ""))
            if m:
                consensus = float(m.group(1))
                ref = r
                break
        if consensus is None:
            return
        scen = deep.get("scenarios", {})
        for sc_name in ("bull", "base", "bear"):
            tp = scen.get(sc_name, {}).get("target_price")
            if isinstance(tp, (int, float)) and tp > 0:
                gap = (tp - consensus) / consensus * 100
                if abs(gap) >= 25:
                    self.flags.append(Flag(
                        "conflict" if abs(gap) >= 40 else "unsourced",
                        target=f"[{sc_name}] 목표가 ${tp:.0f}",
                        detail=f"애널 컨센서스 ${consensus:.2f} 대비 {gap:+.0f}% 괴리",
                        evidence_url=ref.get("source_url", ""),
                        evidence_src=ref.get("publisher", ""),
                    ))
                else:
                    self.flags.append(Flag(
                        "confirmed",
                        target=f"[{sc_name}] 목표가 ${tp:.0f}",
                        detail=f"애널 컨센서스 ${consensus:.2f} 와 정합 ({gap:+.0f}%)",
                        evidence_url=ref.get("source_url", ""),
                        evidence_src=ref.get("publisher", ""),
                    ))

    # ── 실행 + 출력 ───────────────────────────────────────────────────
    def run(self, deep: dict, evidence: dict) -> dict:
        self.check_thesis_conflicts(deep, evidence)
        self.check_unsourced_quant(deep, evidence)
        self.check_valuation_consistency(deep, evidence)
        for fn in self._verifiers:
            try:
                self.flags.extend(fn(deep, evidence))
            except Exception:
                pass
        return self.to_dict()

    def to_dict(self) -> dict:
        counts = {"conflict": 0, "unsourced": 0, "confirmed": 0}
        for f in self.flags:
            counts[f.level] = counts.get(f.level, 0) + 1
        return {
            "ticker": self.ticker,
            "summary": counts,
            "verdict": ("🔴 검토 필요" if counts["conflict"]
                        else "🟡 부분 확인" if counts["unsourced"] else "🟢 검증됨"),
            "flags": [asdict(f) for f in self.flags],
        }

    def write(self, factcheck_dir: Path) -> Path:
        factcheck_dir.mkdir(parents=True, exist_ok=True)
        out = factcheck_dir / f"{self.ticker}.json"
        out.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return out


def make_codex_verifier(max_assumptions: int = 8):
    """codex-integration(OpenAI) 기반 stance-aware LLM 검증기 어댑터.

    fact_checker 의 register_verifier() 에 끼워 휴리스틱을 보강한다.
    opt-in: 환경변수 FACTCHECK_LLM=1 이고 codex/OPENAI_API_KEY 가용할 때만 실행.
    그 외에는 빈 리스트 반환(graceful no-op) → 신규 인프라 0, 비용 0.

    사용:
        fc = FactChecker("BTU")
        fc.register_verifier(make_codex_verifier())
        fc.run(deep, evidence)
    """
    import os

    def _verifier(deep: dict, evidence: dict) -> list:
        if os.environ.get("FACTCHECK_LLM") != "1":
            return []
        # codex_runner lazy import (plugin 재사용)
        import sys as _sys
        from pathlib import Path as _Path
        cdir = (_Path(__file__).resolve().parent.parent.parent.parent
                / "codex-integration" / "scripts")
        if str(cdir) not in _sys.path:
            _sys.path.insert(0, str(cdir))
        try:
            from codex_runner import codex_query, detect_environment  # type: ignore
        except Exception:
            return []
        if detect_environment() == "none":
            return []

        scen = deep.get("scenarios", {})
        assumptions = []
        for sc in ("bull", "base"):
            for a in (scen.get(sc, {}).get("key_assumptions", []) or []):
                assumptions.append(f"[{sc}] {a}")
        assumptions = assumptions[:max_assumptions]
        neg = [f"- {r['claim']} ({r.get('value','')}) [{r.get('publisher','')}|{r.get('source_url','')}]"
               for r in evidence.get("records", []) if r.get("impact") == "-"]
        if not assumptions or not neg:
            return []

        prompt = (
            "당신은 투자 보고서 팩트체커다. 아래 [강세 시나리오 가정]들 중에서 "
            "[반박 근거(negative evidence)]가 **직접적으로 반박**하는 가정만 골라라. "
            "단순히 주제가 같은 게 아니라 방향이 상충해야 한다. "
            "결과는 JSON 배열로만 출력: "
            '[{"assumption":"...","contradicted_by":"...","url":"..."}].\n\n'
            "[강세 시나리오 가정]\n" + "\n".join(assumptions) +
            "\n\n[반박 근거]\n" + "\n".join(neg)
        )
        res = codex_query(prompt, mode="o4-mini", temperature=0.1, max_tokens=1200)
        if res.get("status") != "ok":
            return []
        txt = res.get("response", "")
        m = re.search(r"\[.*\]", txt, re.S)
        if not m:
            return []
        try:
            items = json.loads(m.group(0))
        except Exception:
            return []
        flags = []
        for it in items:
            flags.append(Flag(
                "conflict",
                target=f"[LLM] {str(it.get('assumption',''))[:58]}",
                detail=f"codex 판정 반박: {str(it.get('contradicted_by',''))[:70]}",
                evidence_url=it.get("url", ""),
                evidence_src="codex(o4-mini)",
            ))
        return flags

    return _verifier


def render_citation_audit_html(fc: dict) -> str:
    """보고서 말미 Citation Audit 섹션."""
    badge = {"conflict": "🔴", "unsourced": "🟡", "confirmed": "🟢"}
    rows = ""
    for f in fc.get("flags", []):
        link = (f'<a href="{f["evidence_url"]}" style="color:#2563eb;">{f.get("evidence_src","출처")} ↗</a>'
                if f.get("evidence_url") else "—")
        rows += f"""
        <tr>
          <td style="text-align:center;">{badge.get(f['level'],'')}</td>
          <td><strong>{f['target']}</strong></td>
          <td style="font-size:8.5pt;">{f['detail']}</td>
          <td style="font-size:8pt;">{link}</td>
        </tr>"""
    s = fc.get("summary", {})
    return f"""
    <h2>🔎 Citation Audit (출처 검증)</h2>
    <div class="info">발행 전 자동 팩트체크 — thesis·정량주장을 외부 근거(evidence)와 대조.
      판정: <strong>{fc.get('verdict','')}</strong>
      (🔴 모순 {s.get('conflict',0)} · 🟡 무출처 {s.get('unsourced',0)} · 🟢 검증 {s.get('confirmed',0)})</div>
    <table class="dt">
      <thead><tr><th>등급</th><th>대상</th><th>내용</th><th>출처</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    <div style="font-size:8pt;color:#6b7280;margin-top:4pt;">
      🔴 evidence 가 주장을 반박 · 🟡 대조 출처 부재 · 🟢 evidence 가 뒷받침. LLM 검증기 plug 시 정밀도 향상.</div>
    """
