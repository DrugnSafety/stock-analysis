"""US GAAP 기준 5년 annual + 5분기 quarterly 재무제표 분석 모듈.

Anthropic의 /finance:financial-statements skill 형식을 따라:
- ASC 220 Income Statement (P&L + variance)
- ASC 210 Balance Sheet (snapshot)
- ASC 230 Cash Flow (Indirect method)
- Material Variance Summary (임계값 기반 플래깅)
- Variance Decomposition (Bridge analysis)

데이터 소스:
- 미국 종목 (.NaN ticker): SEC EDGAR XBRL companyfacts API
- 한국 종목 (.KS / .KQ): DART OpenAPI (US GAAP equivalent 매핑)

모든 plugin agent들은 이 모듈을 호출하여 재무 분석을 수행해야 함.
이 모듈은 build_combined.py의 [4] Financial Statements 섹션에서 자동 호출됨.

사용 예:
    from financial_statements_us_gaap import (
        fetch_us_gaap_5y_5q,
        render_financial_statements_section,
    )

    # 1) 데이터 fetch (5년 annual + 5분기 quarterly)
    data = fetch_us_gaap_5y_5q("BTU")

    # 2) 보고서 HTML 섹션 렌더링
    html = render_financial_statements_section("BTU")
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# Path setup for plugin cross-imports
_THIS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _THIS_DIR.parent.parent.parent.parent  # plugins/report-suite/skills/_common → plugins → repo
sys.path.insert(0, str(_REPO_ROOT / "plugins" / "sec-edgar-integration" / "scripts"))
sys.path.insert(0, str(_REPO_ROOT / "plugins" / "dart-integration" / "scripts"))

# ============== MATERIALITY THRESHOLDS ==============
# Either dollar OR percentage threshold triggers "material" flag
# Aligned with /finance:financial-statements skill recommendation
MATERIALITY = {
    "large":  (50_000_000, 5.0),    # > $1B line items
    "medium": (25_000_000, 10.0),   # $100M - $1B
    "small":  (5_000_000, 15.0),    # < $100M
}


def _is_material(curr: float, prior: float) -> bool:
    """Check if a variance exceeds materiality threshold."""
    delta = abs(curr - prior)
    abs_p = abs(prior)
    if abs_p < 0.01:
        return delta > 5
    pct = delta / abs_p * 100
    if abs_p > 1000:
        d_th, p_th = MATERIALITY["large"]
    elif abs_p > 100:
        d_th, p_th = MATERIALITY["medium"]
    else:
        d_th, p_th = MATERIALITY["small"]
    return delta >= d_th or pct >= p_th


# ============== US TICKER FETCH (SEC EDGAR) ==============

def _fetch_us_gaap_annual_5y(ticker: str) -> dict:
    """Fetch 5-year annual financial data from SEC EDGAR XBRL."""
    try:
        from sec_client import get_cik, _request
    except ImportError:
        return {}

    cik = get_cik(ticker)
    if not cik:
        return {}

    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    data = _request(url)
    if not data:
        return {}

    us_gaap = data.get("facts", {}).get("us-gaap", {})

    def get_annual(concepts: list[str], mode: str = "duration") -> dict:
        results = {}
        for c in concepts:
            units = us_gaap.get(c, {}).get("units", {}).get("USD", [])
            for r in units:
                form = r.get("form", "")
                end = r.get("end", "")
                if not form.startswith("10-K") or not end.endswith("-12-31"):
                    continue
                year = int(end[:4])
                if mode == "duration":
                    start = r.get("start", "")
                    if not (start.endswith("-01-01") and int(start[:4]) == year):
                        continue
                else:
                    if "start" in r:
                        continue
                filed = r.get("filed", "")
                existing = results.get(year)
                if existing is None or filed > existing[0]:
                    results[year] = (filed, r["val"] / 1e6)
            if results:
                return {y: v[1] for y, v in results.items()}
        return {}

    revenue = get_annual(["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"])
    op_costs = get_annual(["OperatingCostsAndExpenses", "CostsAndExpenses"])
    op_income = get_annual(["OperatingIncomeLoss"])
    sga = get_annual(["SellingGeneralAndAdministrativeExpense"])
    da = get_annual(["DepreciationDepletionAndAmortization", "DepreciationAndAmortization"])
    interest = get_annual(["InterestExpense"])
    ebt = get_annual(["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest"])
    tax = get_annual(["IncomeTaxExpenseBenefit"])
    ni_cont = get_annual(["IncomeLossFromContinuingOperations"])
    ni_total = get_annual(["NetIncomeLoss"])

    # BS instant
    total_assets = get_annual(["Assets"], "instant")
    cur_assets = get_annual(["AssetsCurrent"], "instant")
    cash = get_annual(["CashAndCashEquivalentsAtCarryingValue"], "instant")
    ar = get_annual(["AccountsReceivableNetCurrent"], "instant")
    inv = get_annual(["InventoryNet"], "instant")
    ppe = get_annual(["PropertyPlantAndEquipmentNet"], "instant")
    total_liab = get_annual(["Liabilities"], "instant")
    cur_liab = get_annual(["LiabilitiesCurrent"], "instant")
    lt_debt = get_annual(["LongTermDebtAndCapitalLeaseObligations", "LongTermDebt"], "instant")
    equity = get_annual(["StockholdersEquity"], "instant")

    # CF
    ocf = get_annual(["NetCashProvidedByUsedInOperatingActivities"])
    capex = get_annual(["PaymentsToAcquirePropertyPlantAndEquipment"])
    icf = get_annual(["NetCashProvidedByUsedInInvestingActivities"])
    fcf_fin = get_annual(["NetCashProvidedByUsedInFinancingActivities"])
    sbc = get_annual(["ShareBasedCompensation"])
    div = get_annual(["PaymentsOfDividends", "PaymentsOfDividendsCommonStock"])
    buybacks = get_annual(["PaymentsForRepurchaseOfCommonStock"])

    all_years = sorted(set(revenue.keys()) | set(op_income.keys()) | set(total_assets.keys()))
    last_5_years = all_years[-5:] if len(all_years) >= 5 else all_years
    if not last_5_years:
        return {}

    return {
        "years": last_5_years,
        "income_statement": {
            "revenue": revenue, "op_costs": op_costs, "op_income": op_income,
            "sga": sga, "da": da, "interest_expense": interest,
            "ebt": ebt, "tax": tax,
            "net_income_continuing": ni_cont, "net_income_total": ni_total,
        },
        "balance_sheet": {
            "total_assets": total_assets, "current_assets": cur_assets,
            "cash": cash, "ar": ar, "inventory": inv, "ppe": ppe,
            "total_liabilities": total_liab, "current_liabilities": cur_liab,
            "lt_debt": lt_debt, "equity": equity,
        },
        "cash_flow": {
            "ocf": ocf, "capex": capex,
            "fcf": {y: ocf.get(y, 0) - capex.get(y, 0) for y in last_5_years},
            "icf": icf, "fcf_finance": fcf_fin,
            "sbc": sbc, "dividends": div, "buybacks": buybacks,
        },
    }


def _fetch_us_gaap_quarterly_5q(ticker: str) -> dict:
    """Fetch last 5 quarters (consecutive) from 10-Q + 10-K filings."""
    try:
        from sec_client import get_cik, _request
    except ImportError:
        return {}

    cik = get_cik(ticker)
    if not cik:
        return {}

    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    data = _request(url)
    if not data:
        return {}
    us_gaap = data.get("facts", {}).get("us-gaap", {})

    def get_quarterly(concepts: list[str], mode: str = "duration") -> dict:
        results = {}
        for c in concepts:
            units = us_gaap.get(c, {}).get("units", {}).get("USD", [])
            for r in units:
                form = r.get("form", "")
                fp = r.get("fp", "")
                end = r.get("end", "")
                if not end:
                    continue
                qmap = {"Q1": 1, "Q2": 2, "Q3": 3}
                if fp not in qmap or form != "10-Q":
                    continue
                quarter = qmap[fp]
                year = int(end[:4]) if end[:4].isdigit() else None
                if year is None:
                    continue
                if mode == "duration":
                    start = r.get("start", "")
                    if not start:
                        continue
                    try:
                        days = (datetime.strptime(end, "%Y-%m-%d") - datetime.strptime(start, "%Y-%m-%d")).days
                        if not (80 <= days <= 100):
                            continue
                    except ValueError:
                        continue
                else:
                    if "start" in r:
                        continue
                key = (year, quarter)
                filed = r.get("filed", "")
                existing = results.get(key)
                if existing is None or filed > existing[0]:
                    results[key] = (filed, r["val"] / 1e6)
            if results:
                return {k: v[1] for k, v in results.items()}
        return {}

    def derive_q4(concepts: list[str]) -> dict:
        """Q4 = FY (10-K) - YTD-9M (Q3 10-Q)."""
        # Get FY values
        fy_vals = {}
        for c in concepts:
            units = us_gaap.get(c, {}).get("units", {}).get("USD", [])
            for r in units:
                if not r.get("form", "").startswith("10-K") or r.get("fp") != "FY":
                    continue
                start, end = r.get("start", ""), r.get("end", "")
                if not (start.endswith("-01-01") and end.endswith("-12-31") and int(start[:4]) == int(end[:4])):
                    continue
                year = int(end[:4])
                filed = r.get("filed", "")
                if year not in fy_vals or filed > fy_vals[year][0]:
                    fy_vals[year] = (filed, r["val"] / 1e6)
            if fy_vals:
                fy_vals = {y: v[1] for y, v in fy_vals.items()}
                break
        # Get YTD-9M values
        ytd9 = {}
        for c in concepts:
            units = us_gaap.get(c, {}).get("units", {}).get("USD", [])
            for r in units:
                if r.get("form") != "10-Q" or r.get("fp") != "Q3":
                    continue
                start, end = r.get("start", ""), r.get("end", "")
                if not (start.endswith("-01-01") and end.endswith("-09-30")):
                    continue
                year = int(end[:4])
                ytd9[year] = r["val"] / 1e6
            if ytd9:
                break
        return {y: fy_vals.get(y, 0) - ytd9.get(y, 0) for y in fy_vals if y in ytd9}

    # Income items
    revenue = get_quarterly(["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"])
    op_costs = get_quarterly(["OperatingCostsAndExpenses", "CostsAndExpenses"])
    op_income = get_quarterly(["OperatingIncomeLoss"])
    sga = get_quarterly(["SellingGeneralAndAdministrativeExpense"])
    da = get_quarterly(["DepreciationDepletionAndAmortization", "DepreciationAndAmortization"])
    ni_total = get_quarterly(["NetIncomeLoss"])
    ni_cont = get_quarterly(["IncomeLossFromContinuingOperations"])

    # BS items
    total_assets = get_quarterly(["Assets"], "instant")
    cash = get_quarterly(["CashAndCashEquivalentsAtCarryingValue"], "instant")
    lt_debt = get_quarterly(["LongTermDebtAndCapitalLeaseObligations", "LongTermDebt"], "instant")
    equity = get_quarterly(["StockholdersEquity"], "instant")

    # Add Q4 (derived)
    q4_rev = derive_q4(["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"])
    q4_op = derive_q4(["OperatingIncomeLoss"])
    q4_opcosts = derive_q4(["OperatingCostsAndExpenses", "CostsAndExpenses"])
    q4_sga = derive_q4(["SellingGeneralAndAdministrativeExpense"])
    q4_da = derive_q4(["DepreciationDepletionAndAmortization", "DepreciationAndAmortization"])
    q4_ni = derive_q4(["NetIncomeLoss"])
    for y in q4_rev:
        revenue[(y, 4)] = q4_rev[y]
    for y in q4_op:
        op_income[(y, 4)] = q4_op[y]
    for y in q4_opcosts:
        op_costs[(y, 4)] = q4_opcosts[y]
    for y in q4_sga:
        sga[(y, 4)] = q4_sga[y]
    for y in q4_da:
        da[(y, 4)] = q4_da[y]
    for y in q4_ni:
        ni_total[(y, 4)] = q4_ni[y]

    # Identify last 5 consecutive quarters (calendar order)
    all_quarters = sorted(set(revenue.keys()) | set(op_income.keys()))
    if not all_quarters:
        return {}
    target = all_quarters[-5:]

    def to_dict(d):
        return {f"{q[0]}Q{q[1]}": d.get(q, 0.0) for q in target}

    return {
        "quarters": [list(q) for q in target],
        "income_statement": {
            "revenue": to_dict(revenue),
            "op_costs": to_dict(op_costs),
            "op_income": to_dict(op_income),
            "sga": to_dict(sga),
            "da": to_dict(da),
            "net_income_total": to_dict(ni_total),
            "net_income_continuing": to_dict(ni_cont),
        },
        "balance_sheet": {
            "total_assets": to_dict(total_assets),
            "cash": to_dict(cash),
            "lt_debt": to_dict(lt_debt),
            "equity": to_dict(equity),
        },
    }


# ============== KOREAN TICKER FETCH (DART) ==============

def _fetch_dart_5y_us_gaap_mapped(ticker: str) -> dict:
    """Fetch 5-year annual from DART, mapped to US GAAP-equivalent line items.

    DART는 K-IFRS 기준이지만, line item을 US GAAP와 매핑하여 동일 형식으로 반환.
    """
    try:
        from dart_client import fetch_5y_financials
    except ImportError:
        return {}

    try:
        d = fetch_5y_financials(ticker)
    except Exception:
        return {}

    if not d:
        return {}

    # DART output format: {"pl_5y": [{"year": ..., "revenue": ..., "op_income": ...}], "bs_snapshot": {...}}
    # Map to same shape as SEC EDGAR
    pl_5y = d.get("pl_5y", [])
    if not pl_5y:
        return {}

    years = [r["year"] for r in pl_5y]

    def to_dict(field):
        return {r["year"]: r.get(field, 0) for r in pl_5y}

    return {
        "years": years,
        "income_statement": {
            "revenue": to_dict("revenue"),
            "op_income": to_dict("op_income"),
            "net_income_continuing": to_dict("net_income"),
            "net_income_total": to_dict("net_income"),
            "op_costs": {y: to_dict("revenue")[y] - to_dict("op_income")[y] for y in years},
            "sga": {y: 0 for y in years},  # K-IFRS는 SG&A 분리 안 함
            "da": {y: 0 for y in years},
            "interest_expense": {y: 0 for y in years},
            "ebt": {y: to_dict("net_income")[y] for y in years},
            "tax": {y: 0 for y in years},
        },
        "balance_sheet": {
            "total_assets": {years[-1]: d.get("bs_snapshot", {}).get("total_assets", 0)},
            "cash": {years[-1]: d.get("bs_snapshot", {}).get("cash", 0)},
            "lt_debt": {years[-1]: d.get("bs_snapshot", {}).get("debt", 0)},
            "equity": {years[-1]: d.get("bs_snapshot", {}).get("equity", 0)},
            "current_assets": {y: 0 for y in years},
            "current_liabilities": {y: 0 for y in years},
            "ar": {y: 0 for y in years},
            "inventory": {y: 0 for y in years},
            "ppe": {y: 0 for y in years},
            "total_liabilities": {years[-1]: d.get("bs_snapshot", {}).get("total_liab", 0)},
        },
        "cash_flow": {
            "ocf": {y: 0 for y in years},
            "capex": {y: 0 for y in years},
            "fcf": {y: 0 for y in years},
            "icf": {y: 0 for y in years},
            "fcf_finance": {y: 0 for y in years},
            "sbc": {y: 0 for y in years},
            "dividends": {y: 0 for y in years},
            "buybacks": {y: 0 for y in years},
        },
        "_note": "K-IFRS → US GAAP equivalent mapping. Only Revenue, Op Income, Net Income are reliable; SG&A/D&A/CF는 미지원.",
    }


# ============== UNIFIED FETCH API ==============

def fetch_us_gaap_5y_5q(ticker: str) -> dict:
    """Unified entry point. Returns 5-year annual + 5-quarter data in US GAAP format.

    Args:
        ticker: 미국 종목 (e.g. "BTU") 또는 한국 종목 (e.g. "005490.KS")

    Returns:
        {
            "ticker": str,
            "annual": {...5-year US GAAP...},
            "quarterly": {...5-quarter US GAAP...},  # KR ticker는 미지원
            "currency": "USD" or "KRW",
            "source": "SEC EDGAR" or "DART (K-IFRS mapped)",
            "fetched_at": ISO timestamp,
        }
    """
    is_kr = ticker.endswith((".KS", ".KQ"))

    if is_kr:
        annual = _fetch_dart_5y_us_gaap_mapped(ticker)
        quarterly = {}
        source = "DART (K-IFRS → US GAAP mapped)"
        currency = "KRW"
    else:
        annual = _fetch_us_gaap_annual_5y(ticker)
        quarterly = _fetch_us_gaap_quarterly_5q(ticker)
        source = "SEC EDGAR XBRL companyfacts"
        currency = "USD"

    return {
        "ticker": ticker,
        "annual": annual,
        "quarterly": quarterly,
        "currency": currency,
        "source": source,
        "fetched_at": datetime.utcnow().isoformat(),
    }


# ============== VARIANCE ANALYSIS ==============

def compute_variance(curr: float, prior: float) -> dict:
    delta = curr - prior
    pct = (delta / abs(prior) * 100) if abs(prior) > 0.01 else 0.0
    return {"current": curr, "prior": prior, "delta": delta, "pct": pct,
            "is_material": _is_material(curr, prior)}


def compute_material_variances(annual: dict, target_year: int, prior_year: int) -> list[dict]:
    """Identify material variances per /finance:financial-statements thresholds."""
    if not annual:
        return []

    INC = annual.get("income_statement", {})
    BS = annual.get("balance_sheet", {})
    CF = annual.get("cash_flow", {})

    items = [
        ("Revenue", INC.get("revenue", {}), "IS", "favor_positive"),
        ("Op. costs (ex SG&A, D&A)",
         {y: INC.get("op_costs", {}).get(y, 0) - INC.get("sga", {}).get(y, 0) - INC.get("da", {}).get(y, 0) for y in [target_year, prior_year]},
         "IS", "favor_negative"),
        ("SG&A", INC.get("sga", {}), "IS", "favor_negative"),
        ("D&A", INC.get("da", {}), "IS", "favor_negative"),
        ("Operating income", INC.get("op_income", {}), "IS", "favor_positive"),
        ("Pre-tax income", INC.get("ebt", {}), "IS", "favor_positive"),
        ("Tax expense", INC.get("tax", {}), "IS", "favor_negative"),
        ("Net income (Continuing)", INC.get("net_income_continuing", {}), "IS", "favor_positive"),
        ("Cash & equivalents", BS.get("cash", {}), "BS", "favor_positive"),
        ("Accounts receivable", BS.get("ar", {}), "BS", "neutral"),
        ("PP&E, net", BS.get("ppe", {}), "BS", "neutral"),
        ("Equity", BS.get("equity", {}), "BS", "favor_positive"),
        ("OCF", CF.get("ocf", {}), "CF", "favor_positive"),
        ("CapEx", CF.get("capex", {}), "CF", "favor_negative"),
        ("FCF", CF.get("fcf", {}), "CF", "favor_positive"),
        ("Share repurchases", CF.get("buybacks", {}), "CF", "neutral"),
    ]

    results = []
    for label, d, stmt, polarity in items:
        c = d.get(target_year, 0)
        p = d.get(prior_year, 0)
        if not _is_material(c, p):
            continue
        delta = c - p
        pct = (delta / abs(p) * 100) if abs(p) > 0.01 else 0.0
        if polarity == "favor_positive":
            direction = "Unfavorable" if delta < 0 else "Favorable"
        elif polarity == "favor_negative":
            direction = "Favorable" if delta < 0 else "Unfavorable"
        else:
            direction = "Neutral"
        results.append({
            "line_item": label, "stmt": stmt,
            "current": c, "prior": p, "delta": delta, "pct": pct,
            "direction": direction,
        })
    return results


# ============== HTML RENDERING ==============

def _fmt(v) -> str:
    if isinstance(v, str):
        return v
    if v is None:
        return "n/a"
    if v < 0:
        return f"({abs(v):,.1f})"
    return f"{v:,.1f}"


def _pct(p) -> str:
    if p is None:
        return "n/a"
    return f"{p:+.1f}%"


def _annual_table_html(annual: dict, currency: str = "USD") -> str:
    if not annual or not annual.get("years"):
        return "<p>Annual data unavailable.</p>"

    years = annual["years"]
    INC = annual["income_statement"]
    BS = annual.get("balance_sheet", {})
    CF = annual.get("cash_flow", {})

    def get_row(label, source_dict, key=None, cls=""):
        if key:
            d = source_dict.get(key, {})
        else:
            d = source_dict
        cells = "".join(f"<td>{_fmt(d.get(y, 0))}</td>" for y in years)
        return f"<tr class='{cls}'><td>{label}</td>{cells}</tr>"

    head_cells = "".join(f"<th>FY{y}</th>" for y in years)
    html = f"""
    <h3>Income Statement (5-Year, US GAAP / ASC 220)</h3>
    <p style="font-size:9pt;color:#777;">{currency} millions  ·  Source: {annual.get('_source', 'SEC EDGAR / DART')}</p>
    <table class="dt">
      <thead><tr><th>Line Item</th>{head_cells}</tr></thead>
      <tbody>
        {get_row('Revenue', INC, 'revenue', 'total')}
        {get_row('Operating Costs (total)', INC, 'op_costs')}
        {get_row('  SG&A', INC, 'sga')}
        {get_row('  D&A', INC, 'da')}
        {get_row('Operating Income', INC, 'op_income', 'total')}
        {get_row('  Interest Expense', INC, 'interest_expense')}
        {get_row('Pre-tax Income', INC, 'ebt', 'total')}
        {get_row('  Tax Expense', INC, 'tax')}
        {get_row('Net Income (Continuing)', INC, 'net_income_continuing', 'total')}
      </tbody>
    </table>
    """

    if BS.get("total_assets"):
        html += f"""
        <h3>Balance Sheet (5-Year Snapshot, US GAAP / ASC 210)</h3>
        <table class="dt">
          <thead><tr><th>Line Item</th>{head_cells}</tr></thead>
          <tbody>
            {get_row('Total Assets', BS, 'total_assets', 'total')}
            {get_row('  Cash & Equivalents', BS, 'cash')}
            {get_row('  Accounts Receivable', BS, 'ar')}
            {get_row('  Inventory', BS, 'inventory')}
            {get_row('  PP&E, net', BS, 'ppe')}
            {get_row('Total Liabilities', BS, 'total_liabilities', 'total')}
            {get_row('  LT Debt + Capital Lease', BS, 'lt_debt')}
            {get_row("Stockholders' Equity", BS, 'equity', 'total')}
          </tbody>
        </table>
        """

    if CF.get("ocf"):
        html += f"""
        <h3>Cash Flow Statement (5-Year, US GAAP / ASC 230 Indirect)</h3>
        <table class="dt">
          <thead><tr><th>Line Item</th>{head_cells}</tr></thead>
          <tbody>
            {get_row('Operating Activities (OCF)', CF, 'ocf', 'total')}
            {get_row('Capital Expenditures', CF, 'capex')}
            {get_row('Free Cash Flow (OCF − CapEx)', CF, 'fcf', 'total')}
            {get_row('Investing Activities (ICF)', CF, 'icf')}
            {get_row('Financing Activities', CF, 'fcf_finance')}
            {get_row('Dividends Paid', CF, 'dividends')}
            {get_row('Share Repurchases', CF, 'buybacks')}
          </tbody>
        </table>
        """

    return html


def _quarterly_table_html(quarterly: dict, currency: str = "USD") -> str:
    if not quarterly or not quarterly.get("quarters"):
        return "<p>Quarterly data unavailable.</p>"

    qs = quarterly["quarters"]
    q_labels = [f"{q[0]}Q{q[1]}" for q in qs]
    QIS = quarterly["income_statement"]
    QBS = quarterly.get("balance_sheet", {})

    def get_row(label, key, source=QIS, cls=""):
        d = source.get(key, {})
        cells = "".join(f"<td>{_fmt(d.get(q, 0))}</td>" for q in q_labels)
        return f"<tr class='{cls}'><td>{label}</td>{cells}</tr>"

    head_cells = "".join(f"<th>{q}</th>" for q in q_labels)

    html = f"""
    <h3>Quarterly Income Statement (Last 5 Quarters)</h3>
    <p style="font-size:9pt;color:#777;">{currency} millions  ·  Q4 derived from FY 10-K minus 9-month YTD</p>
    <table class="dt">
      <thead><tr><th>Line Item</th>{head_cells}</tr></thead>
      <tbody>
        {get_row('Revenue', 'revenue', cls='total')}
        {get_row('Operating Costs (total)', 'op_costs')}
        {get_row('  SG&A', 'sga')}
        {get_row('  D&A', 'da')}
        {get_row('Operating Income', 'op_income', cls='total')}
        {get_row('Net Income (Total)', 'net_income_total', cls='total')}
      </tbody>
    </table>
    """

    if QBS.get("total_assets"):
        html += f"""
        <h3>Quarterly Balance Sheet Snapshot</h3>
        <table class="dt">
          <thead><tr><th>Line Item</th>{head_cells}</tr></thead>
          <tbody>
            {get_row('Total Assets', 'total_assets', QBS, 'total')}
            {get_row('Cash & Equivalents', 'cash', QBS)}
            {get_row('LT Debt + Capital Lease', 'lt_debt', QBS)}
            {get_row("Stockholders' Equity", 'equity', QBS, 'total')}
          </tbody>
        </table>
        """

    return html


def _variance_table_html(material_vars: list[dict], target_year: int, prior_year: int) -> str:
    if not material_vars:
        return ""
    rows = ""
    for i, m in enumerate(material_vars, 1):
        color = "#dc2626" if "Unfav" in m["direction"] else ("#16a34a" if "Favor" in m["direction"] else "#6b7280")
        rows += f"""
        <tr>
          <td>{i}</td>
          <td>{m['line_item']}</td>
          <td>{m['stmt']}</td>
          <td>{_fmt(m['delta'])}</td>
          <td>{_pct(m['pct'])}</td>
          <td style="color:{color};font-weight:700;">{m['direction']}</td>
        </tr>
        """
    return f"""
    <h3>Material Variance Summary (FY{target_year} vs FY{prior_year})</h3>
    <p style="font-size:9pt;color:#777;">Materiality thresholds: > $1B = $50M / 5%, $100M-$1B = $25M / 10%, < $100M = $5M / 15%</p>
    <table class="dt">
      <thead><tr><th>#</th><th>Line Item</th><th>Stmt</th><th>Δ ($M)</th><th>Δ (%)</th><th>방향</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    """


def render_financial_statements_section(ticker: str) -> str:
    """Top-level entry point: 5Y annual + 5Q quarterly + variance summary HTML.

    이 함수는 build_combined.py의 [4] Financial Statements 섹션에서 호출됨.
    모든 plugin agent들이 이 출력을 활용하여 재무 분석을 수행함.
    """
    data = fetch_us_gaap_5y_5q(ticker)
    annual = data.get("annual", {})
    quarterly = data.get("quarterly", {})
    currency = data.get("currency", "USD")

    if not annual:
        return ""

    annual["_source"] = data.get("source", "")

    body = '<h2>4. 재무제표 분석 — US GAAP 기준 (5년 + 5분기)</h2>'
    body += f'<p style="font-size:9.5pt;">/finance:financial-statements (Anthropic Plugin) 표준 형식. 모든 plugin agent들이 이 분석 결과를 무조건 활용해야 함.</p>'

    body += _annual_table_html(annual, currency)

    if quarterly:
        body += _quarterly_table_html(quarterly, currency)

    # Material variance summary (current vs prior year)
    years = annual.get("years", [])
    if len(years) >= 2:
        target, prior = years[-1], years[-2]
        material = compute_material_variances(annual, target, prior)
        body += _variance_table_html(material, target, prior)

    body += f'<p style="font-size:8pt;color:#999;margin-top:10pt;">Data source: {data.get("source", "n/a")} · Fetched: {data.get("fetched_at", "n/a")}</p>'

    return body


# ============== CLI ==============
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Financial Statements US GAAP Analysis")
    p.add_argument("ticker", help="Ticker (e.g. BTU, 005490.KS)")
    p.add_argument("--output", help="Save JSON to this path")
    args = p.parse_args()

    data = fetch_us_gaap_5y_5q(args.ticker)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(data, indent=2, default=str))
        print(f"Saved to {args.output}")
    else:
        print(json.dumps(data, indent=2, default=str))
