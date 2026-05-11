---
name: dart-status
description: DART API 활성 상태 점검 + 캐시 상태 확인 + 샘플 fetch 테스트.
---

DART API 통합 상태를 점검합니다:

1. **DART_API_KEY env 확인**:
```bash
python3 -c "
import sys; sys.path.insert(0, 'plugins/dart-integration/scripts')
from dart_client import get_status
import json; print(json.dumps(get_status(), ensure_ascii=False, indent=2))
"
```

2. **corp_codes.xml 캐시 상태**:
```bash
ls -la ~/.cache/dart_integration/
```

3. **샘플 ticker fetch 테스트** (POSCO홀딩스):
```bash
python3 plugins/dart-integration/scripts/dart_client.py 005490.KS
```

**기대 결과**:
- `configured: true` (DART_API_KEY 있음)
- `corp_codes_cached: true` (XML 다운로드 완료)
- 005490.KS → corp_code: 00126380
- Disclosures (1Y): 47+ items

**문제 해결**:
- `configured: false` → `.env`에 `DART_API_KEY=...` 추가 필요
- `corp_codes_cached: false` → 첫 호출 시 자동 다운로드 (XML 약 4MB, 30초 소요)
- API 오류 → https://opendart.fss.or.kr/mng/apiKeyManage.do 키 활성 상태 확인
