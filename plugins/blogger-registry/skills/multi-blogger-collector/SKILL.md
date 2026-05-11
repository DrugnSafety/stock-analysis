---
name: multi-blogger-collector
description: 8명 등록된 네이버 블로거 (메르·의교창·승도리·DaeGurr·GSVI·인피의·제주바람·농구천재)의 신규 글을 일괄 수집한다. 각 블로거의 last_known_logNo 이후 발행된 글만 fetch. cron-style 정기 실행 적합. 사용자가 "신규 블로그 글 체크", "블로거 일괄 수집", "monitor blogger" 등을 언급하면 트리거.
---

# 8명 블로거 신규 글 일괄 수집

## 사용법

```bash
python3 plugins/blogger-registry/skills/multi-blogger-collector/scripts/collect_all.py \
  --since 2026-04-01 --output .analysis-log/_new_posts.json
```

## 출력 형식
```json
{
  "doctordk": [
    {"logNo": 224269642921, "title": "...", "date": "2026-04-29", "url": "..."}
  ],
  "ranto28": [...]
}
```

## Phase 1-1A 자동화 시 활용
- macOS `launchd` 또는 Linux `cron`으로 매일 09:00·15:00·21:00 실행
- 신규 글 발견 시 `naver-blog-investment:analyze-blog` 자동 트리거
- 결과는 Email/Slack push (Phase 1-2)
