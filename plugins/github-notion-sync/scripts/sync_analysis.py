"""분석 디렉토리 → GitHub + Notion 동시 동기화 (sync orchestrator).

사용법:
    python3 sync_analysis.py \
        --pipeline-dir .analysis-log/standalone/2026-05-11_LNG_Cheniere_Energy \
        --ticker LNG

자동 호출 (post-build hook):
    build_combined.py가 PDF 생성 완료 후 자동 호출.
    실패 시 graceful skip — 분석 결과는 local에 유지됨.

동기화 내용:
1. GitHub repo (자동 생성 → push):
   - meta.json
   - thesis_list.json
   - stocks.json (market_data 포함)
   - decisions.json
   - portfolio.json
   - risk_limits.json
   - persona_panel/{ticker}/aggregate.json
   - deep_research/{ticker}.json (있으면)
   - README.md (분석별 instruction)
   - reports/combined/*.pdf  (PDF는 binary로 push)

2. Notion DB row (자동 생성 또는 업데이트):
   - Ticker, Company, Date, Sector
   - Verdict, Signal Score, Avg Confidence
   - Bull/Neutral/Bear counts
   - GitHub URL, PDF Report URL, Local Path
   - Top Concerns (universal_concerns에서 추출)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Local imports
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from github_client import (
    ensure_repo, push_file, push_text, get_owner, get_repo, get_token as gh_token,
    get_status as gh_status, get_file_sha,
)
from notion_client import (
    upsert_row_direct, emit_mcp_payload, get_token as notion_token,
    get_data_source_id, get_status as notion_status, normalize_sector,
)


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def extract_blog_info(meta: dict) -> dict:
    """Extract blog source info from meta.json — keys vary across analyses.

    Standard keys (priority order):
      blog_url / url
      blog_title / title / post_title_orig
      blog_author / blogger / blogger_kr / blogger_name / blogger_korean
      blog_published_at / published_at / publish_date / post_date / date
      core_thesis / thesis_summary / summary
      key_facts (list)
      blog_category / category / topic / theme
    """
    def first(*keys):
        for k in keys:
            v = meta.get(k)
            if v:
                return v
        return None

    raw_author = first("blog_author", "blogger_kr", "blogger_name", "blogger_korean", "blogger")
    # blogger 필드가 dict로 저장된 경우 nickname/blog_id 추출
    if isinstance(raw_author, dict):
        blog_author = (raw_author.get("blog_author") or raw_author.get("nickname")
                       or raw_author.get("name") or raw_author.get("blog_id") or "")
    else:
        blog_author = raw_author or ""
    return {
        "blog_url": first("blog_url", "url"),
        "blog_title": first("blog_title", "title", "post_title_orig"),
        "blog_author": str(blog_author)[:100],
        "blog_published_at": first("blog_published_at", "published_at", "publish_date", "post_date", "date"),
        "core_thesis": first("core_thesis", "thesis_summary", "summary"),
        "key_facts": meta.get("key_facts") or [],
        "blog_category": first("blog_category", "category", "topic", "theme"),
    }


def extract_metadata(pipeline_dir: Path, ticker: str) -> dict:
    """Read all relevant files and assemble Notion + GitHub metadata payload."""
    meta = _read_json(pipeline_dir / "meta.json")
    stocks_raw = _read_json(pipeline_dir / "stocks.json")
    stocks = stocks_raw if isinstance(stocks_raw, list) else stocks_raw.get("stocks", []) or []
    thesis_raw = _read_json(pipeline_dir / "thesis_list.json")
    theses = thesis_raw.get("theses", []) if isinstance(thesis_raw, dict) else (thesis_raw if isinstance(thesis_raw, list) else [])
    decisions = _read_json(pipeline_dir / "decisions.json").get("decisions", [])
    agg = _read_json(pipeline_dir / "persona_panel" / ticker / "aggregate.json")
    blog_info = extract_blog_info(meta)

    # Stock data for this ticker
    stock = next((s for s in stocks if s.get("ticker") == ticker), {})

    # Determine analysis type
    parts = pipeline_dir.resolve().parts
    if "standalone" in parts:
        atype = "standalone"
        blogger = ""
    elif "bloggers" in parts:
        atype = "blogger"
        idx = parts.index("bloggers")
        blogger = parts[idx + 1] if idx + 1 < len(parts) else ""
    else:
        atype = "standalone"
        blogger = ""

    # Verdict distribution
    vd = agg.get("verdict_distribution", {})
    def vc(k):
        v = vd.get(k, {})
        return v.get("count", 0) if isinstance(v, dict) else (v or 0)
    bull = vc("lean_bullish")
    neut = vc("neutral")
    bear = vc("lean_bearish")
    n_personas = agg.get("n_personas") or (bull + neut + bear)

    # Signal score
    signal = (bull - bear) / max(n_personas, 1) if n_personas else 0

    # Average confidence
    avg_conf = agg.get("average_confidence") or agg.get("avg_confidence") or 0

    # Top concerns
    universal = agg.get("universal_concerns", [])
    # universal_concerns 요소가 dict({"theme": ...})이거나 str일 수 있음 — 둘 다 지원
    def _concern_label(c):
        if isinstance(c, dict):
            return c.get("theme") or c.get("label") or c.get("description") or ""
        if isinstance(c, str):
            return c
        return ""
    top_concerns_text = " · ".join(_concern_label(c) for c in universal[:3]) if universal else ""

    # Decision
    decision = "hold"
    for d in decisions:
        if d.get("ticker") == ticker:
            decision = d.get("action", "hold").lower()
            break

    # Implicit thesis detection
    is_implicit = any(
        t.get("_source", "") in ("catalyst", "risk", "macro", "industry", "financial", "sector_template")
        for t in theses
    )

    # Aggregate top verdict (mode-style)
    if bull > max(neut, bear):
        top_verdict = "lean_bullish"
    elif bear > max(bull, neut):
        top_verdict = "lean_bearish"
    else:
        top_verdict = "neutral"

    # Company name
    company = (meta.get("company_kr") or meta.get("company_en") or meta.get("company")
               or stock.get("kr_name") or stock.get("name") or ticker)

    # Date
    date_str = (meta.get("analyzed_at") or meta.get("blog_published_at")
                or meta.get("scraped_at") or pipeline_dir.name[:10])
    if "T" in date_str:
        date_str = date_str[:10]

    # Sector
    sector = (meta.get("sector") or stock.get("sector") or "Other")

    # GitHub URL
    gh_owner = get_owner()
    gh_repo = get_repo()
    rel_dir = pipeline_dir.as_posix().replace(str(Path.cwd()) + "/", "")
    gh_url = f"https://github.com/{gh_owner}/{gh_repo}/tree/main/{rel_dir}" if gh_owner else ""

    # PDF report — ticker-specific PDF matching (ticker가 파일명에 포함된 것 우선)
    pdf_url = ""
    pdf_files = sorted((pipeline_dir / "reports").rglob("*combined*.pdf")) if (pipeline_dir / "reports").exists() else []
    matched_pdf = None
    if pdf_files:
        # 1) ticker 정확히 매칭 (e.g., "_FCX_", "FCX.pdf")
        t_safe = ticker.replace(".", "_").replace("/", "_")
        for p in pdf_files:
            stem = p.stem
            if f"_{ticker}_" in stem or stem.endswith(f"_{ticker}") or f"_{t_safe}_" in stem:
                matched_pdf = p
                break
        # 2) Fallback: 첫 PDF
        if matched_pdf is None:
            matched_pdf = pdf_files[0]
    if matched_pdf and gh_owner:
        rel_pdf = matched_pdf.as_posix().replace(str(Path.cwd()) + "/", "")
        pdf_url = f"https://github.com/{gh_owner}/{gh_repo}/blob/main/{rel_pdf}"

    # Better blogger name if available
    if blog_info["blog_author"]:
        blogger = blog_info["blog_author"]

    return {
        "Ticker": ticker,
        "Company": str(company)[:200],
        "Date": date_str,
        "Sector": normalize_sector(str(sector)),
        "Analysis Type": atype,
        "Blogger": str(blogger)[:100],
        "Verdict": top_verdict,
        "Signal Score": round(signal, 3),
        "Avg Confidence": round(avg_conf, 3),
        "Decision": decision,
        "Bull": bull,
        "Neutral": neut,
        "Bear": bear,
        "N Thesis": len(theses),
        "Implicit Thesis": is_implicit,
        "Top Concerns": top_concerns_text[:500],
        "GitHub URL": gh_url,
        "PDF Report": pdf_url,
        "Local Path": rel_dir[:500],
        "_meta": meta,
        "_pdf_files": [str(p) for p in pdf_files],
        "_blog_info": blog_info,
        "_theses": theses,
    }


# Files to push to GitHub
DEFAULT_PUSHABLE_FILES = [
    "meta.json",
    "stocks.json",
    "thesis_list.json",
    "decisions.json",
    "portfolio.json",
    "risk_limits.json",
    "README.md",
]


def sync_to_github(pipeline_dir: Path, ticker: str, payload: dict, skip_pdf: bool = False) -> dict:
    """Push analysis files to GitHub. Idempotent — updates existing files.

    Args:
        skip_pdf: If True, skip PDF push (much faster for bulk backfill).
                  PDFs can be ~500KB each — multiple PDFs slow batch sync.
    """
    if not gh_token():
        return {"status": "skipped", "reason": "GITHUB_TOKEN not set in .env — github sync disabled"}

    try:
        repo_info = ensure_repo()
    except Exception as e:
        return {"status": "error", "reason": f"ensure_repo failed: {e}"}

    pushed = []
    rel_dir = pipeline_dir.resolve().as_posix().replace(str(Path.cwd().resolve()) + "/", "")
    commit_msg = f"sync: {ticker} ({payload.get('Date', 'n/a')}) — Verdict {payload.get('Verdict')}, Signal {payload.get('Signal Score')}"

    # 1. Core JSON files + README
    for fname in DEFAULT_PUSHABLE_FILES:
        local = pipeline_dir / fname
        if local.exists():
            try:
                repo_path = f"{rel_dir}/{fname}"
                push_file(local, repo_path, commit_msg)
                pushed.append(fname)
            except Exception as e:
                print(f"[sync_github] push failed for {fname}: {e}")

    # 2. persona_panel aggregate
    agg_path = pipeline_dir / "persona_panel" / ticker / "aggregate.json"
    if agg_path.exists():
        try:
            push_file(agg_path, f"{rel_dir}/persona_panel/{ticker}/aggregate.json", commit_msg)
            pushed.append(f"persona_panel/{ticker}/aggregate.json")
        except Exception as e:
            print(f"[sync_github] persona aggregate push failed: {e}")

    # 3. deep_research
    dr_path = pipeline_dir / "deep_research" / f"{ticker}.json"
    if dr_path.exists():
        try:
            push_file(dr_path, f"{rel_dir}/deep_research/{ticker}.json", commit_msg)
            pushed.append(f"deep_research/{ticker}.json")
        except Exception as e:
            print(f"[sync_github] deep_research push failed: {e}")

    # 4. PDF reports (binary) — slowest step, optional skip
    if skip_pdf:
        print(f"[sync_github] PDF push skipped (skip_pdf=True)")
    else:
        for pdf_local in payload.get("_pdf_files", []):
            pdf_p = Path(pdf_local)
            if pdf_p.exists():
                try:
                    rel_pdf = pdf_p.resolve().as_posix().replace(str(Path.cwd().resolve()) + "/", "")
                    push_file(pdf_p, rel_pdf, commit_msg)
                    pushed.append(rel_pdf)
                except Exception as e:
                    print(f"[sync_github] PDF push failed for {pdf_p.name}: {e}")

    return {
        "status": "ok",
        "repo": repo_info.get("html_url"),
        "pushed_count": len(pushed),
        "pushed_files": pushed[:10],  # cap log
    }


def sync_to_notion(payload: dict) -> dict:
    """Upsert row in Notion DB. Uses direct API if NOTION_TOKEN set, else emit MCP payload."""
    if not get_data_source_id():
        return {"status": "skipped", "reason": "NOTION_DATA_SOURCE_ID not set in .env"}

    # Strip internal fields
    clean = {k: v for k, v in payload.items() if not k.startswith("_")}

    if notion_token():
        try:
            result = upsert_row_direct(clean)
            return {"status": "ok", "mode": "direct_api", **result}
        except Exception as e:
            return {"status": "error", "reason": f"direct upsert failed: {e}"}
    else:
        # MCP mode — emit payload for caller to invoke MCP tools
        try:
            mcp_payload_path = Path("/tmp/notion_sync_payload.json")
            mcp_payload = emit_mcp_payload(clean, mcp_payload_path)
            return {
                "status": "mcp_payload_ready",
                "mode": "mcp",
                "payload_path": str(mcp_payload_path),
                "instructions": "Caller must invoke MCP notion-create-pages or notion-update-page with this payload.",
                "data_source_id": mcp_payload["data_source_id"],
            }
        except Exception as e:
            return {"status": "error", "reason": f"MCP payload emit failed: {e}"}


def _repo_path_from_url(url: str) -> Optional[str]:
    """https://github.com/{owner}/{repo}/(tree|blob)/main/{path} → {path}."""
    if not url:
        return None
    for sep in ("/blob/main/", "/tree/main/"):
        if sep in url:
            return url.split(sep, 1)[1]
    return None


def verify_remote_links(payload: dict) -> dict:
    """Confirm the GitHub URLs embedded in the Notion payload resolve to real
    remote objects BEFORE those links are written to Notion.

    Root-cause guard (2026-07-27): a build run with DISABLE_SYNC=1 skips the
    GitHub push, but the payload still carries GitHub/PDF URLs. If Notion is then
    populated from that payload the links 404 ("empty file"). This check flags
    that mismatch so the caller never publishes dead links.

    Returns {"ok": bool, "checks": {...}, "warnings": [...]}. Network failures are
    reported as warnings (fail-open) rather than raising.
    """
    owner, repo = get_owner(), get_repo()
    result = {"ok": True, "checks": {}, "warnings": []}
    if not gh_token() or not owner or not repo:
        result["ok"] = False
        result["warnings"].append("GITHUB_TOKEN/owner/repo 미설정 — 원격 링크 검증 불가")
        return result

    # PDF Report는 blob URL, GitHub URL은 디렉토리(tree) — 존재 확인 가능한 파일 경로만 검사.
    targets = {"PDF Report": _repo_path_from_url(payload.get("PDF Report", ""))}
    # tree URL 자체는 파일이 아니므로, 대표 파일(meta.json)로 디렉토리 존재를 대리 확인.
    gh_dir = _repo_path_from_url(payload.get("GitHub URL", "").replace("/tree/main/", "/blob/main/"))
    if gh_dir:
        targets["GitHub URL (meta.json)"] = f"{gh_dir}/meta.json"

    for label, path in targets.items():
        if not path:
            continue
        try:
            exists = get_file_sha(owner, repo, path) is not None
        except Exception as e:  # noqa: BLE001 — fail-open on network error
            result["warnings"].append(f"{label} 검증 중 오류: {e}")
            continue
        result["checks"][label] = {"path": path, "exists": exists}
        if not exists:
            result["ok"] = False
            result["warnings"].append(
                f"{label} 원격에 없음 → Notion 링크가 깨짐: {path} "
                f"(GitHub push가 실행됐는지 확인 — DISABLE_SYNC/skip-pdf 여부 점검)"
            )
    return result


def sync_analysis(pipeline_dir: Path, ticker: str, dry_run: bool = False, skip_pdf: bool = False) -> dict:
    """Top-level orchestrator — sync single analysis to GitHub + Notion."""
    if not pipeline_dir.exists():
        return {"status": "error", "reason": f"pipeline_dir not found: {pipeline_dir}"}

    payload = extract_metadata(pipeline_dir, ticker)

    if dry_run:
        return {
            "status": "dry_run",
            "payload": {k: v for k, v in payload.items() if not k.startswith("_")},
            "github_status": gh_status(),
            "notion_status": notion_status(),
            # dry-run은 push를 하지 않으므로 payload의 GitHub/PDF URL은 아직 라이브가 아님.
            # 이 payload로 Notion을 채우기 전에 반드시 실제 sync를 먼저 실행할 것.
            "link_warning": "DRY-RUN — payload의 GitHub URL·PDF Report는 push 전이라 아직 유효하지 않음. "
                            "Notion 반영 전 실제 sync(--dry-run 없이) 실행 후 link_integrity.ok=true 확인 필수.",
        }

    gh_result = sync_to_github(pipeline_dir, ticker, payload, skip_pdf=skip_pdf)
    # GitHub push 직후, Notion에 넣을 URL이 실제 원격에 존재하는지 검증.
    link_integrity = verify_remote_links(payload)
    for w in link_integrity["warnings"]:
        print(f"[sync] ⚠ link check: {w}")
    notion_result = sync_to_notion(payload)

    return {
        "status": "completed",
        "ticker": ticker,
        "github": gh_result,
        "link_integrity": link_integrity,
        "notion": notion_result,
        "payload_summary": {
            "Verdict": payload["Verdict"],
            "Signal Score": payload["Signal Score"],
            "Bull/Neutral/Bear": f"{payload['Bull']}/{payload['Neutral']}/{payload['Bear']}",
            "Decision": payload["Decision"],
        }
    }


def main():
    p = argparse.ArgumentParser(description="GitHub + Notion sync orchestrator")
    p.add_argument("--pipeline-dir", required=True, help="분석 디렉토리")
    p.add_argument("--ticker", required=True)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--skip-pdf", action="store_true", help="PDF push 생략 (백필 시 속도 향상)")
    p.add_argument("--output-json", help="결과 저장 경로")
    args = p.parse_args()

    result = sync_analysis(Path(args.pipeline_dir).resolve(), args.ticker,
                            dry_run=args.dry_run, skip_pdf=args.skip_pdf)

    output = json.dumps(result, indent=2, ensure_ascii=False, default=str)
    print(output)

    if args.output_json:
        Path(args.output_json).write_text(output, encoding="utf-8")


if __name__ == "__main__":
    main()
