# Local Runner — bash sandbox 우회

Cowork bash sandbox는 `bwrap --unshare-pid --die-with-parent`로 자식 프로세스를 45초 후 강제 종료합니다. gpt-5.5 + reasoning_effort=high처럼 60-180초 걸리는 호출은 그 안에 못 끝나죠.

이 폴더의 스크립트는 **사용자 자신의 macOS Terminal**에서 직접 실행되어 그 제약을 받지 않습니다.

## 사용법

### 1회 셋업

```bash
cd "/Users/mingyukang/Documents/Claude/Projects/주식 분석"
chmod +x plugins/multi-model-arena/local-runner/*.sh

# 의존성 설치 (한번만)
pip3 install -r plugins/multi-model-arena/requirements.txt
pip3 install -r plugins/naver-blog-investment/requirements.txt
```

### 분석 실행

```bash
# 메르 블로그 글 한 편에 대한 풀 thesis-first arena 분석
./plugins/multi-model-arena/local-runner/run_arena.sh https://blog.naver.com/ranto28/224264942275

# 단일 ticker 풀 7-role 분석 (블로그 컨텍스트와 함께)
./plugins/multi-model-arena/local-runner/run_analyze.sh 439260.KS https://blog.naver.com/ranto28/224264942275
```

## 어떤 모델을 어떻게 쓰는가

| 단계 | 모델 | 모드 | 환경 |
|---|---|---|---|
| naver-blog-scraper | (없음) | Python | 로컬 |
| thesis-extractor | gpt-5.5 | reasoning=high | 로컬 (60-120s OK) |
| thesis-evaluator (4 analysts) | gpt-5.5 + gemini-3.1 | reasoning/deep_think | 로컬 |
| thesis-to-stocks | gpt-5.5 | reasoning=high | 로컬 |
| stock-extractor | gpt-5.5 + gemini + claude | arena | 로컬 (gpt-5.5) + Cowork(Claude) |
| trading-analysis (7-role) | gpt-5.5 + gemini + claude | arena | 로컬 (gpt-5.5) + Cowork(Claude) |
| report-generator | (Python) | 템플릿 | 로컬 |

Claude(Cowork) 결과가 필요한 단계는 `*.pending.json` 파일을 만들어두면, 다음 Cowork 세션에서 Claude가 받아 채울 수 있도록 설계.

## 결과 저장 위치

```
/Users/mingyukang/Documents/Claude/Projects/주식 분석/.analysis-log/arena/
└── 2026-04-28_<slug>/
    ├── post.json
    ├── thesis_list.json           # ★ 메르 주장 N개
    ├── thesis_eval_<id>.json      # ★ 각 주장 4-Analyst 평가
    ├── thesis_to_stocks.json      # ★ 주장 → 종목 매핑
    ├── arena_extract/
    │   ├── claude.pending.json
    │   ├── openai.json
    │   └── gemini.json
    ├── arena_analyze_<ticker>/
    │   └── ...
    ├── consensus_extract.json
    ├── consensus_analyze_<ticker>.json
    └── report_<slug>.pdf          # 종합 보고서
```

## Cowork 세션과의 협업

로컬 실행 후 Cowork 채팅창에 다음과 같이 말하면 Claude가 pending 결과를 채워줍니다:

> "워크스페이스의 .analysis-log/arena/2026-04-28_canada-crude/ 의 pending JSON들을 채워줘"

Claude는 각 `*.pending.json`의 instruction을 읽고, 본문 + market data를 직접 분석해 결과를 덮어쓴 뒤, 최종 consensus와 PDF를 생성합니다.

## 비용 통제

- `.env`의 `ARENA_MAX_COST_USD=2.00` 한도 초과 시 중단
- 각 호출마다 `cost_log.jsonl`에 기록
- `--dry-run` 옵션으로 비용 추정만 출력 가능

## 비활성화·축소 옵션

```bash
# Gemini 제외 (quota=0인 경우)
./run_arena.sh URL --skip gemini

# Claude도 제외, OpenAI만 (테스트용)
./run_arena.sh URL --only openai

# thesis 단계 건너뛰고 기존 종목 추출 흐름만
./run_arena.sh URL --skip-thesis
```
