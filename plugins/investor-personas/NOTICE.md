# NOTICE — Attribution and Modifications

## 출처

이 plugin의 13개 페르소나 SKILL.md는 다음 저장소들의 작업을 한국어로 번역하고 한국 시장 맥락에 맞게 각색한 것이다:

### 1차 출처

- **vibe-investing** by monarchjuno
- 저장소: https://github.com/monarchjuno/vibe-investing
- 라이선스: MIT
- 라이선스 사본: 본 디렉토리 `LICENSE-MIT-vibe-investing` 참조

### 2차 출처 (vibe-investing가 명시한 reference)

- **virattt/ai-hedge-fund** by virattt
- 저장소: https://github.com/virattt/ai-hedge-fund
- vibe-investing의 README가 다음과 같이 명시:
  > `virattt/ai-hedge-fund`: reference source for the investor persona skill adaptation work under `skills/investor-personas/`

## 수정 내역 (Modifications)

본 plugin이 vibe-investing 원본에서 변경한 내용:

1. **언어**: 영문 → 한국어 번역. 영문 키워드 병기 (예: "워런 버핏 (Warren Buffett)").
2. **시장 맥락**: 한국 KOSPI/KOSDAQ 종목에도 적용 가능하도록 재벌 구조·KRX 시장 시간·환율(KRW/USD) 등 한국 시장 특수성을 보강.
3. **데이터 태깅**: 원본의 `[actual]/[inference]/[assumption]` 태깅 시스템을 그대로 따름. 추가 태그 `[derived]`, `[unavailable]`도 동일.
4. **출력 스키마**: vibe-investing은 자유 텍스트 출력이지만, 본 plugin은 JSON 스키마를 강제하여 cross-persona aggregation 가능하게 함.
5. **다중 모델 통합**: vibe-investing은 LLM-agnostic 설계, 본 plugin은 OpenAI/Gemini/Claude 어느 것으로도 호출 가능한 wrapper 추가.

## 인물 이름·초상권

각 페르소나는 실존 투자자의 이름을 사용하나, 본 plugin은 "X의 투자 철학을 lens로 사용"하는 중립적 분석 도구일 뿐, 해당 인물의 추천·승인·대변이 아니다. 사용자가 결과를 기반으로 "X가 추천했다" 등으로 잘못 표현하는 것은 금지된다.

## 한국어 페르소나 추가 가능성

vibe-investing 원본은 13명 모두 글로벌 인물이다. 향후 본 plugin이 한국 투자자 페르소나(동원, 박영옥, 김경한 등)를 추가할 경우:
- 별도 디렉토리(`personas-kr/`)로 분리
- 출처 표시 명확히
- 각 한국 투자자의 공개된 책·인터뷰·강연 등 공개 자료에 기반

## 라이선스 의무 (요약)

vibe-investing의 MIT 라이선스는 다음 두 가지만 의무로 함:
1. **저작권 표시 유지** ✅ (이 NOTICE.md + LICENSE-MIT-vibe-investing 파일로 충족)
2. **MIT 라이선스 사본 동봉** ✅ (LICENSE-MIT-vibe-investing 파일로 충족)

상업적 사용·수정·재배포 모두 자유롭게 허용된다.

---

본 NOTICE.md 자체도 변경 가능. 단 위의 출처 표시는 유지할 것.
