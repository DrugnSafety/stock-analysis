# Multi-Model Arena

Claude(Anthropic) + GPT-5.5(OpenAI) + Gemini 3.1(Google)을 하나의 입력에 대해 **병렬·독립적으로 실행**하고, 결과의 **합의(consensus)와 이견(disagreement)을 자동 분석**하는 plugin.

`naver-blog-investment` plugin과 함께 사용해 메르 블로그 등 한 글에서 누락 종목을 최소화하고 verdict의 신뢰도를 calibration한다.

## 핵심 가치

| 단일 모델 분석의 한계 | Arena의 해법 |
|---|---|
| 학습 cutoff에 따른 신규 IPO 누락 (예: 대한조선 439260) | 3개 모델의 union → recall 최대화 |
| 단일 모델의 확증편향 | 3개 verdict 분포로 calibration |
| Bull/Bear thesis의 일방성 | adversarial 모드: 모델별로 입장 부여 |
| 단편적 ticker→verdict 직선 흐름 | consensus + disagreement 시각화 |

## 6개 skill 번들

| Skill | 역할 | LLM 사용 |
|---|---|---|
| **api-key-manager** | .env 로드, 키 마스킹, 유효성 검증 | ❌ |
| **openai-worker** | GPT-5.5 reasoning으로 종목 추출·7-role 분석 | ✅ (OpenAI API) |
| **gemini-worker** | Gemini 3.1 deep think로 종목 추출·7-role 분석 | ✅ (Google API) |
| **arena-orchestrator** | 3개 모델 병렬 호출 + 결과 정규화 | 통합만 |
| **consensus-builder** | union·verdict 분포·이견 영역·calibration | ❌ |
| **(claude-worker)** | 세션 내부 Claude 직접 사용 (별도 skill 아님, 인라인) | ✅ (Cowork plan) |

## API 키 입력 방법

워크스페이스 루트에 `.env` 파일 생성:

```env
# /Users/mingyukang/Documents/Claude/Projects/주식 분석/.env
OPENAI_API_KEY=sk-...your-key...
GOOGLE_API_KEY=AIza...your-key...
```

`.env`는 `.gitignore`에 자동 추가되며, 모든 로그·결과 파일에는 키 첫 4자리만 마스킹되어 기록됩니다.

## 명령

| 명령 | 설명 |
|---|---|
| `/arena-extract <BLOG_URL_or_post.json>` | 3개 모델로 종목 추출 → union + 합의 점수 |
| `/arena-analyze <TICKER>` | 단일 종목에 3개 모델 7-role 분석 → consensus verdict |
| `/arena-debate <TICKER>` | Bull(Claude) vs Bear(GPT-5.5) vs Skeptic(Gemini) 의도적 대결 |

## Cowork-Native + External API 하이브리드

- Claude는 세션 내부 (Cowork plan에 포함된 사용량)
- OpenAI, Gemini는 사용자 API 키 (별도 과금)
- 모든 API 호출은 비용·소요시간을 분석 메타데이터에 기록 (`/tmp/arena_usage.json`)

## 의존성

`pip install -r requirements.txt`로 설치:
- `openai>=1.50.0`
- `google-generativeai>=0.8.0`
- `python-dotenv>=1.0.0`
- `tenacity>=8.2.0`

## 출력 스키마 (consensus 결과)

```json
{
  "blog_url": "...",
  "models_run": ["claude-opus-4-7", "gpt-5.5", "gemini-3.1"],
  "extraction_consensus": {
    "all_companies_union": [...],          // 모든 모델이 추출한 회사 합집합
    "consensus_companies": [...],           // 3개 모델 모두 추출한 회사
    "single_model_only": [...],             // 1개 모델만 추출 — 누락 가능성 검토
    "consensus_score_per_company": {"...": 0.67}
  },
  "verdict_consensus": {
    "ticker": {
      "claude": {"verdict": "BUY", "confidence": 0.74},
      "openai": {"verdict": "BUY", "confidence": 0.81},
      "gemini": {"verdict": "HOLD", "confidence": 0.62},
      "weighted_verdict": "BUY",
      "agreement_level": "high|medium|low",
      "disagreement_summary": "..."
    }
  },
  "cost_summary": {"openai_usd": 0.42, "google_usd": 0.18, "total_usd": 0.60}
}
```

## 사용 시 주의

- **API 키 비용**: GPT-5.5 + Gemini 3.1 풀 분석 1회 ≈ $0.50-$2.00 (입력 길이에 따라)
- **동일 입력의 비결정성**: 같은 글에 같은 모델이라도 결과가 미세하게 다를 수 있음 (temperature·sampling)
- **모델 가용성**: 모델명은 `.env`의 `OPENAI_MODEL`, `GOOGLE_MODEL`로 override 가능. 서비스 종료된 모델로 호출 시 자동 fallback (gpt-4.1, gemini-2.5-pro)
