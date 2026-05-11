"""Notion API 클라이언트 — 주식 분석 Hub DB row 생성/업데이트.

두 모드 지원:
- Direct API (NOTION_TOKEN + NOTION_API base): 일반 Python 환경
- MCP wrapper (선호): Cowork/Claude Code MCP가 연결되어 있으면 우선 사용

이 클라이언트는 분석 메타데이터를 받아 Notion DB row를 생성/업데이트한다.

DB schema (data_source_id: NOTION_DATA_SOURCE_ID):
  Ticker (TITLE)   Company (text)   Date (date)   Sector (select)
  Analysis Type (select)   Blogger (text)
  Verdict (select)   Signal Score (number)   Avg Confidence (number)   Decision (select)
  Bull / Neutral / Bear (number)
  N Thesis (number)   Implicit Thesis (checkbox)   Top Concerns (text)
  GitHub URL (url)   PDF Report (url)   Local Path (text)
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional


def _read_env_key(key: str) -> Optional[str]:
    v = os.environ.get(key)
    if v:
        return v
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    candidates = [Path.cwd() / ".env"]
    if project_dir:
        candidates.append(Path(project_dir) / ".env")
    candidates.append(Path(__file__).resolve().parent.parent.parent.parent / ".env")
    for env_path in candidates:
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.strip().startswith(f"{key}="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def get_token() -> Optional[str]:
    return _read_env_key("NOTION_TOKEN")


def get_data_source_id() -> Optional[str]:
    return _read_env_key("NOTION_DATA_SOURCE_ID")


def get_status() -> dict:
    return {
        "token_configured": get_token() is not None,
        "data_source_id": get_data_source_id(),
    }


# Sector mapping — normalize free-text sector to one of DB enum values
SECTOR_MAP = {
    "LNG Export Operator": "LNG Export",
    "LNG Export": "LNG Export",
    "Coal Mining": "Coal Mining",
    "Natural Gas E&P": "Natural Gas E&P",
    "Semiconductor": "Semiconductor",
    "Battery Materials": "Battery Materials",
    "Shipbuilding": "Shipbuilding",
    "Shipbuilding (LNG Carrier)": "Shipbuilding",
    "Bio/Pharma": "Bio/Pharma",
    "Memory": "Memory",
    "Energy Infrastructure": "Energy Infrastructure",
}


def normalize_sector(sector_raw: str) -> str:
    if not sector_raw:
        return "Other"
    s = sector_raw.strip()
    if s in SECTOR_MAP:
        return SECTOR_MAP[s]
    s_lower = s.lower()
    for k, v in SECTOR_MAP.items():
        if k.lower() in s_lower or s_lower in k.lower():
            return v
    return "Other"


# ============== Direct API (when NOTION_TOKEN set) ==============

def _headers_direct() -> dict:
    token = get_token()
    if not token:
        raise RuntimeError("NOTION_TOKEN not set — use MCP instead")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }


def _to_notion_prop(field: str, value, schema_type: str) -> dict:
    """Convert plain Python value to Notion API property format."""
    if value is None:
        return {}
    if schema_type == "title":
        return {"title": [{"type": "text", "text": {"content": str(value)}}]}
    elif schema_type == "rich_text":
        return {"rich_text": [{"type": "text", "text": {"content": str(value)[:2000]}}]}
    elif schema_type == "number":
        return {"number": float(value) if value is not None else None}
    elif schema_type == "select":
        return {"select": {"name": str(value)}} if value else {"select": None}
    elif schema_type == "date":
        if isinstance(value, str):
            return {"date": {"start": value}}
        return {"date": None}
    elif schema_type == "checkbox":
        return {"checkbox": bool(value)}
    elif schema_type == "url":
        return {"url": str(value) if value else None}
    return {}


# Map of field name → Notion type
FIELD_SCHEMA = {
    "Ticker": "title",
    "Company": "rich_text",
    "Date": "date",
    "Sector": "select",
    "Analysis Type": "select",
    "Blogger": "rich_text",
    "Verdict": "select",
    "Signal Score": "number",
    "Avg Confidence": "number",
    "Decision": "select",
    "Bull": "number",
    "Neutral": "number",
    "Bear": "number",
    "N Thesis": "number",
    "Implicit Thesis": "checkbox",
    "Top Concerns": "rich_text",
    "GitHub URL": "url",
    "PDF Report": "url",
    "Local Path": "rich_text",
}


def build_notion_properties(payload: dict) -> dict:
    """Convert analysis metadata dict into Notion API properties."""
    props = {}
    for field, value in payload.items():
        if field not in FIELD_SCHEMA or value is None:
            continue
        if field == "Sector":
            value = normalize_sector(value)
        prop = _to_notion_prop(field, value, FIELD_SCHEMA[field])
        if prop:
            props[field] = prop
    return props


def query_page_by_ticker(ticker: str) -> Optional[str]:
    """Find existing page by Ticker title — return page_id or None."""
    import requests
    ds_id = get_data_source_id()
    if not ds_id or not get_token():
        return None

    body = {
        "filter": {
            "property": "Ticker",
            "title": {"equals": ticker}
        }
    }
    r = requests.post(
        f"https://api.notion.com/v1/data_sources/{ds_id}/query",
        headers=_headers_direct(), json=body, timeout=15
    )
    if r.status_code == 200:
        results = r.json().get("results", [])
        if results:
            return results[0]["id"]
    return None


def upsert_row_direct(payload: dict) -> dict:
    """Create or update a row in the database (direct API)."""
    import requests
    ds_id = get_data_source_id()
    if not ds_id:
        raise RuntimeError("NOTION_DATA_SOURCE_ID not set")

    ticker = payload.get("Ticker")
    if not ticker:
        raise ValueError("Ticker required")

    props = build_notion_properties(payload)
    existing_page_id = query_page_by_ticker(ticker)

    if existing_page_id:
        # Update existing
        r = requests.patch(
            f"https://api.notion.com/v1/pages/{existing_page_id}",
            headers=_headers_direct(),
            json={"properties": props},
            timeout=20,
        )
        r.raise_for_status()
        return {"action": "updated", "page_id": existing_page_id, "url": r.json().get("url")}
    else:
        # Create new
        r = requests.post(
            "https://api.notion.com/v1/pages",
            headers=_headers_direct(),
            json={"parent": {"data_source_id": ds_id}, "properties": props},
            timeout=20,
        )
        r.raise_for_status()
        data = r.json()
        return {"action": "created", "page_id": data["id"], "url": data.get("url")}


# ============== MCP fallback (called by CLI when no NOTION_TOKEN) ==============

def emit_mcp_payload(payload: dict, output_path: Optional[Path] = None) -> dict:
    """Emit JSON payload suitable for MCP notion-create-pages / update-page.

    The caller (sync_analysis.py orchestrator running under Cowork/Claude Code)
    will read this and invoke MCP tools directly.
    """
    ds_id = get_data_source_id()
    if not ds_id:
        raise RuntimeError("NOTION_DATA_SOURCE_ID not set")

    # Normalize sector
    if "Sector" in payload:
        payload["Sector"] = normalize_sector(payload["Sector"])

    mcp_payload = {
        "data_source_id": ds_id,
        "properties": {k: v for k, v in payload.items() if k in FIELD_SCHEMA and v is not None},
        "_instructions": "Pass to mcp__<notion-server>__notion-create-pages or notion-update-page. Filter by Ticker before create."
    }
    if output_path:
        output_path.write_text(json.dumps(mcp_payload, indent=2, ensure_ascii=False))
    return mcp_payload


# ============== CLI ==============
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Notion DB row sync")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")

    pp = sub.add_parser("upsert")
    pp.add_argument("--payload-json", required=True, help="JSON file with row data")
    pp.add_argument("--mode", choices=["direct", "mcp"], default="direct")
    pp.add_argument("--output-mcp-payload", help="(mcp mode) where to write MCP payload JSON")

    args = p.parse_args()

    if args.cmd == "status":
        print(json.dumps(get_status(), indent=2))
    elif args.cmd == "upsert":
        payload = json.loads(Path(args.payload_json).read_text())
        if args.mode == "direct":
            result = upsert_row_direct(payload)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            out_path = Path(args.output_mcp_payload) if args.output_mcp_payload else None
            mcp = emit_mcp_payload(payload, out_path)
            print(json.dumps(mcp, indent=2, ensure_ascii=False))
