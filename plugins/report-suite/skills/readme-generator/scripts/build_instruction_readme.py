#!/usr/bin/env python3
"""분석별 Instruction README.md 자동 생성 — v0.5.0.

기존 build_readme.py가 블로거 분석에 특화된 학습용 README를 만든다면,
이 새 스크립트는 standalone + bloggers 분석 모두를 지원하는
**operational instruction README**를 생성한다.

생성되는 README는 다음을 담는다:
- 분석 개요 (ticker, sector, source, verdict)
- 보고서 섹션 흐름 (v0.5.0 기준)
- 입력 데이터 schema 안내
- 빌드/재빌드 CLI 명령어
- 결과 파일 트리
- 주의사항 (데이터 출처·가정·한계)

사용법:
    python3 build_instruction_readme.py \
        --pipeline-dir .analysis-log/standalone/2026-05-11_LNG_Cheniere_Energy \
        --output README.md
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Optional


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _read_meta(pipeline_dir: Path) -> dict:
    return _read_json(pipeline_dir / "meta.json")


def _read_stocks(pipeline_dir: Path) -> list:
    s = _read_json(pipeline_dir / "stocks.json")
    if isinstance(s, dict):
        return s.get("stocks", []) or s.get("data", []) or []
    return s if isinstance(s, list) else []


def _read_thesis(pipeline_dir: Path) -> list:
    t = _read_json(pipeline_dir / "thesis_list.json")
    if isinstance(t, dict):
        return t.get("theses", []) or t.get("thesis_list", []) or []
    return t if isinstance(t, list) else []


def _read_aggregate(pipeline_dir: Path, ticker: str) -> dict:
    return _read_json(pipeline_dir / "persona_panel" / ticker / "aggregate.json")


def _read_decisions(pipeline_dir: Path) -> list:
    d = _read_json(pipeline_dir / "decisions.json")
    if isinstance(d, dict):
        return d.get("decisions", [])
    return d if isinstance(d, list) else []


def _list_reports(pipeline_dir: Path) -> list[str]:
    out = []
    rp = pipeline_dir / "reports"
    if not rp.exists():
        return out
    for p in rp.rglob("*.pdf"):
        rel = p.relative_to(pipeline_dir)
        size_kb = p.stat().st_size // 1024
        out.append(f"{rel} ({size_kb} KB)")
    return out


def _detect_analysis_type(pipeline_dir: Path) -> str:
    """standalone vs blogger."""
    s = pipeline_dir.parts
    if "standalone" in s:
        return "standalone"
    if "bloggers" in s:
        return "blogger"
    return "unknown"


def _detect_implicit_thesis(theses: list) -> bool:
    return any(t.get("_source", "") in ("catalyst", "risk", "macro", "industry", "financial", "sector_template") for t in theses)


def build_instruction_readme(pipeline_dir: Path) -> str:
    meta = _read_meta(pipeline_dir)
    stocks = _read_stocks(pipeline_dir)
    theses = _read_thesis(pipeline_dir)
    decisions = _read_decisions(pipeline_dir)
    reports = _list_reports(pipeline_dir)
    atype = _detect_analysis_type(pipeline_dir)
    is_implicit = _detect_implicit_thesis(theses)

    # Primary ticker
    primary_ticker = meta.get("ticker") or (stocks[0].get("ticker") if stocks else "UNKNOWN")
    company = meta.get("company_kr") or meta.get("company") or (stocks[0].get("kr_name") or stocks[0].get("name") if stocks else primary_ticker)
    sector = meta.get("sector") or (stocks[0].get("sector") if stocks else "")
    title = meta.get("title") or meta.get("blog_title") or f"{primary_ticker} 분석"
    blogger = meta.get("blog_author") or meta.get("blog_id") or ""
    blog_url = meta.get("blog_url") or ""
    analysis_date = meta.get("analyzed_at") or meta.get("blog_published_at") or meta.get("scraped_at") or pipeline_dir.name[:10]

    # Aggregate (verdict distribution)
    agg = _read_aggregate(pipeline_dir, primary_ticker)
    vd = agg.get("verdict_distribution", {})

    def vc(key):
        v = vd.get(key, {})
        return v.get("count", 0) if isinstance(v, dict) else (v or 0)

    bull = vc("lean_bullish")
    neut = vc("neutral")
    bear = vc("lean_bearish")
    avg_conf = agg.get("average_confidence") or agg.get("avg_confidence") or 0
    n_personas = agg.get("n_personas") or 0
    signal_score = (bull - bear) / max(n_personas, 1) if n_personas else 0

    # Decision
    primary_action = "n/a"
    primary_qty = ""
    if decisions:
        for d in decisions:
            if d.get("ticker") == primary_ticker:
                primary_action = d.get("action", "n/a").upper()
                primary_qty = f"{d.get('target_quantity', '?')} 주 (~${d.get('target_value', 0):,.0f})"
                break

    # Build markdown
    lines = []
    lines.append(f"# {primary_ticker} ({company}) — 분석 리포트")
    lines.append("")
    lines.append(f"> {title}")
    lines.append("")
    lines.append(f"**분석 종류**: {'블로그 글 기반' if atype == 'blogger' else 'Standalone (사용자 지정 종목)'}  ·  ")
    lines.append(f"**분석 일자**: {analysis_date}  ·  ")
    lines.append(f"**보고서 빌드**: v0.5.0")
    lines.append("")

    # ─── 1. 분석 개요 ─────────────────────────────
    lines.append("## 1. 분석 개요")
    lines.append("")
    lines.append(f"| 항목 | 내용 |")
    lines.append(f"|---|---|")
    lines.append(f"| **종목** | {primary_ticker} ({company}) |")
    if sector:
        lines.append(f"| **섹터** | {sector} |")
    lines.append(f"| **분석 종류** | {atype} |")
    if blogger:
        lines.append(f"| **블로거** | {blogger} |")
    if blog_url:
        lines.append(f"| **블로그 URL** | {blog_url} |")
    if stocks:
        lines.append(f"| **분석 대상 종목 수** | {len(stocks)}개 |")
    lines.append(f"| **추출 thesis 수** | {len(theses)}개 {'(implicit thesis 자동 추출 활용)' if is_implicit else ''} |")
    lines.append(f"| **페르소나 패널** | {n_personas}명 |")
    if n_personas:
        lines.append(f"| **Verdict 분포** | Bull {bull} / Neutral {neut} / Bear {bear} |")
        lines.append(f"| **Signal Score** | {signal_score:+.3f} |")
        lines.append(f"| **평균 Confidence** | {avg_conf:.2f} |")
    if primary_action != "n/a":
        lines.append(f"| **최종 Decision** | {primary_action} ({primary_qty}) |")
    lines.append("")

    # ─── 2. 보고서 섹션 흐름 (v0.5.0) ─────────────────
    lines.append("## 2. 보고서 섹션 흐름 (v0.5.0)")
    lines.append("")
    lines.append("이 분석으로 생성된 PDF는 다음 섹션 순서를 따릅니다 (per-stock combined PDF):")
    lines.append("")
    lines.append("| # | 섹션 | 데이터 소스 |")
    lines.append("|---|---|---|")
    lines.append("| 1 | Cover | meta.json + persona aggregate |")
    lines.append("| 2 | Company Intro | stocks.json (yfinance live) |")
    lines.append("| 3 | **Deep Research** (산업 + 재무 + 카탈리스트/리스크) | deep_research/{ticker}.json |")
    lines.append("| 4 | **Financial Statements US-GAAP** (5Y annual + 5Q quarterly) | SEC EDGAR / DART (auto live fetch) |")
    lines.append("| 5 | News Timeline (중립 제외 + 월별 +/- bar chart) | DART/SEC + NewsAPI.org/.ai/Finnhub |")
    lines.append("| 6 | Executive Brief + Thesis List | thesis_list.json (+ implicit thesis if standalone) |")
    lines.append("| 7 | R1 Quant Anchor | stocks.json + risk_limits.json |")
    lines.append("| 8 | R2 Persona Panel + Thesis × Persona Matrix | persona_panel/{ticker}/*.json |")
    lines.append("| 9 | R3 Decision Section | decisions.json + portfolio.json |")
    lines.append("| 10 | (선택) ETF Holdings · Reverse DCF · Subagent Debate | 자동 |")
    lines.append("| 11 | Appendix (용어 사전) | static |")
    lines.append("")

    # ─── 3. Thesis ───────────────────────────────────
    if theses:
        lines.append("## 3. 추출된 Thesis")
        lines.append("")
        if is_implicit:
            sources = sorted(set(t.get("_source", "user_provided") for t in theses))
            lines.append(f"이 분석은 **Implicit Thesis 자동 추출** (v0.5.0)을 활용했습니다 (sources: {', '.join(sources)}).")
            lines.append("")
        lines.append("| ID | Claim | Type | Source |")
        lines.append("|---|---|---|---|")
        for t in theses[:12]:
            claim = t.get("claim", "")[:120]
            t_type = t.get("type", "factual")
            t_src = t.get("_source", "user_provided")
            lines.append(f"| {t.get('claim_id', '?')} | {claim} | {t_type} | {t_src} |")
        lines.append("")

    # ─── 4. 빌드/재빌드 명령어 ─────────────────────────
    lines.append("## 4. 빌드/재빌드 명령어")
    lines.append("")
    rel_dir = pipeline_dir.as_posix()
    lines.append("이 분석을 다시 빌드하려면 (예: 코드 업데이트 후 재생성):")
    lines.append("")
    lines.append("```bash")
    lines.append(f"# v0.5.0 섹션 흐름 적용된 per-stock combined PDF 생성")
    lines.append(f"python3 plugins/report-suite/skills/unified-builder/scripts/build_combined.py \\")
    lines.append(f"  --ticker {primary_ticker} \\")
    lines.append(f"  --meta {rel_dir}/meta.json \\")
    lines.append(f"  --stocks {rel_dir}/stocks.json \\")
    lines.append(f"  --thesis {rel_dir}/thesis_list.json \\")
    lines.append(f"  --eval-dir {rel_dir}/thesis_eval \\")
    lines.append(f"  --persona-aggregate {rel_dir}/persona_panel/{primary_ticker}/aggregate.json \\")
    lines.append(f"  --persona-full {rel_dir}/persona_panel/{primary_ticker} \\")
    lines.append(f"  --persona-aggregates-all {rel_dir}/persona_panel/_all_aggregates.json \\")
    lines.append(f"  --risk-limits {rel_dir}/risk_limits.json \\")
    lines.append(f"  --decisions {rel_dir}/decisions.json \\")
    lines.append(f"  --portfolio {rel_dir}/portfolio.json \\")
    lines.append(f"  --deep-research {rel_dir}/deep_research/{primary_ticker}.json \\")
    lines.append(f"  --output {rel_dir}/reports/combined/01_{primary_ticker}_combined.pdf")
    lines.append("```")
    lines.append("")
    lines.append("부분 재실행 (재무 분석만):")
    lines.append("```bash")
    lines.append(f"# 5년 + 5분기 US GAAP 재무 분석 단독 (디버깅용)")
    lines.append(f"python3 plugins/report-suite/skills/_common/financial_statements_us_gaap.py {primary_ticker} \\")
    lines.append(f"  --output /tmp/{primary_ticker}_fs.json")
    lines.append("```")
    lines.append("")

    # ─── 5. 디렉토리 구조 ─────────────────────────────
    lines.append("## 5. 디렉토리 구조")
    lines.append("")
    lines.append("```")
    lines.append(f"{pipeline_dir.name}/")
    for f in sorted(pipeline_dir.iterdir()):
        if f.name.startswith(".") or f.name.startswith("~$"):
            continue
        if f.is_dir():
            lines.append(f"├── {f.name}/")
            for sub in sorted(f.iterdir())[:5]:
                if sub.name.startswith(".") or sub.name.startswith("~$"):
                    continue
                lines.append(f"│   ├── {sub.name}{'/' if sub.is_dir() else ''}")
            extra = sum(1 for s in f.iterdir() if not s.name.startswith(".") and not s.name.startswith("~$")) - 5
            if extra > 0:
                lines.append(f"│   └── ... (+{extra} more)")
        else:
            lines.append(f"├── {f.name}")
    lines.append("```")
    lines.append("")

    # ─── 6. 생성된 PDF ────────────────────────────────
    if reports:
        lines.append("## 6. 생성된 보고서")
        lines.append("")
        for r in reports:
            lines.append(f"- `{r}`")
        lines.append("")

    # ─── 7. 주의사항 ──────────────────────────────────
    lines.append("## 7. 주의사항 — 데이터 출처 및 한계")
    lines.append("")
    notes = [
        "**Financial Statements (Section 4)**: SEC EDGAR XBRL companyfacts API에서 5년 annual + 5분기 quarterly 자동 fetch. "
        "한국 종목은 DART OpenAPI 사용. K-IFRS 항목은 US GAAP-equivalent로 매핑되며, SG&A/D&A 등 일부 line item은 미지원.",
        "**Material Variance Summary**: 임계값 기반 자동 플래깅 (>$1B 라인 = $50M/5%, $100M-$1B = $25M/10%, <$100M = $5M/15%). "
        "원인 분석은 LLM이 추정한 narrative이므로 10-K Item 7 MD&A 직접 확인 권장.",
        "**News Timeline (Section 5)**: 중립(○) 항목은 KPI에는 카운트되지만 상세 표에서 제외됨. "
        "긍정/부정만 상세 요약 + 월별 +/- bar chart 자동 생성 (종목별 개별).",
        "**Persona Panel (Section 8)**: 13명 페르소나의 verdict는 sector-aware heuristic 또는 LLM 평가 결과. "
        "`_meta.is_mock: true`이면 demo 데이터, 아니면 실제 OpenAI/Gemini 평가.",
    ]
    if is_implicit:
        notes.append(
            "**Implicit Thesis 자동 추출 (v0.5.0)**: 이 분석은 standalone (블로그 글 없음)이므로 implicit thesis가 자동 추출되었습니다. "
            "deep_research의 catalysts → predictive thesis, risks → conditional thesis로 변환됨. "
            "실제 블로거의 1차 분석이 없으므로 narrative 깊이는 제한적."
        )
    notes.extend([
        "**투자 자문 아님**: 본 분석은 paper portfolio simulation 전용. 실제 거래는 절대 자동 실행하지 않음. "
        "모든 verdict는 `[actual]` / `[inference]` / `[assumption]` 태그로 출처 명시."
    ])
    for n in notes:
        lines.append(f"- {n}")
    lines.append("")

    # ─── 8. 자동 생성 정보 ─────────────────────────────
    lines.append("---")
    lines.append("")
    lines.append(f"_이 README는 `plugins/report-suite/skills/readme-generator/scripts/build_instruction_readme.py`로 자동 생성되었습니다._  ")
    lines.append(f"_생성 일시: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}  ·  보고서 빌더 v0.5.0_")
    lines.append("")

    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description="분석별 instruction README 생성기 (v0.5.0)")
    p.add_argument("--pipeline-dir", required=True, help="분석 디렉토리 경로")
    p.add_argument("--output", default="README.md", help="출력 파일명 (default: README.md)")
    args = p.parse_args()

    pipeline_dir = Path(args.pipeline_dir).resolve()
    if not pipeline_dir.exists():
        raise SystemExit(f"분석 디렉토리 없음: {pipeline_dir}")

    md = build_instruction_readme(pipeline_dir)
    out_path = pipeline_dir / args.output
    out_path.write_text(md, encoding="utf-8")
    print(f"Saved: {out_path} ({len(md)} chars, {md.count(chr(10))} lines)")


if __name__ == "__main__":
    main()
