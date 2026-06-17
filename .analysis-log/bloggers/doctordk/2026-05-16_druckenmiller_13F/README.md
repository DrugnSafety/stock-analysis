# 의교창 — 드러켄밀러 2026 Q1 13F 분석 (2026-05-16)

## 분석 메타
- **원문**: https://blog.naver.com/doctordk/224287187737
- **블로거**: 의교창 (doctordk)
- **발행일**: 2026-05-16 10:45
- **분석일**: 2026-05-16 (Cowork)
- **검증**: validate_format.py **32/32 통과** (100%)

## 한 줄 요약
드러켄밀러의 2026 Q1 13F가 **알파벳 전량 매도 + AI 인프라·병목 자산 매수 + 아르헨티나 정상화 베팅**을 동시에 보여줌. AI 자금이 플랫폼(빅테크)에서 인프라(네트워크·메모리·첨단 공정)로 구조 이동 중. 학습→추론 패러다임 전환으로 메모리·스토리지·CPU 효율이 새로운 병목으로 부상.

## Top 5 종목 + 최종 액션

| # | 티커 | 종목명 | Signal | Action | 핵심 thesis |
|---|------|--------|--------|--------|------------|
| 1 | AVGO | 브로드컴 | +0.49 | 🟢 BUY 355주 (15.1%) | AI 네트워크·ASIC 신규 매수 |
| 2 | TSM  | TSMC    | +0.55 | 🟢 BUY 392주 (15.8%) | 3nm 첨단 공정 독점 병목 |
| 3 | MU   | 마이크론 | +0.35 | 🟢 BUY 151주 (10.9%) | AI 추론 메모리 사이클 |
| 4 | ARM  | ARM 홀딩스 | +0.03 | 🟡 HOLD 210주 (4.4%) | 저전력 CPU 효율 (P/E 68x) |
| 5 | SNDK | 샌디스크 | +0.13 | 🟡 HOLD 31주 (4.4%) | 스토리지 + spin-off catalyst |

**Total deployed**: $418,871 (41.9%) | **Cash**: $581,129 (58.1%)

## 보고서 위치

### Layer 1 — Per-Stock Combined PDF (5종, 각 ~500KB)
- `reports/combined/1_AVGO_브로드컴_combined.pdf`
- `reports/combined/2_TSM_TSMC_combined.pdf`
- `reports/combined/3_MU_마이크론_combined.pdf`
- `reports/combined/4_ARM_ARM_홀딩스_combined.pdf`
- `reports/combined/5_SNDK_샌디스크_combined.pdf`

각 PDF 포함: Cover → Company Intro → Deep Research → R1 Quant Anchor → R2 13명 페르소나 Panel → R3 Decision Sheet → Appendix

### Layer 2 — Multi-format Overview
- `reports/overview/overview.md` (6.7KB)
- `reports/overview/overview.pdf` (63KB)
- `reports/overview/overview.pptx` (39KB, 6슬라이드)

## 분석 파이프라인 데이터 (검증된 산출물)
- `meta.json` — 블로그 메타데이터
- `raw.json` — 원문 본문 (2,987자)
- `thesis_list.json` — 11개 thesis (7 core + 2 secondary + 2 context)
- `thesis_eval/all_aggregate.json` — 11 theses × 4-Analyst(Macro/Industry/Empirical/Counter) = 44 evaluations
- `stocks.json` — yfinance live market data 5종목 (v1.3.0 live)
- `persona_panel/{AVGO,TSM,MU,ARM,SNDK}/` — 각 13명 페르소나 JSON + aggregate.json
- `persona_panel/_all_aggregates.json` — 5종목 × 13명 통합
- `deep_research/{ticker}.json` — 산업·재무·시나리오·카탈리스트·리스크·thesis decomposition
- `risk_limits.json` — vol_multiplier 기반 포지션 한도 (포트폴리오 $1M 기준)
- `decisions.json` — 페르소나 가중 signal score → BUY/HOLD action
- `portfolio.json` — paper portfolio (실거래 X)

## 11개 Thesis 핵심 (4-Analyst 가중 평균 신뢰도 0.60~0.82)

| ID | 핵심 주장 | 가중 stance | 신뢰도 |
|----|----------|------------|--------|
| T01 | GOOGL 전량 매도 = AI 플랫폼 정점 시그널 | support | 0.63 |
| T02 | AI 자금 흐름 플랫폼→인프라 구조 이동 | support | 0.78 |
| T03 | AVGO 신규 매수 = AI 네트워크·ASIC 부상 | support | 0.73 |
| T04 | ARM 신규 = 저전력 CPU 효율 경쟁 | support | 0.66 |
| T05 | 학습→추론 패러다임 = 메모리 병목화 | support | 0.74 |
| T06 | SNDK·MU·STX = 스토리지 구조 베팅 | support | 0.71 |
| **T07** | **TSMC 3nm 독점 = AI 산업 수도관** | **support** | **0.82** |
| T08 | YPF·ARGT 아르헨티나 정상화 | support | 0.68 |
| T09 | YPF 바카 무에르타 비대칭 upside | support | 0.71 |
| T10 | 드러켄밀러 트랙레코드 패턴 | support | 0.60 |
| T11 | 단기 변동성 caution | neutral | 0.51 |

가장 강한 thesis: **T07 (TSMC 첨단 공정 병목)** — 4-Analyst 모두 support, 신뢰도 0.82

## 13명 페르소나 패널 verdict 분포 종합

| 페르소나 | AVGO | TSM | MU | ARM | SNDK |
|---------|------|-----|-----|------|------|
| Warren Buffett | lean_bullish | lean_bullish | neutral | lean_bearish | neutral |
| Charlie Munger | lean_bullish | lean_bullish | neutral | lean_bearish | lean_bearish |
| Ben Graham | neutral | lean_bullish | **lean_bullish** | lean_bearish | neutral |
| Mohnish Pabrai | lean_bullish | lean_bullish | **lean_bullish** | neutral | lean_bullish |
| Michael Burry | neutral | neutral | **lean_bullish** | lean_bearish | **lean_bullish** |
| Peter Lynch | lean_bullish | lean_bullish | neutral | lean_bullish | neutral |
| Cathie Wood | **strong_bullish** | lean_bullish | lean_bullish | lean_bullish | lean_bullish |
| Phil Fisher | lean_bullish | lean_bullish | neutral | lean_bullish | neutral |
| Jhunjhunwala | lean_bullish | **strong_bullish** | lean_bullish | lean_bullish | neutral |
| **Druckenmiller** | **strong_bullish** | **strong_bullish** | **strong_bullish** | lean_bullish | lean_bullish |
| Nassim Taleb | neutral | neutral | lean_bearish | lean_bearish | lean_bearish |
| Bill Ackman | lean_bullish | lean_bullish | neutral | neutral | neutral |
| Aswath Damodaran | neutral | lean_bullish | lean_bullish | lean_bearish | neutral |

**페르소나별 패턴**:
- **만장일치 bull (Druckenmiller)** — 본인 picks
- **Quality bull (TSM·AVGO)** — Buffett, Munger, Ackman, Fisher 모두 lean_bullish
- **Deep value bull (MU·SNDK)** — Burry, Pabrai, Graham 모두 lean_bullish
- **ARM 회피 다수** — Buffett, Munger, Graham, Damodaran 모두 lean_bearish (P/E 68x 부담)

## Key Risks (Top 5)
1. **AI capex 사이클 정점** (AVGO·MU 영향) — hyperscaler capex 2027 -10% scenario 시 매출 직접 영향
2. **Taiwan tail event** (TSM) — geopolitical conflict 시 -50%+ tail risk
3. **Memory cycle peak** (MU) — 2027 supply glut 재발 시 매출 -40%
4. **ARM P/E 68x 압박** — growth deceleration 시 멀티플 compression -30%+
5. **SNDK post-spin volatility** — 1Y vol 95%, price discovery 미완료

## 검증 결과
```
[1/5] Required top-level files     8/8 ✓
[2/5] Thesis list                  2/2 ✓ (11 theses, 7 core)
[3/5] Stocks list                  3/3 ✓ (yfinance live 5/5)
[4/5] Persona panels (13명/티커)   10/10 ✓
[5/5] Combined PDF reports         3/3 ✓ (5 PDFs)
[bonus] 4-Analyst schema           3/3 ✓
[bonus] Layer 2 overview           3/3 ✓
─────────────────────────────────────
TOTAL: 32/32 (100%) ✓ canonical format 일치
```

---
*Generated by naver-blog-investment plugin pipeline · 2026-05-16*
