# 보고서 형식 표준 (Report Format Standard)

> **목적**: 새 세션에서도 동일한 형식의 보고서가 생성되도록 표준을 명시. 모든 분석은 본 문서의 형식을 따라야 함.
>
> **버전**: v0.3.0 (2026-05-28) — Sprint 1.2 + 누적 모든 sprint 반영
> **이전**: v0.1.0 (2026-05-01 ECM canonical) → v0.2.0 (Phase 2 + Sprint 1.5/2/C 누적) → v0.3.0 (Sprint 1.2 + 6/6 macro)

---

## 0. v0.3.0 변경 요약 (한 눈에 보기)

| 영역 | 이전 (v0.1.0) | 현재 (v0.3.0) |
|---|---|---|
| 페르소나 패널 | 13명 | **17명** (Dalio·Soros·Simons·Asness 추가) |
| Macro 통합 | 없음 | **6개 기관 live** (FRED·IMF·WB·OECD·ECB·BIS) |
| Quant Anchor | 없음 | **신규 plugin** (DCF·Reverse DCF·VaR·Sharpe·Portfolio) |
| PDF 섹션 수 | 9개 | **13개** (Macro Anchor·Quant Anchor·Sector Impact·Special-Lens 추가) |
| Investment Checklist | heuristic only | **실 데이터 기반 검증** (160+ criterion 매핑) + 학습 가이드 column |
| Cost/분석 (LLM) | ~$2.04 | **~$0.17** (tier_mid 자동 라우팅, −91.5%) |
| Mock 데이터 처리 | silent | **명시적 경고 배너** + 실행 가이드 표시 |
| Emoji 호환성 | 일부 깨짐 (⊠) | **EMOJI_MAP 65+ 항목** 텍스트 prefix 대체 |
| 한글 폰트 | 깨짐 가능 | Noto Sans KR + Apple SD Gothic Neo + emoji_replace |

---

## 1. 표준 디렉토리 구조 (v0.3.0)

```
.analysis-log/bloggers/{blogger}/{date}_{slug}/
├── meta.json                      # 필수: blog_url, title, date, blogger
├── thesis_list.json               # 필수: 6-12 theses with importance/timeframe
├── stocks.json                    # 필수: top 5 stocks with market_data
│
├── thesis_eval/
│   ├── all_aggregate.json         # 필수: 4-Analyst (Macro·Industry·Empirical·Counter)
│   └── all_aggregate_mock_backup.json   # mock 데이터 백업 (실 평가 전)
│
├── persona_panel/
│   ├── _all_aggregates.json       # 필수: 모든 ticker의 aggregate
│   └── {ticker}/
│       ├── aggregate.json         # 필수: 17명 verdict + style_split
│       ├── panel_summary.json     # 필수: cost·timing 메타
│       └── {persona_id}.json      # 필수: 17개 persona 개별 평가
│
├── deep_research/
│   └── {ticker}.json              # 필수: industry/financials/scenarios/catalysts/risks
│                                  # ★ income_statement 형식도 OK — auto_convert_deep_research_financials가 pl_5y 변환
│
├── ★ macro_snapshot.json          # NEW v0.2.0+ — FRED + IMF + WB + OECD + ECB + BIS (6개 기관)
├── ★ quant_anchor_{TICKER}.json   # NEW v0.2.0+ — DCF + Reverse DCF + Risk + Portfolio Optimizer
│
├── risk_limits.json               # 필수: vol_multiplier 기반 position 한도
├── decisions.json                 # 필수: signal_score → BUY/HOLD/SELL
├── portfolio.json                 # 필수: paper portfolio state
│
└── reports/
    ├── combined/                  # Layer 1 — per-stock deep PDFs
    │   └── {idx}_{ticker}_{name}_combined.pdf
    └── overview/                  # Layer 2 — multi-format summary
        ├── overview.md
        ├── overview.pdf
        └── overview.pptx
```

---

## 2. PDF 섹션 표준 흐름 (v0.3.0, 13 sections)

```
[1] Cover
[2] [브리핑] 회사 소개 (Company Profile)
    ├ 사업 개요 (요약) — yfinance longBusinessSummary 자동 한글 번역 (LLM)
    ├ 회사 메타데이터 (yfinance 자동 수집)
    ├ 사업 내용 원문 (longBusinessSummary · 영문)
    ├ 매출 구조 (Segment 비중)
    ├ 글로벌 위치
    ├ 주요 고객 / 경쟁사
    └ 주요 지표 (Valuation Snapshot)

[3] ★ [글로벌] Macro Anchor — 거시·정책 환경 ★ (NEW v0.2.0)
    ├ [차트] Regime Summary (rule-based narrative)
    ├ [美] US Macro — FRED 5종 핵심 지표
    ├ [글로벌] Global Outlook — IMF WEO 전망
    ├ [歐] Eurozone Macro — ECB SDW (MRO·HICP·M3)         ★ NEW v0.3.0
    ├ [글로벌] Development Indicators — World Bank          ★ NEW v0.3.0
    ├ [차트] OECD Leading Indicators — 경기 선행 지수       ★ NEW v0.3.0
    ├ [글로벌] BIS Credit Cycle — Dalio Debt Cycle Anchor   ★ NEW v0.3.0
    └ [기업·산업] Sector Impact — {company} → {sector}      ★ NEW v0.2.0
        (활성 macro factor × sector 영향 매트릭스 + verdict)

[4] [심층] Deep Research
    ├ 산업 맥락 (Industry Context)
    └ 재무 심층 분석 (Financial Deep Dive)
        ├ 5년 손익 추이 (currency·scale auto-detect)
        ├ [상승] 추세 분석 (Analytic Agent)
        ├ [주목] Watch Points (향후 1~2년)                    ★ NEW v0.2.0
        ├ [학습] 추세 지표 해석 가이드 (학습용)               ★ NEW v0.2.0
        ├ 대차대조표 스냅샷
        ├ 현금흐름 요약 (5년 평균)
        └ 피어 비교 (Peer Comparison)

[5] [재무] 재무제표 분석 — US GAAP 기준 (5Y annual + 5Q quarterly + variance)

[6] ★ [측정] Quantitative Anchor — {TICKER} ★ (NEW v0.2.0)
    ├ [종합] Consolidated Signals (valuation·risk·verdict hints)
    ├ [가치] DCF Valuation
    │   ├ [학습] DCF 부연설명 (이 지표는·해석법·본 종목 적용)
    │   ├ Intrinsic Value · Current Price · Upside (3-card)
    │   └ DCF 세부 표 (FCF projection·terminal value·sensitivity)
    ├ [역산] Reverse DCF — Market-Implied Growth
    │   ├ [학습] Reverse DCF 부연설명
    │   └ implied growth vs historical CAGR vs analyst consensus
    ├ [리스크] Risk Metrics (60-day rolling, 1Y window)
    │   ├ [학습] Sharpe/Sortino/VaR/CVaR/MaxDD/Beta 6종 해설
    │   └ 6 metric cards (annual return, vol, Sharpe, Sortino, MaxDD, β)
    └ [종합] Portfolio Optimization (efficient frontier — 있을 때)

[7] [일정] News Timeline — 1년 뉴스·공시 (NewsAPI + Finnhub)

[8] [브리핑] Executive Brief + 전체 Thesis List

[8.5] [주의] Thesis × 4-Analyst 평가 데이터 부재 (mock 감지 시 자동 표시)  ★ NEW v0.3.0

[9] R1 Quant Anchor — 정량 데이터 (4-Analyst stance · confidence heatmap)
    └ 데이터 검증 시 mock 자동 감지 → 실 평가 안내

[10] R2 Persona Panel (17명 대가 패널)
    ├ Verdict 분포 + Style split
    ├ Thesis × Persona Matrix
    ├ 페르소나별 상세 (각 대가 철학 + 종목 분석)
    │   ├ 5단계 분석 결과
    │   ├ 우려 / 기회 / Narrative-vs-Quant
    │   ├ ★ Special-Lens panel (Dalio·Soros·Simons·Asness 전용)      ★ NEW v0.2.0
    │   └ ★ Investment Checklist (5-column: 항목·결과·설명·학습 가이드) ★ NEW v0.2.0
    │       — 실 데이터 기반 검증 (160+ criterion 매핑)
    │       — 학습 가이드 column에 의미·해석법·sector 평균 등 풍부한 설명

[11] R3 Executive Summary — 의사결정 시트

[12] Specialist Agents (Tier 2 — Research Manager·Sentiment·Earnings·Model)
[13] (선택) ETF Holdings · Subagent Debate · Reverse DCF Standalone

[14] [학습] Appendix — 용어 사전
```

---

## 3. 페르소나 17명 표준 (v0.3.0)

```
Original 13 (v0.1.0):
  warren-buffett, charlie-munger, peter-lynch, cathie-wood,
  michael-burry, nassim-taleb, ben-graham, bill-ackman,
  mohnish-pabrai, phil-fisher, rakesh-jhunjhunwala,
  stanley-druckenmiller, aswath-damodaran

Phase 2 추가 4명 (v0.2.0):
  ray-dalio         — Debt Cycle + All Weather + 4-Quadrant
  george-soros      — Reflexivity 8-stage Boom-Bust
  jim-simons        — Pure Quant / Statistical Arbitrage (narrative-blind)
  cliff-asness      — Fama-French 6-Factor
```

**가중치 baseline** (`_weights.json`):
```
stanley-druckenmiller: 1.5    michael-burry: 1.2    ray-dalio: 1.2
peter-lynch: 1.3              warren-buffett: 0.7   cathie-wood: 0.9
george-soros: 1.0             jim-simons: 0.9       cliff-asness: 0.9
기타 default: 1.0
```

---

## 4. 6개 거시 데이터 기관 (v0.3.0 — 6/6 live)

| 기관 | API | 키 필요 | 핵심 지표 |
|---|---|---|---|
| **FRED** | api.stlouisfed.org | ✓ (무료) | 美 UNRATE, CPIAUCSL, FEDFUNDS, T10Y2Y, DGS10 |
| **IMF** | imf.org/datamapper/api | ✗ | NGDP_RPCH, BCA_NGDPD, PCPIPCH, GGXWDG_NGDP |
| **WB** | api.worldbank.org/v2 | ✗ | GDP, GDP/capita, 인구, 도시화율, 수출/GDP |
| **OECD** | stats.oecd.org/sdmx-json/data (legacy) | ✗ | CLI, BCI, CCI (per-country fetch) |
| **ECB** | data-api.ecb.europa.eu/service/data | ✗ | MRO rate, HICP, M3 (CSV format) |
| **BIS** | stats.bis.org/api/v1/data | ✗ | Total credit/GDP, REER |

**Auto-generated regime flags**:
- `MONETARY_TIGHTENING` — Fed funds restrictive
- `INFLATION_ABOVE_TARGET` — CPI YoY > 3%
- `RECESSION_LEADING_INDICATOR` — 10Y-2Y 역전
- `KR_UNDERPERFORM_US` — IMF GDP 전망 격차 >0.5%p
- `US_EU_POLICY_DIVERGENCE` — Fed funds vs ECB MRO 차이 >2.0%p  ★ NEW v0.3.0
- `EU_INFLATION_ABOVE_TARGET` — 유로존 HICP >3%                  ★ NEW v0.3.0

---

## 5. Quant Anchor plugin (v0.2.0+)

```
plugins/quant-anchor/scripts/
├── dcf_engine.py            — 5Y FCF + Gordon Growth (cyclic normalization fix)
├── reverse_dcf.py           — Market-implied growth (binary search)
├── risk_metrics.py          — VaR/CVaR/Sharpe/Sortino/MaxDD/Beta
├── portfolio_optimizer.py   — pyportfolioopt efficient frontier
└── quant_anchor_builder.py  — 통합 orchestrator
```

**Build hook (자동)**:
```python
# build_combined.py
if not (pipeline_dir / f"quant_anchor_{ticker}.json").exists():
    from quant_anchor_builder import ensure_quant_anchor
    qa = ensure_quant_anchor(pipeline_dir, ticker, stocks=stocks)
```

---

## 6. Investment Checklist 5-column 구조 (v0.2.0+ Fix-C)

```
| # | 판단 항목 (Criterion) 22% | 결과 6% | 설명 (검증결과) 30% | 학습 가이드 (의미·해석법) 39% |
|---|---------------------------|---------|---------------------|------------------------------|
| 1 | Durable economic moat     | [?]     | 정성 평가 — ...     | Moat = 경쟁사가 진입·복제   |
|   |                           |         |                     | 어려운 구조적 우위...        |
| 3 | Consistent ROE 15%+       | [X]     | 미달: ROE = 8.40%   | ROE = 순이익/자본. 자본 1단 |
|   |                           |         | (기준: ≥ 15%)        | 위당 효율적 이익...          |
```

**Criterion 매핑 데이터 소스 (CRITERION_DATA_RULES)**:
- `market_data` (forward_pe, pb, roe, peg, beta, dividend_yield)
- `bs_snapshot` (de_ratio_pct, cash_to_assets, net_cash)
- `cf_summary` (fcf_5y_avg, capex_intensity_pct, fcf_conversion_pct)
- `pl_5y` (revenue_cagr_pct, op_margin_pct, fcf_margin_pct derived)
- `quant_anchor.dcf.upside_pct`, `quant_anchor.risk_metrics.{sharpe_ratio·max_drawdown_pct}`

---

## 7. Cost Optimization 표준 (v0.2.0+)

```
persona-evaluator default tier: tier_mid (gpt-4o + gemini-2.5-flash)
  → 분석당 비용 ~$0.17 (premium 대비 −91.5%)

Override:
  --tier {cheap|mid|premium}      (per-call)
  ROUTER_OVERRIDE_TIER=cheap      (전역)
  PERSONA_EVAL_PREMIUM=1          (back-compat — 기존 gpt-5.5 강제)
```

Macro/Quant plugins: **LLM 0 호출** (rule-based + 공식 API).
Company intro 한글 번역: **gpt-4o-mini, 7일 캐시, $0.0005/번역 (1회)**.

---

## 8. PDF 빌드 표준 명령

### Layer 1 — per-stock deep PDF (필수)
```bash
DISABLE_SYNC=1 python3 plugins/report-suite/skills/unified-builder/scripts/build_multi_stocks.py \
    --pipeline-dir .analysis-log/.../{slug} \
    --output-dir .../reports/combined \
    --top-n 5
```

### Layer 2 — multi-format overview (권장)
```bash
python3 plugins/report-suite/skills/unified-builder/scripts/build_overview.py \
    --pipeline-dir .analysis-log/.../{slug} \
    --output-dir .../reports/overview \
    --formats md pdf pptx
```

### 검증 (의무)
```bash
python3 plugins/report-suite/skills/unified-builder/scripts/validate_format.py \
    .analysis-log/.../{slug}
```

---

## 9. 17-Panel 실행 표준

```bash
# 자동 tier_mid (cost ~$0.17 for 17 personas × LNG)
python3 plugins/investor-personas/skills/persona-panel/scripts/run_panel.py \
    {TICKER} \
    --market {pdir}/stocks.json \
    --output-dir {pdir}/persona_panel/{TICKER} \
    --max-workers 2

# 신규 4명만 추가 (Phase 2)
python3 plugins/.../run_panel.py {TICKER} \
    --include ray-dalio,george-soros,jim-simons,cliff-asness \
    --max-workers 2
```

**Mock 데이터 자동 감지**: thesis_eval rationale에 "(mock)" 또는 "user_provided" 패턴 50%+이면 PDF에 **경고 배너 자동 표시** + 실 평가 실행 가이드.

---

## 10. Thesis 4-Analyst 실제 평가 (선택, ~$0.03)

```bash
python3 plugins/multi-model-arena/skills/thesis-evaluator/scripts/evaluate_theses.py \
    {pipeline_dir}/thesis_list.json \
    --output-dir {pipeline_dir}/thesis_eval \
    --provider openai \
    --include-supporting
```

실행 후 PDF 재빌드 시:
- mock 경고 배너 자동 사라짐
- 각 thesis의 4-Analyst rationale이 실제 LLM 평가로 채워짐
- Aggregate stance + confidence 정확

---

## 11. Emoji 호환성 표준 (Fix-B v0.2.0+)

WeasyPrint + Noto Sans KR에서 emoji 깨짐 (⊠ box). **EMOJI_MAP 65+ 항목**으로 자동 치환:

```
📋 → [브리핑]    📊 → [차트]     📈 → [상승]      📉 → [하락]
📐 → [측정]     📅 → [일정]     📑 → [공시]      📚 → [학습]
🔬 → [심층]     🌐 → [글로벌]    🌏 → [글로벌]    🏛️ → [정책]
🥊 → [Debate]   💰 → [재무]     💵 → [가치]      🔁 → [역산]
🇺🇸 → 美       🇰🇷 → 韓       🇨🇳 → 中        🇯🇵 → 日
🟢 → [녹]       🟡 → [노]       🔴 → [적]       ✓ → [O]   ✗ → [X]
```

`build_combined.py` line 975: `body = remove_emoji(body)` — 자동 최종 처리.

---

## 12. 형식 일관성 자동 검증

```bash
python3 plugins/report-suite/skills/unified-builder/scripts/validate_format.py \
    .analysis-log/bloggers/{blogger}/{slug}
```

- 필수 파일 존재 확인 (meta·theses·stocks·persona_panel·deep_research·decisions)
- thesis 개수 ≥ 5, persona 17명 풀 평가, deep_research 모든 ticker
- ★ NEW v0.3.0: macro_snapshot.json + quant_anchor_*.json 존재 확인
- 누락 시 명확한 에러 메시지

---

## 13. ❌ Anti-Pattern (절대 금지)

- ❌ `analyses/` 디렉토리 사용 (잘못된 패턴 — 2026-04-23 헨리허브 LNG 사례)
- ❌ 단일 `report.pdf` 출력 (per-stock PDF가 표준)
- ❌ 7-Role 분석으로 대체 (17명 페르소나 + 4-Analyst가 표준)
- ❌ Roman numeral 섹션 (Korean 헤더 통일)
- ❌ One-off scripts 작성 (plugin 호출만 사용)
- ❌ Layer 1 누락 또는 단축 형태 PDF
- ❌ 페르소나 panel 13명만 (17명 풀 패널 필수, v0.2.0+)
- ❌ **stocks.json의 market_data를 LLM이 placeholder로 채움** — 반드시 yfinance live fetch
- ❌ Emoji 직접 사용 — `emoji_replace.EMOJI_MAP` 추가 없이 새 emoji 도입 금지

---

## 14. Few-shot 참조 샘플

**Canonical (이전)**:
- 의교창 lithium: `.analysis-log/bloggers/doctordk/2026-04-29_lithium/`
- 메르 ECM: `.analysis-log/bloggers/ranto28/2026-04-21_ECM_skinbooster/`

**v0.3.0 기준 (Sprint 1.2 모든 기능 반영)**:
- LNG: `.analysis-log/standalone/2026-05-11_LNG_Cheniere_Energy/`
  - macro_snapshot.json (6/6 institutions live)
  - quant_anchor_LNG.json (DCF $345.71, +49.7% upside)
  - persona_panel/LNG/ (17명 personas, special-lens 채워짐)

---

## 15. 새 세션 시작 시 — Best Practice

```
사용자 → "/analyze-blog <URL>" 또는 "{TICKER} 분석"
   ↓
Claude → CLAUDE.md + 본 표준 인지
   ↓
Claude → 의교창 lithium 또는 LNG 샘플 디렉토리 참조 (few-shot)
   ↓
Claude → 동일 디렉토리 구조 + v0.3.0 PDF 양식
   ↓
Output: Layer 1 (per-stock PDFs with 13 sections) + Layer 2 (PPT/MD overview)
```

---

## 16. Sprint 누적 변경 history

| 버전 | 일자 | 주요 변경 |
|---|---|---|
| v0.1.0 | 2026-05-01 | 13 페르소나 + 4-Analyst + Deep Research baseline (ECM canonical) |
| v0.2.0 | 2026-05-28 | macro plugin + quant-anchor plugin + 17 페르소나 + cost opt + 8개 결함 fix |
| **v0.3.0** | **2026-05-29** | **6/6 macro institutions live + Investment Checklist 5-col + emoji 65+ map + mock 경고 + thesis mock detect** |

---

## 17. 결론

- **v0.3.0 시스템 = 표준** (deep + reusable plugin + 6/6 macro)
- **17명 페르소나 + 6개 macro 기관 + Quant Anchor + 학습 가이드 column** = 학습 친화적 deep analysis
- **Cost ~$0.17/분석** (premium 대비 −91.5%)
- **Few-shot 샘플(LNG) + SKILL.md 강화 + 자동 검증**으로 일관성 보장

본 문서는 모든 새 분석의 baseline이며, `CLAUDE.md`에서 자동 참조됩니다.
