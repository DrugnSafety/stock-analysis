---
name: readme-generator
description: 분석 결과 폴더에 학습 친화적 README.md를 자동 생성한다. 8단계 파이프라인 설명, 블로거 소개, FAQ-style 결과 해석, 보고서 활용 가이드 포함. 사용자가 "샘플 README", "분석 결과 설명서", "학습용 가이드" 등을 언급하면 트리거.
---

# Per-Sample README.md Generator

각 분석 폴더 (`.analysis-log/.../{date}_{slug}/`)에 학습 친화적 README.md 생성.

## 호출
```bash
python3 plugins/report-suite/skills/readme-generator/scripts/build_readme.py \
  --pipeline-dir .analysis-log/bloggers/doctordk/2026-04-29_lithium \
  --output README.md
```

## README 구성
1. 분석 요약 (블로거·종목·결과)
2. 8단계 분석 파이프라인 설명
3. 블로거 소개 (specialty, hit rate)
4. FAQ-style 결과 해석 (verdict 의미, signal score 활용 등)
5. 보고서 활용 가이드 (R1/R2/R3 읽는 법)
6. 한계점 (Honest Disclosure)
