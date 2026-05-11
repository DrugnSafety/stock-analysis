---
name: registry-loader
description: registry.yaml 파일에서 8명 블로거 메타데이터를 로드한다. 각 블로거의 specialty (KR market·US bio·tanker·macro 등), 페르소나 가중치 override, 최근 분석 이력 등 제공. 사용자가 "블로거 정보", "블로거 specialty", "페르소나 가중치 조회" 등을 언급하면 트리거.
---

# Blogger Registry 메타데이터 로더

## 사용법

```python
from plugins.blogger_registry.skills.registry_loader.scripts.loader import load_registry

reg = load_registry()
print(reg["doctordk"]["specialty"])  # "korean_industrial + lithium"
print(reg["doctordk"]["persona_weights"])
# {"stanley-druckenmiller": 1.5, "warren-buffett": 0.7, ...}
```

## registry.yaml schema

```yaml
doctordk:
  url: https://blog.naver.com/doctordk
  specialty: korean_industrial + lithium
  language: ko
  persona_weights:
    stanley-druckenmiller: 1.5
    warren-buffett: 0.7
  recent_post_count: 24
  hit_rate_1m: 0.66
```
