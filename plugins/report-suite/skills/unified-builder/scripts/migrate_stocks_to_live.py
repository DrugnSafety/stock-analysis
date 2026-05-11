#!/usr/bin/env python3
"""모든 분석의 stocks.json을 LLM placeholder → 실제 yfinance 데이터로 마이그레이션.

Usage:
  python migrate_stocks_to_live.py --pipeline-dir <path>     # 단일 분석
  python migrate_stocks_to_live.py --all                     # 모든 .analysis-log/ 분석

이 스크립트는 stocks.json의 ticker만 추출하고, market_data 필드는
yfinance에서 라이브 fetch된 실제 데이터로 완전히 교체합니다.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = SCRIPT_DIR.parent.parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "skills" / "_common"))

from market_fetcher import fetch_market_data  # type: ignore
from ticker_resolver import resolve_ticker  # type: ignore


def migrate_one(pipeline_dir: Path) -> bool:
    stocks_path = pipeline_dir / "stocks.json"
    if not stocks_path.exists():
        print(f"  ✗ {pipeline_dir.name}: stocks.json missing")
        return False

    try:
        old_stocks = json.loads(stocks_path.read_text())
    except Exception as e:
        print(f"  ✗ {pipeline_dir.name}: malformed JSON ({e})")
        return False

    tickers = [s.get("ticker") for s in old_stocks if s.get("ticker")]
    if not tickers:
        print(f"  ✗ {pipeline_dir.name}: no tickers")
        return False

    new_stocks = []
    for ticker in tickers:
        # Preserve metadata fields
        old = next((s for s in old_stocks if s.get("ticker") == ticker), {})
        info = resolve_ticker(ticker)
        live_data = fetch_market_data(ticker)
        if not live_data:
            print(f"    ⚠ {ticker}: fetch failed, keeping old data with warning")
            new_stocks.append({**old, "fetch_warning": "yfinance fetch failed"})
            continue

        new_entry = {
            "ticker": ticker,
            "name": info.get("kr") or live_data.get("name", ticker),
            "exchange": _exchange(ticker),
            "thesis_alignment": old.get("thesis_alignment", "high"),
            "market_data": live_data,
        }
        # Preserve any other custom fields
        for k, v in old.items():
            if k not in ("ticker", "name", "exchange", "thesis_alignment", "market_data"):
                new_entry[k] = v
        new_stocks.append(new_entry)

    # Backup old + write new
    backup = stocks_path.with_suffix(".json.placeholder_backup")
    if not backup.exists():
        backup.write_text(json.dumps(old_stocks, ensure_ascii=False, indent=2))
    stocks_path.write_text(json.dumps(new_stocks, ensure_ascii=False, indent=2))

    print(f"  ✓ {pipeline_dir.name}: {len(new_stocks)} stocks migrated to live yfinance")
    for s in new_stocks:
        m = s.get("market_data", {})
        print(f"      {s['ticker']}: {m.get('current_price', '?'):,.0f} {m.get('currency', '?')} "
               f"({m.get('as_of_date', '?')})")
    return True


def _exchange(ticker: str) -> str:
    if ticker.endswith(".KS"):
        return "KOSPI"
    if ticker.endswith(".KQ"):
        return "KOSDAQ"
    if ticker.endswith(".T"):
        return "TSE"
    if ticker.endswith(".HE"):
        return "Helsinki"
    return "NYSE/NASDAQ"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pipeline-dir")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--root", default=".analysis-log")
    args = parser.parse_args()

    if args.pipeline_dir:
        migrate_one(Path(args.pipeline_dir))
        return

    if args.all:
        root = Path(args.root)
        if not root.exists():
            print(f"Error: {root} does not exist")
            sys.exit(1)

        pipelines = []
        # bloggers
        for blogger_dir in (root / "bloggers").iterdir() if (root / "bloggers").exists() else []:
            if blogger_dir.is_dir():
                for slug_dir in blogger_dir.iterdir():
                    if slug_dir.is_dir() and (slug_dir / "stocks.json").exists():
                        pipelines.append(slug_dir)
        # standalone
        if (root / "standalone").exists():
            for slug_dir in (root / "standalone").iterdir():
                if slug_dir.is_dir() and (slug_dir / "stocks.json").exists():
                    pipelines.append(slug_dir)

        print(f"=== Migrating {len(pipelines)} pipelines to live yfinance data ===\n")
        for p in pipelines:
            migrate_one(p)


if __name__ == "__main__":
    main()
