# NOTICE — Attribution

본 plugin의 risk_manager 및 portfolio_manager 패턴은 다음 저장소에서 차용:

- **virattt/ai-hedge-fund** (MIT)
- 저장소: https://github.com/virattt/ai-hedge-fund
- 라이선스 사본: `LICENSE-MIT-ai-hedge-fund`

## 차용한 핵심 컴포넌트 (verbatim 패턴)

### risk_manager.py
- `calculate_volatility_metrics()` — 60일 rolling stdev → annualized (× √252)
- `calculate_volatility_adjusted_limit()` — 변동성 구간별 multiplier (1.25 / 1.0 / 0.75 / 0.50)
- `calculate_correlation_multiplier()` — 활성 포지션과의 평균 상관계수에 따른 multiplier

### portfolio_manager.py
- `compute_allowed_actions()` — cash·margin 조건 하에서 가능한 action·quantity 계산
- `PortfolioDecision` 스키마 (action / quantity / confidence / reasoning)

## 본 plugin이 추가한 사항

1. **메르 시스템 통합**: ledger.jsonl(thesis-first / persona-panel / multi-model arena) verdict들을 입력으로 받음
2. **페르소나별 가중치**: Phase C 검증으로 발견한 한국 시장 적합도 (Druckenmiller × 1.5, Buffett × 0.7) 옵션 적용 가능
3. **한국 시장 특수성**:
   - KRW/USD 환율 변동성 추가 옵션
   - KRX 거래일 calendar 처리
   - 한국 종목 lot size 무시 (1주 단위)
4. **Paper portfolio 추적**: ai-hedge-fund의 backtester와 별개로 시점별 일일 NAV·drawdown·Sharpe 추적
5. **결정론적 aggregation 우선**: ai-hedge-fund는 LLM 호출 필수, 본 plugin은 deterministic aggregation을 기본으로 (LLM은 옵션) → 비용·재현성 우수

## 라이선스 의무 (요약)

ai-hedge-fund의 MIT 라이선스는 두 가지 의무만:
1. **저작권 표시 유지** ✅
2. **MIT 라이선스 사본 동봉** ✅

상업적 사용·수정·재배포 자유.

## 안전장치

- **실제 거래 자동화 금지**: 본 plugin은 paper portfolio simulation only
- 실제 매수·매도는 사용자가 증권사 HTS/MTS에서 수동 실행
- API 키로 실제 거래 발주는 본 plugin에서 절대 시도하지 않음 (시스템 정책 준수)
