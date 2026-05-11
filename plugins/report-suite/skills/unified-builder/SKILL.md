---
name: unified-builder
description: R1 (정량) + R2 (13명 페르소나) + R3 (의사결정) + Deep Research (산업·재무·시나리오·카탈리스트·리스크·뉴스·DART 공시·ETF holdings·Reverse DCF·Subagent debate)를 단일 통합 PDF로 생성한다. Top N 종목 일괄 처리 가능. 종목명 자동 매핑 (005490.KS → POSCO홀딩스). pdftocairo 후처리로 모든 PDF 뷰어 호환. 사용자가 "통합 보고서", "combined PDF", "top 5 종목 보고서" 등을 언급하면 트리거.
---

# Unified Combined Report Builder ⭐

R1 + R2 + R3 + Deep Research를 **하나의 PDF**로 통합. 분석 시스템의 final output.

## 단일 종목

```bash
python3 plugins/report-suite/skills/unified-builder/scripts/build_combined.py \
  --ticker 005490.KS \
  --meta meta.json --stocks stocks.json \
  --thesis thesis_list.json --eval-dir thesis_eval/ \
  --persona-aggregate persona_panel/005490.KS/aggregate.json \
  --persona-full persona_panel/005490.KS/ \
  --persona-aggregates-all persona_panel/_all_aggregates.json \
  --risk-limits risk_limits.json --decisions decisions.json \
  --portfolio portfolio.json \
  --deep-research deep_research/005490.KS.json \
  --output reports/combined.pdf
```

## Top N 종목 일괄

```bash
python3 plugins/report-suite/skills/unified-builder/scripts/build_multi_stocks.py \
  --pipeline-dir .analysis-log/bloggers/{blogger}/{date}_{slug} \
  --output-dir .../reports/combined \
  --top-n 5 \
  --tickers 005490.KS 006400.KS ALB SQM LIT
```

## 출력 구조 (45-52 페이지/종목)

1. Cover (회사명 · ticker · sector · verdict 분포)
2. Executive Brief (TL;DR)
3. 1년 뉴스·공시 Timeline (DART 자동 fetch — 한국 종목)
4. R1 정량 anchor (Fundamentals + 4-Analyst + Risk)
5. R2 13명 페르소나 패널 + Style Split + Thesis × Persona Matrix
6. Deep Research (산업·재무·Bull/Base/Bear·Catalyst·Risk Matrix)
7. ETF Holdings (ETF 한정 — Top 20 + 섹터 + 국가 breakdown)
8. Reverse DCF (Damodaran 자동)
9. Subagent Debate (해당 시)
10. R3 의사결정 시트
11. 부록 — 학습용 용어 사전

## 의존성
- WeasyPrint (HTML → PDF)
- matplotlib (차트)
- Noto Sans KR 폰트 (`~/.fonts/`)
- pdftocairo (Cairo 후처리 — CJK 폰트 호환성)
- yfinance (가격 fetch — 자동)
- DART API (한국 종목 — 자동 활성, DART_API_KEY 있을 때)
