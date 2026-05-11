---
name: analyze-stock
description: 사용자 지정 종목 (한국·미국 모두)에 대한 standalone 분석 보고서 생성. 블로그 글 없이 ticker만으로 13명 페르소나 + Deep Research + 통합 PDF.
argument-hint: <ticker> [--name "회사명"]
---

분석 대상 종목: $ARGUMENTS

다음 7단계를 진행해주세요:

1. **종목 정보 확인**: ticker_resolver에서 회사명·sector 매핑 (없으면 yfinance에서 자동 fetch + curated map 추가 권고)
2. **Standalone Thesis 작성**: 산업·재무·정책 기반으로 6-8개 thesis 정의 (블로거 perspective 없이 industry expert 관점)
3. **4-Analyst 평가**: 각 thesis에 대해 Macro/Industry/Empirical/Counter 평가 (확장 rationale 600+자)
4. **Market Data**: yfinance fetch (가격·PE·베타·변동성·수익률). 한국 종목이면 DART도 자동 fetch.
5. **13명 페르소나 패널 synthesis**: 종목 특성 기반 페르소나 verdict + key concerns/opportunities
6. **Deep Research**: 산업 맥락 + 5년 P&L + Bull/Base/Bear 시나리오 + Catalyst Timeline + Risk Matrix + 1년 뉴스
7. **통합 PDF 생성**: build_combined.py로 단일 종목 combined PDF

결과는 `.analysis-log/standalone/{date}_{ticker}_{name}/reports/`에 저장.

**예시**:
- `/analyze-stock BTU` → Peabody Energy (미국 석탄)
- `/analyze-stock 005490.KS` → POSCO홀딩스
- `/analyze-stock NVDA` → NVIDIA

**주의 사항**:
- US 종목: yfinance만 사용 (SEC EDGAR 통합은 Phase 2-2)
- 한국 종목: yfinance + DART 자동 (DART_API_KEY 활성 시)
- Standalone 분석은 industry expert 관점 — 블로거 견해 미포함
