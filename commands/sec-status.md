---
name: sec-status
description: SEC EDGAR + NewsAPI/Finnhub 통합 상태 점검 + 샘플 fetch 테스트.
---

미국 주식 데이터 통합 상태 점검:

```bash
cd "/Users/mingyukang/Documents/Claude/Projects/주식 분석"

echo "=== SEC EDGAR ==="
python3 -c "
import sys; sys.path.insert(0, 'plugins/sec-edgar-integration/scripts')
from sec_client import get_status
import json; print(json.dumps(get_status(), ensure_ascii=False, indent=2))
"

echo ""
echo "=== News Integration (NewsAPI + Finnhub) ==="
python3 -c "
import sys; sys.path.insert(0, 'plugins/news-integration/scripts')
from news_client import get_status
import json; print(json.dumps(get_status(), ensure_ascii=False, indent=2))
"

echo ""
echo "=== Financial fetcher 통합 라우터 ==="
python3 -c "
import sys; sys.path.insert(0, 'plugins/report-suite/skills/_common')
from financial_fetcher import get_status
import json; print(json.dumps(get_status(), ensure_ascii=False, indent=2))
"
```

## 샘플 fetch 테스트

### BTU (Peabody Energy) SEC 공시 5건
```bash
python3 plugins/sec-edgar-integration/scripts/sec_client.py BTU
```

### BTU 5년 P&L (10-K XBRL)
```bash
python3 -c "
import sys; sys.path.insert(0, 'plugins/sec-edgar-integration/scripts')
from sec_client import fetch_financial_5y
fin = fetch_financial_5y('BTU')
for row in fin.get('pl_5y', []):
    print(f'{row[\"year\"]}: rev=\${row[\"revenue\"]:.0f}M, OPM={row[\"op_margin\"]:.1f}%')
"
```

### BTU 뉴스 (NewsAPI/Finnhub 키 있을 때)
```bash
python3 plugins/news-integration/scripts/news_client.py BTU "Peabody Energy"
```

## 활성 상태 매트릭스

| 데이터 소스 | 키 필요? | 종목 type |
|---|---|---|
| **DART** | DART_API_KEY ✓ 활성 | 한국 (.KS / .KQ) |
| **SEC EDGAR** | 불필요 ✓ 즉시 활성 | 미국 (모든 NYSE/NASDAQ) |
| **NewsAPI** | NEWSAPI_KEY 필요 | 모든 종목 |
| **Finnhub** | FINNHUB_KEY 필요 | 미국 우선 |

## 문제 해결

- **SEC 응답 느림**: 첫 호출 시 ticker→CIK map 다운로드 (4MB, 30초). 이후 30일 cache.
- **403 Forbidden (SEC)**: User-Agent header 누락 — `.env`에 `SEC_USER_AGENT=` 추가.
- **NewsAPI 401**: 키 무효화 — https://newsapi.org/account 에서 재발급.
- **Quota exceeded**: NewsAPI 100/day, Finnhub 60/min — 잦은 backtest 시 도달 가능.
