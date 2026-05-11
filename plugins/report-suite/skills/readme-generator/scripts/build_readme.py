#!/usr/bin/env python3
"""분석 sample별 README.md 자동 생성 — 학습용 자세한 설명."""
import argparse
import json
from datetime import datetime
from pathlib import Path


PERSONA_NAMES = {
    "warren-buffett": "워런 버핏 (Warren Buffett)",
    "charlie-munger": "찰리 멍거 (Charlie Munger)",
    "peter-lynch": "피터 린치 (Peter Lynch)",
    "cathie-wood": "캐시 우드 (Cathie Wood)",
    "michael-burry": "마이클 버리 (Michael Burry)",
    "nassim-taleb": "나심 탈레브 (Nassim Taleb)",
    "ben-graham": "벤저민 그레이엄 (Ben Graham)",
    "bill-ackman": "빌 애크먼 (Bill Ackman)",
    "mohnish-pabrai": "모니시 파브라이 (Mohnish Pabrai)",
    "phil-fisher": "필 피셔 (Phil Fisher)",
    "rakesh-jhunjhunwala": "라케시 준준왈라 (Rakesh Jhunjhunwala)",
    "stanley-druckenmiller": "스탠리 드러켄밀러 (Stanley Druckenmiller)",
    "aswath-damodaran": "애스워드 다모다란 (Aswath Damodaran)",
}


BLOGGER_INTRO = {
    "ranto28": "메르 — '메르의 블로그' 운영자. 비즈니스·경제 거시 시각으로 '다른 시각으로 세상을 정리'. 번호 매김 형식의 사실 누적 후 한 줄 코멘트 결론 스타일. 36만+ 이웃.",
    "doctordk": "의교창 — '군포금융치료센터'. 'Life is unfair, get used to it.' 산업·매크로 분석에 능함. 2차전지·반도체·지정학 다각도 시각.",
    "sungdory": "승도리 — '과거에 잘했다고 앞으로도 잘 할거라 생각하지 마라'. 짧고 신랄한 시장 코멘트. 현실주의·냉정 투자.",
    "daegurrr_": "DaeGurr — 산업 분석 + 구루 단상. 탱커·해운·매크로 산업 분석에 강함.",
    "dlaldhr0821": "GSVI — '가치투자자 GSVI 주식투자 블로그'. 가치투자 (Graham·Buffett 계열) 철학.",
    "infidoc": "인피의 — '투자와 생각들'. 'risky world, hedged mind'. 미국 바이오텍에 집중. 한국 바이오의 기형적 valuation 회피.",
    "onejejuwave": "제주바람 — '제주바람의 투자기록'. 제주 전업 투자자, 쌍둥이 육아. AI·실전 trade 기록.",
    "tosoha1": "농구천재 — '이것 또한 지나가리라'. 메모리·NAND·AI 인프라 데이터 분석.",
}


def render_thesis_section(thesis_data: dict) -> str:
    summary = thesis_data.get("summary_one_liner", "")
    theses = thesis_data.get("theses", [])

    md = f"## 📋 글의 핵심 주장 (Thesis)\n\n"
    md += f"**한 줄 요약**: {summary}\n\n"
    md += "이 글에서 추출한 thesis는 다음과 같습니다:\n\n"
    md += "| ID | Claim | Type | Importance | Timeframe |\n"
    md += "|---|---|---|---|---|\n"
    for t in theses:
        md += f"| {t.get('claim_id')} | {t.get('claim','')} | {t.get('type')} | {t.get('importance')} | {t.get('timeframe')} |\n"
    md += "\n"
    md += "**Thesis Type 의미**:\n"
    md += "- `factual` (사실): 검증 가능한 사실. 예: '2026.4.20 무관세 적용'\n"
    md += "- `predictive` (예측): 미래 예측·추론. 예: 'Panamax 만재가 합리적 대안이 될 것'\n"
    md += "- `normative` (규범): 가치 판단·권고. 예: '본업 실적 함께 봐야 한다'\n"
    md += "- `conditional` (조건부): 'if X then Y' 명제\n\n"
    md += "**Importance 의미**:\n"
    md += "- `core` (핵심): 글 전체의 thesis pillar. 평가의 중심.\n"
    md += "- `supporting` (부수): core를 뒷받침하는 사실.\n"
    md += "- `aside` (여담): 글 흐름상 추가된 정보. 평가 제외.\n\n"
    return md


def render_4analyst_section(eval_data: dict) -> str:
    md = "## 🔬 4-Analyst 정량 평가 결과\n\n"
    md += "각 thesis가 정량 데이터·역사적 사례로 검증되는지를 4명의 analyst가 독립 평가합니다.\n\n"
    md += "**4-Analyst Lens 설명**:\n"
    md += "- **Macro Analyst**: 거시경제·정책·지정학 관점. '거시 환경이 이 thesis를 강화/약화하는가?'\n"
    md += "- **Industry Analyst**: 산업·기업 미시 관점. '산업 사이클·기업 capex와 정합한가?'\n"
    md += "- **Empirical Analyst**: 정량·역사적 사례. '데이터로 검증되는가? 비슷한 사례는?'\n"
    md += "- **Counter (Devil's Advocate)**: 의도적 반박. '가장 강한 반론은? 어떤 가정이 무너지면 틀리는가?'\n\n"
    md += "각 analyst는 stance(support/neutral/rebut) + confidence(0-1)로 평가하며, 4명 합의가 종합 stance와 weighted_confidence를 결정합니다.\n\n"

    if not eval_data.get("aggregates"):
        return md

    md += "### Thesis별 합의 결과\n\n"
    md += "| Thesis | 합의 stance | 신뢰도 | Agreement |\n"
    md += "|---|---|---|---|\n"
    for a in eval_data.get("aggregates", []):
        agg = a.get("aggregate", {})
        md += f"| {a.get('claim_id')}: {a.get('claim','')} | **{agg.get('weighted_stance','?')}** | {int((agg.get('weighted_confidence') or 0)*100)}% | {agg.get('agreement_level','')} |\n"
    md += "\n"
    md += "**Agreement Level 의미**:\n"
    md += "- `high (4/4)`: 4명 만장일치 — 가장 강한 신호\n"
    md += "- `medium-high (3/4)`: 3명 합의 + 1명 이견 — 신뢰 높음\n"
    md += "- `split (2/4)`: 분열 — 본인 판단 필요\n"
    md += "- `low`: 합의 부재 — verdict 약함\n\n"
    return md


def render_persona_panel_section(panel_data: dict) -> str:
    md = "## 🎭 13명 페르소나 패널 결과\n\n"
    md += "전설적 투자자 13명의 lens로 같은 fact-base를 평가합니다. **같은 사실 × 다른 철학 = 다른 결론**.\n\n"

    dist = panel_data.get("verdict_distribution", {})
    bull = dist.get("lean_bullish", {}).get("count", 0)
    neu = dist.get("neutral", {}).get("count", 0)
    bear = dist.get("lean_bearish", {}).get("count", 0)
    avg_conf = panel_data.get("average_confidence", 0)

    md += "### Verdict 분포\n\n"
    md += f"| 매수 성향 | 중립 | 매도 성향 | 평균 신뢰도 |\n"
    md += f"|---|---|---|---|\n"
    md += f"| 🟢 **{bull}** | 🟡 {neu} | 🔴 {bear} | {int(avg_conf*100)}% |\n\n"

    personas = panel_data.get("persona_results", {})
    md += "### 13명 verdict 매트릭스\n\n"
    md += "| 페르소나 | 카테고리 | Verdict | Confidence |\n"
    md += "|---|---|---|---|\n"
    for pid, p in sorted(personas.items(), key=lambda x: -(x[1].get('confidence') or 0)):
        kr = PERSONA_NAMES.get(pid, pid)
        v = p.get("verdict", "neutral")
        emoji = {"lean_bullish": "🟢", "neutral": "🟡", "lean_bearish": "🔴"}.get(v, "⚪")
        md += f"| {kr} | - | {emoji} {v} | {int((p.get('confidence') or 0)*100)}% |\n"
    md += "\n"

    # Style split
    style = panel_data.get("style_split", {})
    if style:
        md += "### Style Split — 투자 스타일별 합의\n\n"
        for cat, info in style.items():
            md += f"- **{cat.upper()}** ({info.get('n_members', 0)}명): 우세 = {info.get('dominant', '?')}\n"
        md += "\n"
        md += "**왜 Style Split이 중요한가**: 같은 사실에 대해 가치파(Buffett·Munger·Graham)가 lean_bullish인데 risk파(Taleb)가 lean_bearish인 경우, 두 lens 모두 valid한 경고. 본인 투자 철학에 가까운 페르소나의 verdict에 더 무게를 두되, 다른 lens의 우려도 검토해야 합니다.\n\n"

    # Universal concerns
    concerns = panel_data.get("universal_concerns", [])
    if concerns:
        md += "### Universal Concerns — 다수가 공유하는 우려\n\n"
        for c in concerns[:5]:
            md += f"- **[{c['theme']}]** ({c['frequency']}건): {(c.get('examples') or ['-'])[0][:120]}\n"
        md += "\n"
        md += "**의미**: 다수 페르소나(보통 5명+)가 같은 우려를 공유하면 가장 신뢰도 높은 risk 신호입니다. 공유 우려를 무시하면 안 됩니다.\n\n"

    return md


def render_decision_section(decisions: list, portfolio: dict) -> str:
    md = "## 💼 Trade Decision (Risk-Adjusted)\n\n"
    md += "13명 페르소나 + thesis-first verdict를 페르소나 가중치로 weighted average한 후, Risk Manager의 변동성-조정 한도 내에서 trade decision을 도출합니다.\n\n"
    md += "**Signal Score 해석**:\n"
    md += "- `+0.7 이상`: 한도까지 buy 진입 (high conviction)\n"
    md += "- `+0.3 ~ +0.7`: 한도의 50% buy (medium)\n"
    md += "- `-0.3 ~ +0.3`: hold (변경 없음)\n"
    md += "- `-0.7 ~ -0.3`: sell partial (보유분 50% 청산)\n"
    md += "- `-0.7 이하`: sell all (전량 청산)\n\n"

    if not decisions:
        return md

    md += "### Trade Decisions\n\n"
    md += "| 종목 | Signal | Action | 수량 | 한도 % |\n"
    md += "|---|---|---|---|---|\n"
    for d in decisions:
        if "error" in d:
            continue
        md += f"| {d.get('ticker')} | {d.get('signal_score', 0):+.2f} | {d.get('action')} | {d.get('target_quantity', 0):,}주 | {d.get('combined_limit_pct', 0)*100:.1f}% |\n"
    md += "\n"

    if portfolio:
        ret = portfolio.get("total_return_pct", 0)
        md += f"### Paper Portfolio 결과\n\n"
        md += f"- **Total Return**: {ret:+.2f}%\n"
        md += f"- **Final NAV**: {portfolio.get('final_nav', 0):,.0f}\n"
        md += f"- **Trades**: {portfolio.get('total_trades', 0)}\n\n"
    return md


def main():
    parser = argparse.ArgumentParser(description="Sample README generator")
    parser.add_argument("--blogger", required=True, help="blogger ID (예: doctordk)")
    parser.add_argument("--blog-url", required=True)
    parser.add_argument("--blog-title", required=True)
    parser.add_argument("--published-at", required=True)
    parser.add_argument("--thesis", required=True)
    parser.add_argument("--eval-dir", required=True)
    parser.add_argument("--panel-aggregate", help="aggregate.json (단일 종목)")
    parser.add_argument("--decisions")
    parser.add_argument("--portfolio")
    parser.add_argument("--reports-dir", help="R1/R2/R3 PDF 경로")
    parser.add_argument("--output", "-o", required=True)
    args = parser.parse_args()

    with open(args.thesis, encoding="utf-8") as f:
        thesis_data = json.load(f)

    eval_data = {}
    eval_path = Path(args.eval_dir) / "all_aggregate.json"
    if eval_path.exists():
        with open(eval_path, encoding="utf-8") as f:
            eval_data = json.load(f)

    panel_data = {}
    if args.panel_aggregate and Path(args.panel_aggregate).exists():
        with open(args.panel_aggregate, encoding="utf-8") as f:
            panel_data = json.load(f)

    decisions = []
    portfolio = {}
    if args.decisions and Path(args.decisions).exists():
        with open(args.decisions, encoding="utf-8") as f:
            decisions = json.load(f).get("decisions", [])
    if args.portfolio and Path(args.portfolio).exists():
        with open(args.portfolio, encoding="utf-8") as f:
            portfolio = json.load(f)

    blogger_intro = BLOGGER_INTRO.get(args.blogger, args.blogger)

    md = f"""# 분석 README — {args.blog_title}

## 📌 분석 개요

| 항목 | 값 |
|---|---|
| **블로거** | {args.blogger} |
| **블로그 URL** | [{args.blog_url}]({args.blog_url}) |
| **글 제목** | {args.blog_title} |
| **글 발행일** | {args.published_at} |
| **분석 일자** | {datetime.now().strftime('%Y-%m-%d')} |

## 👤 블로거 소개

{blogger_intro}

## 🧠 분석 시스템 — 어떻게 작동하는가?

이 분석은 **8단계 자동 파이프라인**으로 작동합니다:

1. **본문 fetch** (naver-blog-scraper): 모바일 페이지에서 본문·메타데이터 수집
2. **Thesis 추출** (Claude 인라인): 글에서 핵심 주장 6-8개를 분리
3. **4-Analyst 평가** (Macro/Industry/Empirical/Counter): 각 thesis를 4개 lens로 정량 검증
4. **종목 식별 + market data** (yfinance): 영향받는 종목과 현재가·PE·변동성·수익률 수집
5. **★ 13명 페르소나 패널** (Buffett~Damodaran): 전설적 투자자 13명의 lens로 종목 평가 (thesis-aware: 각 페르소나가 thesis 인용 + 정량 anchor 검증)
6. **Risk Manager**: 변동성·상관관계로 종목별 position 한도 계산
7. **Portfolio Manager**: verdict aggregate(페르소나 가중치 적용) → trade decision
8. **R1+R2+R3 PDF + 이 README**: 자동 산출

각 단계의 결과는 모두 JSON으로 저장되어 추후 backtester가 적중률·alpha를 자동 측정합니다.

{render_thesis_section(thesis_data)}

{render_4analyst_section(eval_data)}

{render_persona_panel_section(panel_data) if panel_data else ''}

{render_decision_section(decisions, portfolio)}

## 📂 산출 보고서 3종

이 분석은 다음 3종 PDF를 자동 생성합니다 (모두 차트 포함):

| 보고서 | 페이지 수 | 대상 독자 | 핵심 내용 |
|---|---|---|---|
| **R1 Quant Anchor** | ~10p | 정량 분석가 | Fundamentals·Technical·4-Analyst 평가·Risk metrics·정량 metric 용어 풀이·데이터 태깅 시스템 교육 |
| **R2 Persona Panel** | ~20p (per ticker) | 투자 철학 비교 학습자 | **13명 페르소나의 철학·배경·5단계 분석 + Thesis × Persona Matrix + Universal Concerns + 각 페르소나 narrative vs quant resolution** |
| **R3 Executive Summary** | ~6p | 의사결정자 | 한 페이지 결정 시트 + Verdict·Confidence 해석 가이드 + 핵심 위험 5개 + 모니터링 포인트 + 의사결정 가이드 |

### 보고서 읽는 순서 권고

**처음 보시는 분께**:
1. 먼저 **R3 Executive Summary** — 한 페이지 Decision Sheet + 의사결정 가이드로 전체 그림 파악
2. 그 다음 **R2 Persona Panel** — 13명 대가의 reasoning을 비교하며 자신의 투자 철학 찾기
3. 마지막 **R1 Quant Anchor** — 정량 데이터·4-Analyst 평가가 위 결론을 어떻게 뒷받침하는지

**숙련자**: R1 → R2 → R3 (정량 anchor → reasoning → decision) 순서로 일관된 framework 검토

## 🎯 결과 해석 가이드

### "Verdict 분포가 7/3/3이면 어떻게 해석?"

13명 페르소나 중 7명 lean_bullish, 3명 neutral, 3명 lean_bearish:
- **합의 정도**: 53.8% 매수 — medium consensus
- **Style Split 확인**: 어느 카테고리가 lean_bullish인지 봐야. 가치파(Buffett 등) 만장일치 vs 매크로파 split은 매우 다른 신호.
- **Universal Concerns 확인**: 다수가 공유하는 우려가 있는가?
- **본인 투자 철학 적용**: 본인이 가치투자자라면 Buffett·Munger·Graham·Pabrai 4명의 합의에 더 무게.

### "Signal Score +0.5 vs +0.8의 차이?"

- **+0.5**: 한도의 50%만 진입. 신호 강도 medium. 분할 매수 권고.
- **+0.8**: 한도까지 진입. 강한 conviction. Druckenmiller 'bet the ranch' zone 근접.

### "정량과 narrative가 충돌할 때?"

각 페르소나의 'narrative_vs_quant_resolution' 섹션을 확인하세요:
- **Buffett**: 정량(margin of safety) > narrative
- **Cathie Wood**: narrative(disruption) > 단기 정량
- **Druckenmiller**: macro tailwind narrative > micro 정량
- **Damodaran**: story와 numbers의 strict 정합 강제

본인이 어느 페르소나의 framework를 신뢰하는지에 따라 결론이 달라집니다.

## 📚 학습 포인트

1. **같은 사실에 대한 다른 해석**: 13명 페르소나는 같은 정량 데이터·thesis를 받지만 verdict가 갈립니다. 이는 '투자 철학의 차이'가 핵심 — 본인의 framework를 명확히 하는 것이 중요합니다.

2. **데이터 태깅의 중요성**: 모든 숫자에 [actual]/[inference]/[assumption] 태그가 붙습니다. [assumption] 비율이 높은 thesis는 fragility 위험 — 가정 하나 깨지면 verdict 흔들립니다.

3. **Counter analyst의 중요성**: 4-Analyst 중 Counter는 의도적으로 반박을 추구합니다. Counter가 'rebut'한 thesis는 weakest link — 가장 먼저 무너질 가정.

4. **페르소나 가중치 (Phase C 결과 반영)**: 한국 시장에서는 Druckenmiller(1.5×)·Lynch(1.3×)가 Buffett(0.7×) 대비 적중률이 높았습니다. 이는 backtester가 측정한 한국 시장 적합도.

5. **Cash drag trade-off**: Risk Manager의 보수적 sizing(11-16% 한도)이 안전하지만 KOSPI 폭등기에 alpha 깎입니다. Risk-adjusted return vs absolute return 중 본인 우선순위 결정 필요.

## 🔗 관련 산출물

생성된 PDF는 `reports/` 폴더에 있습니다.

## 🛠 사용 시 주의

- 본 보고서는 **교육·연구 목적**이며 투자 자문이 아닙니다.
- 모든 verdict는 분석 시점의 정보에 한정되며, 시장 환경 변화 시 결과가 달라집니다.
- Paper portfolio는 **simulation only** — 실제 거래는 사용자 책임.
- 페르소나는 실존 인물의 투자 철학을 lens로 사용할 뿐, 그 인물을 대변하지 않습니다.

---

생성: {datetime.now().strftime('%Y-%m-%d %H:%M')} · 분석 시스템: thesis-first + 13 personas + 4-Analyst + Risk-adjusted Trade Engine
"""

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"[readme] saved: {args.output} ({len(md):,} chars)")


if __name__ == "__main__":
    main()
