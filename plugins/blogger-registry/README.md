# Blogger Registry Plugin

다중 네이버 블로거를 통합 관리하는 plugin. 8명 (메르 외 7명)의 메타데이터·신뢰도 가중치·카테고리·분석 스타일을 한 곳에서 관리.

## 핵심 기능

| 기능 | 설명 |
|---|---|
| **블로거 메타** | nickname / blog_name / category / 분석 스타일 / typical topics |
| **신뢰도 가중치** | backtest 적중률 누적으로 자동 학습 (한국·미국 시장 별도) |
| **자동 라우팅** | blog_id만 주면 collector·analyzer·ledger 분기 자동화 |
| **블로거별 ledger 분리** | `.analysis-log/bloggers/<blog_id>/ledger.jsonl` |
| **블로거별 alpha 비교** | 누가 한국 시장에서 가장 alpha 있는지 backtester가 측정 |

## Plugin 구조

```
plugins/blogger-registry/
├── plugin.json
├── README.md
├── registry.yaml              ← 8명 블로거 메타 (편집 가능)
├── skills/
│   ├── registry-loader/       ← yaml 읽고 Python dict로 노출
│   ├── multi-blogger-collector/  ← collect_blogger.py (일반화)
│   └── blogger-stats/         ← 블로거별 적중률·alpha 비교
└── commands/
    ├── analyze-blogger.md     ← /analyze-blogger <blog_id> <log_no>
    ├── multi-collect.md       ← /multi-collect (모든 블로거 신규 글)
    └── blogger-leaderboard.md ← /blogger-leaderboard (적중률 랭킹)
```

## 다른 plugin과의 관계 — 변경 없음

기존 plugin들(naver-blog-investment, multi-model-arena, investor-personas, trade-engine, backtester, subagent-orchestrator)은 **이미 blog-agnostic**이라 코드 수정 거의 불필요. registry가 그 위에 얹히는 routing layer.

## 기존 → 신규 디렉토리 전환

```
이전:
.analysis-log/
├── arena/
├── backtest_real/
└── sa_debate_demo/

신규:
.analysis-log/
├── bloggers/
│   ├── ranto28/         ← 메르 (기존 데이터 이전)
│   │   ├── posts/
│   │   ├── ledger.jsonl
│   │   ├── arena/
│   │   ├── persona_panel/
│   │   └── debates/
│   ├── doctordk/        ← 신규
│   │   └── ...
│   ├── sungdory/
│   ├── daegurrr_/
│   ├── dlaldhr0821/
│   ├── infidoc/
│   ├── onejejuwave/
│   └── tosoha1/
└── _global/
    ├── leaderboard.json   ← 블로거별 alpha 비교
    └── consolidated_ledger.jsonl  ← 모든 블로거 통합 ledger (옵션)
```

## 사용 예

```bash
# 단일 블로거 신규 글 분석
/analyze-blogger doctordk 224250000000

# 모든 블로거 새 글 일괄 collect
/multi-collect --since 2026-04-01

# 블로거 적중률 랭킹
/blogger-leaderboard --horizon 1m
```

## 신뢰도 가중치 — 자동 학습 메커니즘

각 블로거의 적중률이 누적되면 trust_weight 자동 갱신:

```yaml
ranto28:
  trust_weight_kr: 1.20   # backtest로 alpha +2% 입증
  trust_weight_us: 1.10
  hit_rate_history:
    - {as_of: "2026-04-28", n_verdicts: 18, hit_rate_1m: 0.66, alpha_kospi: 2.03}
```

backtester가 새 verdict의 horizon 도달 시 자동 update. portfolio-manager가 trust_weight를 페르소나 가중치와 곱하여 signal 강도 계산.

## 라이선스

각 블로거의 본문은 그 블로거의 저작물. 본 plugin은 분석 결과만 보존 (원문 미캐시). 메타데이터는 공개 정보.
