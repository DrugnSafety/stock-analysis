# NOTICE — Attribution

## 출처

본 plugin의 backtest 패턴은 다음 저장소에서 영감을 받음:

### virattt/ai-hedge-fund

- 저장소: https://github.com/virattt/ai-hedge-fund
- 라이선스: MIT
- 라이선스 사본: `LICENSE-MIT-ai-hedge-fund`

본 plugin은 ai-hedge-fund의 다음 컴포넌트 설계를 참고:
- `src/backtester.py` — 진입·청산 시뮬레이션 패턴
- `src/backtesting/engine.py` — BacktestEngine 클래스 구조
- `src/backtesting/types.py` — PerformanceMetrics 스키마

## 수정·확장 사항

본 plugin이 ai-hedge-fund 원본에서 변경·추가한 내용:

1. **단일 모델 → multi-source ledger**: ai-hedge-fund는 단일 모델의 verdict를 backtest. 본 plugin은 thesis-first / 13 personas / multi-model arena 등 **여러 source의 verdict를 통합 ledger로** 처리.
2. **페르소나별 hit rate 매트릭스**: ai-hedge-fund 원본에 없음. 본 plugin은 13명 페르소나별 hit rate를 별도 추적하여 "한국 시장에서 어느 페르소나가 alpha 있는가" 측정.
3. **Confidence calibration**: ai-hedge-fund의 BacktestEngine은 confidence를 무시. 본 plugin은 confidence 구간별 실제 적중률을 비교하여 overconfidence 측정.
4. **한국 시장 벤치마크**: ai-hedge-fund는 SPY 기준. 본 plugin은 KOSPI(`^KS11`)·KOSDAQ(`^KQ11`)·SPY 모두 지원.
5. **메르 블로그 통합**: ai-hedge-fund는 generic. 본 plugin은 메르 블로그 글 시점·종목 mapping을 우선 지원.

## 라이선스 의무 (요약)

ai-hedge-fund의 MIT 라이선스는 다음 두 가지만 의무로 함:
1. **저작권 표시 유지** ✅ (이 NOTICE.md + LICENSE-MIT-ai-hedge-fund 파일로 충족)
2. **MIT 라이선스 사본 동봉** ✅

상업적 사용·수정·재배포 자유.
