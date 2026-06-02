## v0.9.1 (2026-06-02) — Sprint F-3: Checklist qualitative LLM 평가

evidence·heuristic 모두 실패하는 경우 단순 "[?]" 표시 대신, gpt-4o-mini가 종목 데이터 + 페르소나 철학 종합하여 정성 평가 작성.

### `guru_checklist.py` 신규 함수

- `_llm_qualitative_assessment()`: criterion + persona_id + company_data + ticker 입력 → `{"status": "[O]/[X]/[?]", "note": "<html bullet 음슴체>"}` 출력. gpt-4o-mini · temperature 0.2 · JSON response.
- `_summarize_company_data()`: market_data + pl_5y + bs_snapshot + cf_summary + quant_anchor → LLM이 읽기 좋은 짧은 요약. D/E·5Y CAGR 등 derived metric 자동 계산.
- `_summarize_persona_verdict()`: 페르소나 전체 verdict + 핵심 우려/기회 짧은 context.
- `PERSONA_PHILOSOPHY` dict: 17명 페르소나별 핵심 철학 brief (Buffett=Quality moat, Lynch=GARP, Asness=Multi-factor 등).

### 호출 순서

1. 정량 metric 매핑 가능 → 직접 계산
2. Qualitative item: 페르소나 본문 evidence 추출 (E-9·F-1) → 성공 시 사용
3. **신규 F-3**: LLM 정성 평가 → 성공 시 사용
4. 최종 fallback: heuristic verdict-based 추정

### Cache & 비용

- Cache: `.cache/checklist_llm/{ticker}.json` — `{persona_id}::{criterion}` 키
- 1 ticker × 17 personas × ~3 qualitative items/persona ≈ 50건/run → 약 $0.005
- 재실행 시 cache hit → 비용 0
- 비활성화: `DISABLE_LLM_CHECKLIST=1`

### 검증 (Samsung 005930.KS)

- Jhunjhunwala × "India/EM growth story" → `[X]` "한국 기업으로 인도 성장 스토리와 직접적인 연관이 없음 / 라케시 준준왈라의 투자 철학에 부합하지 않음"
- Cliff Asness × "Value factor z-score (HML 노출)" → `[O]` "Forward PE가 5.94로 낮은 수준임 / EV/EBITDA가 14.11로 상대적으로 높은 평가 / 모멘텀 긍정적임"
- 음슴체 어조 100% 적용 ("없음", "부족함", "낮은 수준임", "긍정적임" 등)

---

# CHANGELOG

## v0.9.0 (2026-06-02) — Sprint E + F: PDF 보고서 결함 일괄 패치 (12건)

대용량 종목 분석(삼성전자 005930.KS 90페이지) 검증 과정에서 발견된 데이터 누락·렌더링 오류·UX 결함 12건을 패치.

### Sprint E (10건) — 데이터 누락 + 포맷팅

#### P0 데이터 누락 (4건)
- **E-1** `aggregate_panel.py`: persona 17명 individual JSON → `aggregate.json` + `_all_aggregates.json` aggregator. 기존 `run_panel.py`에 누락된 aggregator step 보완. Phase 2 4명(Dalio·Soros·Simons·Asness) PERSONA_CATEGORY + PERSONA_NAMES 추가.
- **E-2** `deep_research.py` + `build_combined.py`: Deep Research thesis_decomposition 섹션에 `thesis_eval/all_aggregate.json`의 4-Analyst evaluations overlay. claim_id + claim_text fuzzy 매칭. stance 집계 → confirmed/pending/invalidated 자동 도출. "1지지·2중립·1반박 (of 4)" 형태 표시.
- **E-3** `thesis_eval_normalizer.py`: `_normalize_v2_to_canonical()`이 stance/confidence/rationale 3개 필드만 보존했던 버그 수정 — `supporting_data`, `counter_evidence`, `key_assumption`, `fragility_score` 등 풍부한 metadata 모두 보존. `build_r1.py` data tagging count 영어 source keyword 33종 확장 (Fed·SEC·DART·yfinance·earnings call 등).
- **E-9** `guru_checklist.py`: Investment Checklist `_extract_persona_evidence()` 신설 — heuristic fallback 진입 전 페르소나의 `quant_anchor_validation` + `thesis_lens_applications` + `stage_results` + `key_opportunities`/`key_concerns` 4개 소스에서 criterion 관련 evidence를 keyword fuzzy match로 추출. "heuristic 추정 충족 (criterion 매핑 미수행)" → 페르소나 stage_results의 구체적 평가 ("최근 1년 475.03% [actual]라는 강력한 모멘텀") 직접 인용.

#### P1 포맷팅 (3건)
- **E-4** `company_intro.py`: "사업 개요 (요약)" + "사업 내용 상세 (한글)" 박스 paragraph → bullet 자동 변환. 한글 문장 끝(다./음./함./~.) 기준 split.
- **E-5** `deep_research.py`: 산업 맥락 `overview` field paragraph → bullet 자동 변환.
- **E-6** `translate_thesis_eval.py` (신규 utility): thesis_eval rationale·counter_evidence·supporting_data·key_assumption의 영어 → 한글 번역. gpt-4o-mini batch 8, ~$0.01/run. 기술 용어(HBM·DRAM·Foundry·ROE 등) + 회사명(Samsung·TSMC·NVIDIA) 영문 유지. `.bak` 자동 백업.

#### P2 페이지 최적화 (2건)
- **E-7** `macro_renderer.py`: OECD Leading Indicators 57개국 raw table → 1줄 summary 기본 모드. `OECD_FULL_TABLE=1` env로 강제 가능. 데이터는 macro_snapshot.json에 그대로 유지(분석 활용).
- **E-8** `news_disclosures.py`: Samsung 005930.KS NEWS_TIMELINE 24건 추가 (2025-05 ~ 2026-05, 13개월 분포). HBM3e·Foundry 2nm·Galaxy AI·자사주 매입·환율 등 catalysts 기반.

#### Persona Matrix 진단 (1건)
- **E-10** `build_r2.py`: thesis × persona stance 매트릭스가 "모든 stance neutral" 거짓 진단하던 버그 수정. heatmap 0 cell ≠ "neutral 평가". 미평가 cell은 별도 `None`/회색 처리. `claim_id` 외 `claim_text` substring fuzzy 매칭 fallback 추가. 실제 stance 분포(support N · neutral N · challenge N · 미평가 N) 명시.

### Sprint F (2건) — UX 고도화

- **F-1** `guru_checklist.py`: Checklist qualitative 항목에서 "정성 평가 — 실데이터로 정량 검증 불가. 페르소나 본문 평가 참조." 단순 메시지 → `_extract_persona_evidence()` 호출하여 페르소나 본문에서 정성 의견 추출. evidence 발견 시 "페르소나 본문에서 추출한 의견:" + 구체적 stance·rationale 인용. evidence 진짜 없으면 "페르소나 본문에서도 명시적 평가 없음" 명시.
- **F-2** `deep_research.py` `_short_rationale()` + `_to_eumsumche()` + `_split_to_sentences()` 신설: 4-Analyst rationale paragraph → bullet point + 한국어 음슴체 변환. 격식체("~습니다/입니다/됩니다") → 음슴체("~함/임/음"). 3-pass 변환: (1) 직접 매핑 (보입니다·있습니다 등), (2) "습니다 → 음" general catch-all + 한글 자모 종성 ㅂ → ㅁ 자동 변환 (나타냅니다 → 나타냄), (3) 반말 종결 (한다/된다/이다 → 함/됨/임). 검증: 48건 rationale에서 격식체 잔존 0건, 음슴체 50회 등장.

### 검증 데이터 (삼성전자 005930.KS)

- 90페이지 PDF 빌드 (v3 → v4 패치 적용)
- 17/17 persona aggregator 성공 — lean_bullish 10명 (58.8%) · neutral 5명 · lean_bearish 2명 · avg confidence 0.77
- 4-Analyst real evaluation 48/48 (12 thesis × 4 analyst), 영어 rationale → 한글 번역 완료
- Data tagging: actual 158 / inference 67 / assumption 116 (341 total)
- NEWS Timeline 24 entries (13개월 분포)

---

## v0.8.0 (2026-06-02) — Phase 7: Evidence Layer (외부 근거 + 팩트체크)

AMEET-style "외부 1차 자료 조회 → 교차검증 → 인용" 레이어 추가.

- `evidence_retriever.py` — WebSearch + SEC EFTS + DART 통합 evidence 수집
- `fact_checker.py` — thesis↔evidence 모순 / 무출처 정량 / 밸류 정합성 3종 검증
- Citation Audit 섹션 자동 렌더 (🔴conflict / 🟡unsourced / 🟢confirmed)
- 옵션 `FACTCHECK_LLM=1` for codex LLM 검증

## v0.7.0 (2026-05-20) — LangSmith + Codex + Claude Code 호환

- LangSmith tracing (`@traced_call` decorator)
- `codex-integration` plugin (Claude vs OpenAI cross-validation)
- Claude Code 환경 호환 (`CLAUDE_CODE_QUICKSTART.md`)

## v0.6.0 (2026-05-20) — Tier 2 Specialist Agents

- `specialist-agents` plugin (Research Manager · Sentiment Analyst · Earnings Reviewer · Model Builder)
- Checkpoint manager (10-stage 진행 상태 영구 저장)
- Multi-LLM 3-tier 비용 라우팅 (83% 절감)

## v0.5.0 (2026-05-11) — Financial Statements + News Improvements

- `finance:financial-statements` US-GAAP 5Y annual + 5Q quarterly 의무 활용
- Thesis × Persona Matrix 정상화 + 명시적 진단 메시지
- News Timeline 중립 제외 + 월별 +/- bar chart
- Deep Research 위치 승격 (Section 8 → Section 3)
