#!/usr/bin/env python3
"""Notion Page Builder — DB row 페이지 본문 + 메인 페이지 hub + 하위 페이지 구성.

이 모듈은 단순 메타데이터 upsert (notion_client.py) 위에서 작동:
- DB row의 페이지 body에 분석 README markdown 작성
- GitHub raw URL을 통해 PDF 외부 임베드
- 메인 페이지에 README 요약 + version history + DB linked view 작성
- 하위 페이지 2개 (README 전체 + Methodology 상세) 자동 생성

두 모드 지원:
- Direct API (NOTION_TOKEN 설정 시): REST API로 page.children blocks 추가
- MCP payload mode (default): JSON payload를 emit, 호출자(Cowork/Claude Code)가 MCP 호출

CLI:
    python3 page_builder.py write-row --ticker LNG --readme-path ... [--pdf-github-url ...]
    python3 page_builder.py build-hub --main-page-id ...
    python3 page_builder.py build-subpages --main-page-id ...
    python3 page_builder.py full-rebuild --main-page-id ...
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Re-use env reader from notion_client
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR.parent.parent.parent / "scripts"))
from notion_client import _read_env_key, get_token as _notion_token, get_data_source_id


MAIN_PAGE_ID_DEFAULT = "2d402c77-e2c9-800b-ba24-c9d354d4c0aa"
DB_DATA_SOURCE_ID = "7aa5488f-99e9-4ca0-afef-4ac110435597"


def get_github_owner() -> str:
    return _read_env_key("GITHUB_OWNER") or "DrugnSafety"


def get_github_repo() -> str:
    return _read_env_key("GITHUB_REPO") or "stock-analysis"


# ============== Markdown 변환 ==============

def build_blog_source_section(blog_info: dict, theses: list = None) -> str:
    """Render blog source info as Notion markdown section.

    Used for blogger-driven analyses (not standalone).
    """
    if not blog_info or not blog_info.get("blog_url"):
        return ""

    parts = ["## 📰 출처 블로그 글 정보\n"]
    if blog_info.get("blog_title"):
        parts.append(f"- **글 제목**: {blog_info['blog_title']}")
    if blog_info.get("blog_author"):
        parts.append(f"- **작성자**: {blog_info['blog_author']}")
    if blog_info.get("blog_published_at"):
        parts.append(f"- **발행일**: {blog_info['blog_published_at']}")
    if blog_info.get("blog_category"):
        parts.append(f"- **카테고리**: {blog_info['blog_category']}")
    if blog_info.get("blog_url"):
        parts.append(f"- **원문 URL**: [{blog_info['blog_url']}]({blog_info['blog_url']})")
    if blog_info.get("core_thesis"):
        parts.append(f"\n### 핵심 주장 (Core Thesis)\n\n> {blog_info['core_thesis']}\n")
    if blog_info.get("key_facts"):
        parts.append(f"\n### 주요 팩트 (Key Facts)\n")
        for i, fact in enumerate(blog_info["key_facts"][:8], 1):
            parts.append(f"{i}. {fact}")

    # Top thesis preview
    if theses:
        parts.append(f"\n### 추출된 Thesis ({len(theses)}개)\n")
        for t in theses[:6]:
            cid = t.get("claim_id", "?")
            claim = (t.get("claim") or "")[:160]
            t_type = t.get("type", "")
            parts.append(f"- **{cid}** *(type: {t_type})*: {claim}")
        if len(theses) > 6:
            parts.append(f"- _… and {len(theses) - 6} more theses_")

    return "\n".join(parts) + "\n\n---\n"


def readme_to_notion_md(readme_path: Path, pdf_github_url: Optional[str] = None,
                        blog_info: Optional[dict] = None,
                        theses: Optional[list] = None) -> str:
    """분석 README.md → Notion-flavored markdown (페이지 body 용).

    핵심 섹션만 추출 + PDF 임베드 + 블로그 정보 + thesis preview.
    """
    if not readme_path.exists():
        return ""

    content = readme_path.read_text(encoding="utf-8")

    # PDF embed at top if URL provided
    pdf_block = ""
    if pdf_github_url:
        # Notion expects raw URL for file embed
        raw_url = pdf_github_url.replace("/blob/", "/raw/")
        pdf_block = f"\n## 📄 통합 PDF 보고서\n\n[PDF 직접 열기]({pdf_github_url})  \n(또는 raw 다운로드: [{raw_url.split('/')[-1]}]({raw_url}))\n\n"

    # Blog source section
    blog_section = build_blog_source_section(blog_info or {}, theses or [])

    # Insert blocks after first heading (before Section 1)
    lines = content.splitlines()
    out_lines = []
    inserted = False
    for line in lines:
        out_lines.append(line)
        if not inserted and line.startswith("## 1. "):
            # Insert PDF + blog block before Section 1
            insert_block = (pdf_block + blog_section).rstrip()
            if insert_block:
                out_lines.insert(-1, insert_block)
            inserted = True

    if not inserted:
        # Append at end if no Section 1 found
        tail = (pdf_block + blog_section).rstrip()
        if tail:
            out_lines.append(tail)

    return "\n".join(out_lines)


# ============== MCP payload mode ==============

def emit_row_page_payload(ticker: str, readme_path: Path,
                          pdf_github_url: Optional[str] = None,
                          output_path: Optional[Path] = None) -> dict:
    """Emit MCP payload to update a DB row's page body.

    Caller (Cowork/Claude Code) must invoke MCP notion-update-page with this.
    """
    md = readme_to_notion_md(readme_path, pdf_github_url=pdf_github_url)
    payload = {
        "ticker": ticker,
        "data_source_id": DB_DATA_SOURCE_ID,
        "content_markdown": md,
        "pdf_github_url": pdf_github_url,
        "_instructions": (
            "Find page by Ticker title in DB, then invoke notion-update-page "
            "with this page's id and the content_markdown."
        )
    }
    if output_path:
        output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


def emit_hub_page_payload(main_page_id: str, repo_url: str,
                          output_path: Optional[Path] = None) -> dict:
    """Emit MCP payload for main hub page content."""
    md = build_hub_page_markdown(repo_url)
    payload = {
        "main_page_id": main_page_id,
        "content_markdown": md,
        "_instructions": "Invoke notion-update-page with main_page_id and content_markdown."
    }
    if output_path:
        output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


def emit_subpages_payload(main_page_id: str, readme_path: Path,
                          methodology_md: str,
                          output_path: Optional[Path] = None) -> dict:
    """Emit MCP payload for two sub-pages under main."""
    readme_content = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    payload = {
        "main_page_id": main_page_id,
        "subpages": [
            {
                "title": "📘 README — 시스템 전체 소개",
                "icon": "📘",
                "content": readme_content,
            },
            {
                "title": "🔬 분석 Methodology — 8단계 파이프라인 + 13명 페르소나 + 5Y/5Q 재무 분석",
                "icon": "🔬",
                "content": methodology_md,
            },
        ],
        "_instructions": "Invoke notion-create-pages with main_page_id as parent and these subpages."
    }
    if output_path:
        output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


# ============== 콘텐츠 빌더 ==============

def build_hub_page_markdown(repo_url: str) -> str:
    """메인 페이지 hub 콘텐츠 — README 요약 + version + DB view."""
    return f"""# 📊 주식분석 by Claude — Hub

> 네이버 블로그 (메르·의교창·DaeGurr 등 8명) 또는 사용자 지정 종목에 대해 **13명 페르소나 패널 + 4-Analyst + Risk·Portfolio Manager + Backtester** 통합 분석을 수행하고 **Deep Research 형식의 단일 통합 PDF 보고서**를 자동 생성하는 시스템입니다.

**현재 버전**: v0.5.0 (2026-05-11)  ·  **GitHub Repo**: [{repo_url.replace("https://github.com/", "")}]({repo_url})

---

## ✨ 핵심 기능

- **13명 legendary 투자자 패널**: Buffett · Munger · Lynch · Wood · Burry · Taleb · Graham · Ackman · Pabrai · Fisher · Jhunjhunwala · Druckenmiller · Damodaran
- **4-Analyst 평가**: Macro · Industry · Empirical · Counter-thesis
- **5년 + 5분기 US-GAAP 재무 분석** (SEC EDGAR + DART)
- **Implicit Thesis 자동 추출** (standalone 분석용)
- **News Timeline** — 중립 제외 + 월별 +/- bar chart
- **Multi-model arena** (Claude + OpenAI + Gemini 합의)
- **GitHub + Notion 자동 sync** (분석 완료 시 post-build hook)

---

## 📜 Version History

| 버전 | 일자 | 핵심 변경 |
|---|---|---|
| **v0.5.0** | 2026-05-11 | Phase 1 Deep Research 승격 · Phase 2 5Y+5Q US-GAAP 재무 · Phase 3 Timeline 개선 · Phase 4 Matrix 정상화 · Phase 5 Implicit Thesis · GitHub/Notion sync |
| v0.4.0 | 2026-04-30 | ETF Holdings · Reverse DCF · Subagent Debate · 한글 PDF |
| v0.3.0 | 2026-04 초 | 13명 페르소나 + 4-Analyst · Deep Research · 한국 calibration |
| v0.2.0 | 2026-03 ~ 4 초 | Multi-model arena · Backtester · Trade engine |
| v0.1.0 | 2026-02 ~ 3 초 | 8명 블로거 registry · DART · R1/R2/R3 builder |

---

## 📚 하위 페이지

- 📘 **[README — 시스템 전체 소개]** — 셋업, 사용법, plugin 매트릭스, CLI 명령어
- 🔬 **[분석 Methodology]** — 8단계 파이프라인, 13명 페르소나 철학, 5Y/5Q US-GAAP 재무 분석, Implicit Thesis 추출 등 상세

---

## 📋 분석 이력 (📊 주식 분석 Hub DB)

아래 DB는 모든 분석 결과를 종목 단위로 정리한 것입니다. 각 row를 클릭하면 분석 상세 페이지로 이동합니다.

(아래에 linked database view를 인라인으로 표시 — Notion에서 직접 view 추가 후 정렬·필터 설정 가능)

---

## 🔗 관련 링크

- **GitHub Private Repo**: {repo_url}
- **로컬 저장소**: `~/Documents/Claude/Projects/주식 분석/`
- **분석 결과 디렉토리**: `.analysis-log/standalone/*` 또는 `.analysis-log/bloggers/*/*/`

---

## ⚠️ 면책 사항

본 시스템은 **paper portfolio simulation** 전용입니다. 실제 거래는 절대 자동 실행하지 않습니다. 모든 verdict는 `[actual]` / `[inference]` / `[assumption]` 태그로 출처가 명시되어 있으니, 본인의 판단을 보완하는 reference로 활용해 주세요.
"""


def build_methodology_markdown() -> str:
    """분석 Methodology 상세 페이지."""
    return """# 🔬 분석 Methodology

본 페이지는 주식 분석 시스템의 분석 방법론을 단계별로 상세히 설명합니다. 시스템이 어떻게 데이터를 수집하고, 어떻게 13명의 legendary 투자자 lens로 평가하며, 어떻게 최종 결정에 도달하는지 투명하게 공개합니다.

---

## 1. 8단계 분석 파이프라인

### Stage 1 — 입력 수집
**(a) 블로그 분석**: 네이버 블로그 URL을 입력받아 본문 + 메타데이터 수집
**(b) Standalone 분석**: 사용자가 직접 ticker만 지정 — implicit thesis 자동 추출

### Stage 2 — Thesis 추출 (블로그 분석만)
LLM (gpt-5.5 또는 gemini-3.1)이 블로그 본문에서 핵심 주장 6-12개를 추출. 각 thesis는 `factual / predictive / normative / conditional` 4가지 type 중 하나로 분류.

### Stage 3 — 종목 식별
본문에 명시된 (explicit) 종목 + 본문 컨텍스트에서 유추되는 (implicit) 종목을 식별. 글로벌 거래소 ticker 형식으로 표준화.

### Stage 4 — 4-Analyst 평가
각 thesis를 4명의 analyst가 독립 평가:
- **Macro Analyst**: 거시·정책·금리 영향
- **Industry Analyst**: 산업 구조·경쟁 동학
- **Empirical Analyst**: 정량 데이터·역사적 사례 검증
- **Counter-thesis Devil's Advocate**: 반박 가능성·논리적 약점

### Stage 5 — 시장 데이터 fetch (live)
**yfinance**로 종목별 현재가·시가총액·52주 high/low·P/E·beta·변동성 등 fetch. **반드시 live 호출** — LLM placeholder 절대 사용 금지.

### Stage 6 — 13명 페르소나 패널
각 종목을 13명의 legendary 투자자 lens로 평가:

| 분류 | 페르소나 | 핵심 framework |
|---|---|---|
| Value | Warren Buffett | Margin of safety, durable moat |
| Value | Charlie Munger | Multidisciplinary, mental models |
| Value | Benjamin Graham | NCAV, deep value |
| Value | Mohnish Pabrai | Spawner thesis, contrarian |
| Growth | Peter Lynch | PEG, 10-bagger |
| Growth | Cathie Wood | Disruption, exponential tech |
| Growth | Phil Fisher | R&D innovation, scuttlebutt |
| Macro | Stanley Druckenmiller | Top-down macro, leveraged conviction |
| Risk | Nassim Taleb | Antifragility, black swan |
| Contrarian | Michael Burry | Deep value contrarian |
| Activist | Bill Ackman | Capital allocation activism |
| Emerging | Rakesh Jhunjhunwala | India + global bull markets |
| Valuation | Aswath Damodaran | Reverse DCF, story-numbers integrity |

각 페르소나는:
- 5단계 분석 시퀀스 통과 (Circle of competence → ... → Verdict)
- `lean_bullish / neutral / lean_bearish` verdict + confidence (0~1) 산출
- `thesis_lens_applications` (모든 thesis에 대한 stance) 필수 출력 — v0.4.0+

### Stage 7 — Risk-adjusted sizing
**Risk Manager**: 60일 rolling 변동성 기반 `vol_multiplier` (저변동성 1.25× / 고변동성 0.50×). 활성 포지션과의 상관관계 multiplier 결합.

### Stage 8 — Portfolio Decision
**Portfolio Manager**: signal_score = (Bull - Bear) / N. signal × confidence × position_limit으로 BUY / HOLD / SELL + 수량 결정.

---

## 2. 재무 분석 — 5년 Annual + 5분기 Quarterly (US GAAP)

v0.5.0에서 추가된 `financial_statements_us_gaap.py` 모듈은 **모든 plugin agent의 재무 anchor 의무 사용** 표준입니다.

### 데이터 소스
- **미국 종목**: SEC EDGAR XBRL companyfacts API (10-K + 10-Q)
- **한국 종목**: DART OpenAPI → US GAAP-equivalent line item 매핑

### Income Statement (ASC 220)
5년 P&L + 직전 연도 대비 variance ($ 및 %). FY2025 vs FY2024 같은 period-over-period 비교가 기본.

### Balance Sheet (ASC 210)
5년 연말 snapshot. Current/Non-current asset/liability + Stockholders' Equity. Net Debt, Current Ratio 등 핵심 지표 자동 산출.

### Cash Flow (ASC 230 간접법)
OCF, CapEx, FCF, Investing/Financing activities. FCF Margin과 CapEx Intensity 5년 추이.

### Material Variance Summary
임계값 기반 자동 플래깅:
- **>$1B 라인**: $50M 또는 5% 변동 시 material
- **$100M-$1B**: $25M 또는 10%
- **<$100M**: $5M 또는 15%

각 항목에 favorable / unfavorable / neutral 방향 + driver 추정.

### Quarterly (최근 5분기)
10-Q filings에서 3-month duration P&L + BS snapshot 추출. Q4는 10-K - 9M YTD로 derive. 분기 변동성 시그널 (예: 영업이익 흑전·적전) 캡처.

---

## 3. Implicit Thesis 자동 추출 (Phase 5, v0.5.0)

블로그 글 없이 ticker만으로 분석할 때 standalone 모드가 작동합니다. `implicit_thesis_extractor.py`가 다음 소스를 thesis로 변환:

| Source | Thesis type | 예시 |
|---|---|---|
| `deep_research.catalysts` | predictive | "Centurion Stage 3 가동 시 valuation reprice" |
| `deep_research.risks` | conditional | "Henry Hub 가격 상승 시 마진 압박" |
| `industry.market_size` (CAGR) | factual | "산업 CAGR 12% — macro tailwind" |
| `financials.fcf` trend | factual | "FCF 음전환 — capital 사이클 trough" |
| Sector template | normative | "Capital allocation 정책 적정성" |

자동 추출된 thesis는 13명 페르소나 패널의 `thesis_lens_applications` 입력으로 사용되어, **standalone 분석에서도 Thesis × Persona Matrix가 의미있게 작동**합니다.

---

## 4. News Timeline (v0.5.0 개선)

종목별 1년 뉴스·공시 timeline:
- **데이터 소스 (3-source)**: DART (한국) · SEC EDGAR (미국) · NewsAPI.org / NewsAPI.ai (Event Registry) / Finnhub
- **중립 필터링**: ○ 항목은 KPI 카운트만, 상세 표에서 제외
- **상세 요약**: 긍정/부정 항목은 `expand_summary=True`로 1.5배 길이 확장
- **월별 +/- bar chart**: matplotlib base64 PNG로 종목별 개별 임베드

---

## 5. Multi-model Arena

선택적으로 활성화. 동일 입력을 OpenAI gpt-5.5 + Gemini 3.1 + Claude에 병렬 분배 후 결과를 비교:
- Union of tickers (각 모델이 다르게 식별한 종목 통합)
- Verdict 분포 (모델 간 합의 vs 이견)
- Ticker별 합의 점수 (cross-model conviction)

비용 cap: `ARENA_MAX_COST_USD=2.00` (`.env` 설정)

---

## 6. Backtester

과거 verdict에 대해 entry/exit price를 yfinance로 fetch한 후 사후 수익률 계산:
- Multi-horizon: 1m / 3m / 6m / 12m
- Benchmark: KOSPI(^KS11) / SPY 대비 alpha
- Persona별 적중률 (어떤 페르소나가 어떤 sector에 강한지)
- Confidence calibration (높은 confidence가 실제로 적중률에 반영되는지)

---

## 7. Anti-Hallucination 표준

모든 verdict의 근거에 출처 태그 필수:
- `[actual]` — SEC EDGAR / DART / yfinance 실측 데이터
- `[inference]` — 실측 데이터로부터의 합리적 추정
- `[assumption]` — 명시적 가정 (예: "가스 가격 $3/MMBtu 유지 가정")
- `[derived]` — Reverse DCF 등 계산 도출 값
- `[unavailable]` — 데이터 없음 명시

페르소나 평가에서 LLM이 임의로 만든 숫자는 절대 금지. 모든 정량 데이터는 위 5가지 태그 중 하나를 가져야 함.

---

## 8. 보고서 섹션 흐름

per-stock combined PDF (v0.5.0):

```
1.  Cover
2.  Company Intro
3.  Deep Research (산업 + 재무 + 카탈리스트/리스크)
4.  Financial Statements US-GAAP (5Y annual + 5Q quarterly + variance)
5.  News Timeline (중립 제외 + 월별 +/- bar chart)
6.  Executive Brief + Thesis List (implicit thesis 자동 보강)
7.  R1 Quant Anchor
8.  R2 Persona Panel (Thesis × Persona Matrix)
9.  R3 Decision Section
10. (선택) ETF Holdings · Reverse DCF · Subagent Debate
11. Appendix
```

---

## 9. GitHub + Notion 자동 sync

분석 완료 시 `build_combined.py`의 post-build hook이 자동으로:
1. **GitHub** (private repo: DrugnSafety/stock-analysis): 메타데이터 JSON + README + PDF push
2. **Notion** (📊 주식 분석 Hub DB): 종목별 row upsert + 페이지 본문 markdown 작성

비활성화: `DISABLE_SYNC=1 python3 build_combined.py ...`

---

## 10. 한계 및 주의사항

### 모델 한계
- LLM (gpt-5.5/gemini-3.1)이 자유 작문하지 않도록 강한 prompt + 데이터 태깅 강제했지만, narrative 일부는 추정 포함
- Phase 5 implicit thesis는 sector-aware heuristic — 실제 블로거의 1차 분석 깊이엔 미치지 않음

### 데이터 한계
- DART는 K-IFRS 기준 — US GAAP 매핑 시 일부 line item (SG&A, D&A 등) 불완전
- SEC EDGAR는 XBRL concept naming이 회사마다 다름 — fetcher가 fallback chain으로 처리
- 뉴스 sentiment는 keyword-based classifier — LLM 정밀도엔 미치지 않음

### 사용자 책임
본 시스템 출력은 **투자 자문이 아닙니다**. 모든 final 투자 결정은 사용자 본인이 직접 검토 후 내려야 합니다.
"""


# ============== CLI ==============

def main():
    p = argparse.ArgumentParser(description="Notion Page Builder")
    sub = p.add_subparsers(dest="cmd", required=True)

    # write-row
    pw = sub.add_parser("write-row", help="DB row 페이지 본문에 README 작성")
    pw.add_argument("--ticker", required=True)
    pw.add_argument("--readme-path", required=True)
    pw.add_argument("--pdf-github-url", default=None)
    pw.add_argument("--output-mcp-payload", default="/tmp/notion_row_payload.json")

    # build-hub
    ph = sub.add_parser("build-hub", help="메인 페이지 hub 콘텐츠 생성")
    ph.add_argument("--main-page-id", default=MAIN_PAGE_ID_DEFAULT)
    ph.add_argument("--output-mcp-payload", default="/tmp/notion_hub_payload.json")

    # build-subpages
    ps = sub.add_parser("build-subpages", help="하위 페이지 2개 (README + Methodology)")
    ps.add_argument("--main-page-id", default=MAIN_PAGE_ID_DEFAULT)
    ps.add_argument("--readme-path", default="README.md")
    ps.add_argument("--output-mcp-payload", default="/tmp/notion_subpages_payload.json")

    # full-rebuild
    pf = sub.add_parser("full-rebuild", help="전체 재구성 (hub + subpages + 모든 row 페이지)")
    pf.add_argument("--main-page-id", default=MAIN_PAGE_ID_DEFAULT)
    pf.add_argument("--readme-path", default="README.md")
    pf.add_argument("--analysis-log-dir", default=".analysis-log")
    pf.add_argument("--output-dir", default="/tmp/notion_full_rebuild")

    args = p.parse_args()

    if args.cmd == "write-row":
        payload = emit_row_page_payload(
            args.ticker, Path(args.readme_path),
            pdf_github_url=args.pdf_github_url,
            output_path=Path(args.output_mcp_payload)
        )
        print(f"Saved row payload: {args.output_mcp_payload}")
        print(f"  ticker: {payload['ticker']}, content_length: {len(payload['content_markdown'])}")

    elif args.cmd == "build-hub":
        owner = get_github_owner()
        repo = get_github_repo()
        repo_url = f"https://github.com/{owner}/{repo}"
        payload = emit_hub_page_payload(args.main_page_id, repo_url, Path(args.output_mcp_payload))
        print(f"Saved hub payload: {args.output_mcp_payload}")

    elif args.cmd == "build-subpages":
        meth = build_methodology_markdown()
        payload = emit_subpages_payload(
            args.main_page_id, Path(args.readme_path),
            methodology_md=meth,
            output_path=Path(args.output_mcp_payload)
        )
        print(f"Saved subpages payload: {args.output_mcp_payload}")

    elif args.cmd == "full-rebuild":
        out_dir = Path(args.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        # hub
        owner = get_github_owner()
        repo = get_github_repo()
        repo_url = f"https://github.com/{owner}/{repo}"
        emit_hub_page_payload(args.main_page_id, repo_url, out_dir / "hub.json")
        # subpages
        emit_subpages_payload(
            args.main_page_id, Path(args.readme_path),
            methodology_md=build_methodology_markdown(),
            output_path=out_dir / "subpages.json"
        )
        # row pages
        analysis_dir = Path(args.analysis_log_dir)
        rows = []
        for d in list((analysis_dir / "standalone").iterdir()) + list((analysis_dir / "bloggers").rglob("*/")):
            if (d / "README.md").exists() and (d / "meta.json").exists():
                meta = json.loads((d / "meta.json").read_text())
                # Get primary ticker
                ticker = meta.get("ticker")
                if not ticker and (d / "stocks.json").exists():
                    try:
                        s = json.loads((d / "stocks.json").read_text())
                        if isinstance(s, list) and s:
                            ticker = s[0].get("ticker")
                    except:
                        pass
                if ticker:
                    pdf_files = list((d / "reports").rglob("*combined*.pdf")) if (d / "reports").exists() else []
                    pdf_url = None
                    if pdf_files:
                        rel = pdf_files[0].relative_to(Path.cwd())
                        pdf_url = f"https://github.com/{owner}/{repo}/blob/main/{rel.as_posix()}"
                    emit_row_page_payload(
                        ticker, d / "README.md",
                        pdf_github_url=pdf_url,
                        output_path=out_dir / f"row_{ticker.replace('.', '_')}.json"
                    )
                    rows.append(ticker)
        print(f"Full rebuild payloads saved to {out_dir}/")
        print(f"  hub.json + subpages.json + {len(rows)} row payloads")


if __name__ == "__main__":
    main()
