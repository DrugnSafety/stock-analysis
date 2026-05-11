# News Integration Plugin

NewsAPI + Finnhub freemium API를 통해 미국 종목의 1년치 뉴스를 자동 fetch하여 분석 보고서에 통합한다. **API 키 없으면 graceful fallback** (curated 데이터 사용).

## 🎯 무엇을 해결하는가?

**Before**:
- 미국 종목 뉴스는 hardcoded 10건 sample (BTU 등)
- 새 뉴스 누락 빈번
- 영향도 (+/-/○) 수동 분류

**After**:
- NewsAPI + Finnhub에서 자동 fetch
- 키워드 기반 영향도 자동 분류 (LLM 분류는 Phase 2)
- 24시간 캐시로 효율 운영

## 📋 셋업 (5분, 둘 다 무료)

### NewsAPI

1. https://newsapi.org/register — 회원가입 (이메일만)
2. Dashboard에서 API 키 복사
3. **Free tier**: 100 calls/day · 30일 lookback · 다국어

### Finnhub (권장 — 회사별 정확한 매핑)

1. https://finnhub.io/register — 회원가입
2. Dashboard → API Keys 복사
3. **Free tier**: 60 calls/min · 365일 lookback

### `.env` 추가

```
# 둘 중 하나 또는 둘 다
NEWSAPI_KEY=...
FINNHUB_KEY=...
```

미설정 시 자동으로 curated fallback 사용 — 시스템 작동에 영향 없음.

### 동작 확인

```bash
cd "/Users/mingyukang/Documents/Claude/Projects/주식 분석"
python3 plugins/news-integration/scripts/news_client.py BTU "Peabody Energy"
```

기대 출력:
```
News integration status: {"newsapi_configured": true, "finnhub_configured": true, "any_active": true}
BTU news (1Y): 32 items
  2026-04-30 + Peabody beats Q1 estimates...
  2026-04-22 + EBITDA jumps 25% on AI demand...
  ...
```

## 🔧 모듈 구성

```
plugins/news-integration/
├── plugin.json
├── README.md (이 파일)
├── scripts/
│   └── news_client.py          ← NewsAPI + Finnhub aggregator
├── skills/
│   └── news-fetcher/
│       └── SKILL.md
└── cache/                       ← (gitignored, runtime cache)
```

연동 지점:
- `report-suite/_common/news_disclosures.py` — `get_news_items()` 가 자동 호출
- `unified-builder/scripts/build_combined.py` — 미국 종목 보고서 생성 시 자동 활성

## 🔍 API 비교

| 항목 | NewsAPI | Finnhub |
|---|---|---|
| Free quota | 100 calls/day | 60 calls/min |
| Lookback (free) | 30일 | 365일 |
| 회사 정확 매핑 | ✗ (키워드 기반) | ✓ (ticker 기반) |
| 다국어 | ✓ (한국어 가능) | × (영어 위주) |
| Source 다양성 | ✓ (수천 곳) | ✓ (회사 IR 포함) |

→ **권장**: Finnhub 우선 + NewsAPI 보충

## 🔄 영향도 분류 룰 (현재 — Phase 2에서 LLM 업그레이드)

키워드 기반:

- **+ (긍정)**: BEAT, EXCEED, RAISE, ACQUIRE, BUYBACK, GROWTH, UPGRADE, AWARD, APPROVAL, NEW PRODUCT
- **- (부정)**: MISS, DOWNGRADE, LAWSUIT, BANKRUPTCY, RESIGN, RECALL, INVESTIGATION, LAYOFF, PROBE
- **○ (중립)**: 그 외

## ⚠️ 한계 및 주의사항

1. **NewsAPI free tier**: 30일 lookback만 → 30일 이전 뉴스는 fetch 불가. Finnhub 보완 필요.

2. **Quota exhaustion**: 매일 분석 1회면 NewsAPI 100 calls/day로 충분. 잦은 backtest 시 quota 도달 가능.

3. **영향도 keyword 분류**: 정확도 70-80% 수준. 동음이의어 ("strike a deal" vs "labor strike") 오류 가능. Phase 2에서 LLM 분류로 업그레이드 권고.

4. **회사 매핑**: NewsAPI는 query 기반 — 같은 이름 다른 회사 (예: "Apple" → Apple Inc + apple.com 등) 노이즈 가능. Finnhub은 ticker 기반이라 정확.

## 🚀 다음 단계 (Phase 2-4 이후)

- [ ] LLM 기반 영향도 분류 (Claude Haiku — 100 articles ~$0.10)
- [ ] Sentiment score (1-5 점수)
- [ ] Topic clustering (AI / 어닝 / M&A / 정책 자동 그룹화)
- [ ] Relevance ranking (회사 vs 산업 vs 거시 분리)
- [ ] Twitter / X integration (Phase 3)
