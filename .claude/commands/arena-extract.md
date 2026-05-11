---
name: arena-extract
description: Multi-Model Arena로 메르 블로그 글에서 종목을 추출. Claude(현재 세션) + GPT-5.5 + Gemini 3.1을 병렬 실행하여 union of tickers, 합의 점수, 단독 발견 종목을 식별. naver-blog-scraper와 연동되어 블로그 URL 하나로 풀 파이프라인 실행 가능. .env에 OPENAI_API_KEY, GOOGLE_API_KEY가 설정되어 있어야 한다.
---

# /arena-extract

세 모델(Claude·OpenAI·Gemini)을 동시에 가동해 한 글에서 누락 종목을 최소화한다.

## 사용법

```
/arena-extract <BLOG_URL>
```

또는 이미 스크래핑한 post.json 사용:

```
/arena-extract --post /tmp/post.json
```

옵션:
- `--include claude,openai,gemini` (기본 모두): 일부만 실행
- `--workers-only`: Claude는 건너뛰고 외부 모델만 (PoC용)
- `--no-grounding`: Gemini web grounding 비활성화

## Claude가 따를 절차

### Step 1: 환경 검증

```bash
python plugins/multi-model-arena/skills/api-key-manager/scripts/check_keys.py
```

- 두 키 모두 ✅면 진행
- 키 누락 시 .env 위치·필요 항목 안내 후 중단

### Step 2: 블로그 본문 수집 (URL이 입력일 때)

```bash
python plugins/naver-blog-investment/skills/naver-blog-scraper/scripts/scrape_naver_blog.py \
    "$URL" --output /tmp/post.json
```

### Step 3: Arena 디스패치

```bash
TS=$(date +%Y%m%d_%H%M%S)
OUT_DIR="/tmp/arena_extract_$TS"
python plugins/multi-model-arena/skills/arena-orchestrator/scripts/orchestrate_extract.py \
    /tmp/post.json --output-dir "$OUT_DIR" --include claude,openai,gemini
```

이 명령은:
- OpenAI worker, Gemini worker를 **병렬 실행**
- Claude worker용 placeholder를 `claude.json`에 생성

### Step 4: Claude 직접 추출 (in-session)

Claude는 stock-extractor SKILL.md의 7원칙을 따라 `/tmp/post.json`을 읽고, 결과를 `$OUT_DIR/claude.json`에 **덮어쓰기**.

(외부 API 비용 없음 — Cowork plan 사용량으로 처리)

### Step 5: Consensus 분석

```bash
python plugins/multi-model-arena/skills/consensus-builder/scripts/build_consensus.py \
    "$OUT_DIR" --type extract --output /tmp/consensus_extract.json
```

### Step 6: 시각화

```bash
python plugins/multi-model-arena/skills/consensus-builder/scripts/visualize.py \
    /tmp/consensus_extract.json --output /tmp/consensus.html --format html

# 또는 PDF
python plugins/multi-model-arena/skills/consensus-builder/scripts/visualize.py \
    /tmp/consensus_extract.json --output /tmp/consensus.pdf --format pdf
```

### Step 7: 결과 제시

사용자에게 다음 표 형태로 요약:

```
✅ Multi-Model Arena 추출 완료

블로그: 캐나다산 원유가 대안이 될 수 있을까?
실행 모델: Claude Opus 4.6 + GPT-5.5 + Gemini 3.1

📊 추출 통계
- 총 unique 종목: 17
- 3/3 합의: 8개 (가장 신뢰)
- 2/3 다수: 5개
- 1/3 단독: 4개 ← 검토 필요 (놓쳐선 안 될 인사이트일 수 있음)

🟢 3/3 합의 종목 (8건)
| 회사 | Ticker | 합의 점수 |
| SK이노베이션 | 096770.KS | 100% |
| ...

🔵 1/3 단독 발견 (4건) — 검토 권장
| 회사 | Ticker | 발견 모델 | 이유 |
| 대한조선 | 439260.KS | OpenAI | 신규 IPO, 다른 모델 학습 cutoff 외 |
| ... 

💰 비용: $0.42 (OpenAI) + $0.18 (Google) = $0.60
```

## 후속 작업 제안

- 단독 발견 종목 중 하나 선택 → `/arena-analyze <ticker>` 로 7-role 분석
- 모든 합의 종목 일괄 분석 → 별도 batch 스크립트 (개발 예정)
