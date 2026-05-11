---
name: validate-analysis
description: 분석 디렉토리가 canonical format을 따르는지 검증. 28+ checks. 새 분석 종료 시 의무 실행.
argument-hint: <분석 디렉토리 경로>
---

분석 디렉토리: $ARGUMENTS

다음 명령으로 canonical format 준수 검증:

```bash
cd "/Users/mingyukang/Documents/Claude/Projects/주식 분석"
python3 plugins/report-suite/skills/unified-builder/scripts/validate_format.py "$ARGUMENTS"
```

## 검증 항목 (총 28+)

### [1/5] Required top-level files (8개)
- meta.json, thesis_list.json, stocks.json
- thesis_eval/all_aggregate.json
- persona_panel/_all_aggregates.json
- risk_limits.json, decisions.json, portfolio.json

### [2/5] Thesis 검증
- thesis ≥ 5개
- core thesis ≥ 3개

### [3/5] Stocks 검증
- stock ≥ 3개
- 모든 stock에 market_data 포함

### [4/5] Persona panels (per ticker)
- 각 ticker 폴더 + aggregate.json
- 13명 페르소나 모두 존재 (Buffett·Munger·Lynch·Wood·Burry·Taleb·Graham·Ackman·Pabrai·Fisher·Jhunjhunwala·Druckenmiller·Damodaran)

### [5/5] Layer 1 PDFs
- reports/combined/ 디렉토리 존재
- ≥ 3개 combined PDFs
- naming: {idx}_{ticker}_{name}_combined.pdf

### [bonus] Layer 2 overview
- overview.md / .pdf / .pptx (권장)

## Exit Code
- 0 — 모든 checks 통과 → canonical format 일치
- 1 — 1개 이상 실패 → REPORT_FORMAT_STANDARD.md 참조해서 보완

## 자동 호출

`commands/analyze-blog.md`의 마지막 단계에서 자동 실행. 새 분석 종료 시 반드시 통과 확인.
