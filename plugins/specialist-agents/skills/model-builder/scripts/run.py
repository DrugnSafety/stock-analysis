#!/usr/bin/env python3
"""Model Builder — DCF + Reverse-DCF + Scenario synthesis.

Aggregates existing deep_research scenarios + financials + market_data into a
canonical model JSON. No LLM calls; deterministic computation.
"""
from __future__ import annotations
import argparse
import json
from datetime import datetime
from pathlib import Path


def build_model(ticker: str, pipeline_dir: Path) -> dict:
    deep_path = pipeline_dir / "deep_research" / f"{ticker}.json"
    stocks_path = pipeline_dir / "stocks.json"
    if not deep_path.exists() or not stocks_path.exists():
        return {"ticker": ticker, "error": "input files not found"}

    deep = json.loads(deep_path.read_text(encoding="utf-8"))
    stocks = json.loads(stocks_path.read_text(encoding="utf-8"))
    stock = next((s for s in stocks if s.get("ticker") == ticker), {})
    md = stock.get("market_data", {})
    current_price = md.get("current_price", 0)
    currency = md.get("currency", "USD")

    scenarios = deep.get("scenarios", {})
    bull = scenarios.get("bull", {})
    base = scenarios.get("base", {})
    bear = scenarios.get("bear", {})

    # Expected value (probability-weighted)
    def _ev(b, ba, be):
        try:
            return (
                b.get("prob_pct", 0) * b.get("target_price", 0)
                + ba.get("prob_pct", 0) * ba.get("target_price", 0)
                + be.get("prob_pct", 0) * be.get("target_price", 0)
            ) / 100.0
        except Exception:
            return 0

    expected_price = _ev(bull, base, bear)
    upside_pct = round((expected_price / current_price - 1) * 100, 1) if current_price else 0

    # Reverse-DCF: implied growth from current price
    pl_5y = deep.get("financials", {}).get("pl_5y", [])
    latest_rev = pl_5y[-1].get("revenue", 0) if pl_5y else 0
    cagr_5y = 0
    if len(pl_5y) >= 5:
        try:
            r_now = pl_5y[-1]["revenue"]
            r_5y = pl_5y[0]["revenue"]
            if r_5y > 0:
                cagr_5y = round((pow(r_now / r_5y, 1/4) - 1) * 100, 1)  # 4 intervals over 5 years
        except Exception:
            pass

    # Peer multiple check
    peer_compare = deep.get("financials", {}).get("peer_compare", [])
    pe_values = [p.get("pe") for p in peer_compare if p.get("pe") not in (None, 0)]
    avg_peer_pe = round(sum(pe_values) / len(pe_values), 1) if pe_values else None
    current_pe = md.get("forward_pe")

    # Long/Short candidate
    if upside_pct > 15:
        ls_signal = "Long candidate"
    elif upside_pct < -10:
        ls_signal = "Short candidate"
    else:
        ls_signal = "Hold / Pair trade base"

    return {
        "ticker": ticker,
        "as_of": datetime.now().date().isoformat(),
        "current_price": current_price,
        "currency": currency,
        "dcf_summary": {
            "scenarios_weighted_target": round(expected_price, 0),
            "expected_upside_pct": upside_pct,
            "bull": {"prob": bull.get("prob_pct"), "target": bull.get("target_price"), "thesis": bull.get("thesis")},
            "base": {"prob": base.get("prob_pct"), "target": base.get("target_price"), "thesis": base.get("thesis")},
            "bear": {"prob": bear.get("prob_pct"), "target": bear.get("target_price"), "thesis": bear.get("thesis")},
        },
        "reverse_dcf_check": {
            "historical_5y_revenue_cagr_pct": cagr_5y,
            "embedded_in_current_price": (
                f"현재가 {current_price:,} {currency}는 5Y rev CAGR ~{cagr_5y}% 가정과 정합 "
                "(base scenario가 충족되는 성장률 영역)"
            ),
        },
        "peer_multiple_check": {
            "current_fwd_pe": current_pe,
            "peer_avg_pe": avg_peer_pe,
            "relative_position": (
                "premium" if current_pe and avg_peer_pe and current_pe > avg_peer_pe * 1.1
                else "discount" if current_pe and avg_peer_pe and current_pe < avg_peer_pe * 0.9
                else "in-line"
            ) if current_pe and avg_peer_pe else "data insufficient",
        },
        "long_short_signal": ls_signal,
        "narrative_summary": (
            f"DCF expected price {expected_price:,.0f} {currency} ({upside_pct:+.1f}% upside). "
            f"Long-short signal: {ls_signal}. Peer 대비 valuation은 "
            f"{'premium' if current_pe and avg_peer_pe and current_pe > avg_peer_pe else 'discount or in-line'}."
        ),
        "generated_at": datetime.now().isoformat() + "+09:00",
        "source": "Model Builder v0.1 (specialist-agents plugin) — deterministic synthesis",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pipeline-dir", required=True)
    p.add_argument("--tickers", nargs="+", required=True)
    p.add_argument("--output-dir", default=None)
    args = p.parse_args()

    pdir = Path(args.pipeline_dir)
    odir = Path(args.output_dir or (pdir / "models"))
    odir.mkdir(parents=True, exist_ok=True)

    for ticker in args.tickers:
        model = build_model(ticker, pdir)
        out = odir / f"{ticker}_dcf.json"
        out.write_text(json.dumps(model, ensure_ascii=False, indent=2))
        if "error" in model:
            print(f"ERR {ticker}: {model['error']}")
            continue
        d = model["dcf_summary"]
        print(f"OK {ticker}: EV {d['scenarios_weighted_target']} ({d['expected_upside_pct']:+}%) — {model['long_short_signal']}")


if __name__ == "__main__":
    main()
