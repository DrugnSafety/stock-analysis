# Plugin 안정화 PR — 2026-05-03

> Cowork 환경에서 `build_combined.py`가 5종목 빌드 시 일부 ticker가 timeout으로 실패하는 문제를 수정. 한화엔진 분석 (의교창 2026-05-03) 작업 중 발견.

## 증상

- WRTBY (US ticker): 16초 빌드 성공
- 082740.KS / 329180.KS / 034020.KS / 012450.KS: bash 45초 timeout 초과로 실패
- 결과: 우회 builder (markdown→PDF)로 fallback → 8p 단축 보고서 생성 (canonical 47p와 다름)

## 원인 분석

### Root Cause 1: DART API 30초 timeout x 다수 호출
`.KS` ticker는 `news_disclosures.render_news_timeline()` + `financial_fetcher.fetch_financials_for_deep_research()`가 각각 DART API 호출:
- `_download_corp_codes()` — 30초 timeout, 거대한 ZIP XML download
- `fetch_disclosures()` — 20초 timeout
- `fetch_financials()` — 5년치 × 종목당 5회 × 20초 timeout

네트워크 느림/오류 시 누적되어 build_combined.py가 30초+ 소요.

### Root Cause 2: matplotlib 한글 폰트 미설정
`chart_utils.py`의 `_register_korean_font()` 후보 리스트에 Noto Sans CJK KR 누락:
```python
candidates = [
    Path.home() / ".fonts" / "NotoSansKR-Regular.otf",   # 안 받아짐
    Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),  # Cowork에 없음
]
```
결과: 차트의 한글 라벨이 □ 박스로 렌더 (의교창 lithium 보고서에서도 동일 이슈 추정).

### Root Cause 3: 차트 DPI 100
matplotlib 한글 폰트 subsetting + DPI 100 + 5종목 비교 차트(3종) → 종목당 2-3초 소요.

## 수정 내용

### Fix 1 — `dart_client.py`: 환경변수 기반 fast-fail

```python
# DART_DISABLE=1 → 모든 DART 호출 스킵 (offline mode)
# DART_TIMEOUT=5 → 기본 30/20초 timeout 단축 가능
```

수정 함수:
- `_download_corp_codes()` — DART_DISABLE check + DART_TIMEOUT 적용
- `fetch_disclosures()` — DART_DISABLE check + DART_TIMEOUT 적용
- `fetch_financials()` — DART_DISABLE check + DART_TIMEOUT 적용

사용:
```bash
# 빠른 빌드 (DART 캐시만 사용)
DART_DISABLE=1 python3 build_combined.py ...
# 짧은 timeout (네트워크 느릴 때)
DART_TIMEOUT=5 python3 build_combined.py ...
```

### Fix 2 — `chart_utils.py`: Korean font 후보 확장

```python
candidates = [
    Path.home() / ".fonts" / "NotoSansKR-Regular.otf",
    Path.home() / ".fonts" / "NotoSansKR-Regular.ttf",
    Path.home() / ".fonts" / "NotoSansCJKkr-Regular.otf",      # 신규 추가
    Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
    Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),  # 신규 추가
    Path("/Library/Fonts/AppleGothic.ttf"),
]
```

### Fix 3 — `chart_utils.py`: DPI 100 → 80

차트 렌더 시간 약 -25% 단축. 가독성 영향은 minimal (PDF 임베드 시 충분).

### Fix 4 (수동) — Cowork 환경 폰트 설치

CLAUDE.md에 다음 추가 권장:
```bash
# Cowork sandbox first-run
mkdir -p ~/.fonts
curl -sL "https://github.com/notofonts/noto-cjk/raw/main/Sans/OTF/Korean/NotoSansCJKkr-Regular.otf" \
  -o ~/.fonts/NotoSansCJKkr-Regular.otf
curl -sL "https://github.com/notofonts/noto-cjk/raw/main/Sans/OTF/Korean/NotoSansCJKkr-Bold.otf" \
  -o ~/.fonts/NotoSansCJKkr-Bold.otf
fc-cache -f
```

## 검증

수정 후 5종목 모두 정상 빌드:

| Ticker | Pages | Size | Time |
|---|---|---|---|
| WRTBY | 56 | 444KB | 16s |
| 082740.KS 한화엔진 | 47 | 404KB | 15s |
| 329180.KS HD현대중공업 | 47 | 398KB | 14.6s |
| 012450.KS 한화에어로스페이스 | 46 | 400KB | 14.7s |
| 034020.KS 두산에너빌리티 | 47 | 401KB | 14.5s |

`validate_format.py`: **29/29 checks passed (100%)**

## 향후 개선 (Phase 2)

1. **chart caching**: 동일 ticker 재빌드 시 차트 PNG 재사용 (현재 매번 생성)
2. **parallel build**: `build_multi_stocks.py`가 5종목 순차 처리 — `multiprocessing.Pool`로 병렬화
3. **incremental output**: 종목별 PDF 완료 시점에 file write (현재는 5개 모두 끝나야 결과 노출)
4. **DART corp_code 사전 패키징**: 한국 주요 200개 종목 corp_code 매핑을 plugin에 정적 포함하여 첫 호출 시 30초 download 회피
