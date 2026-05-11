"""Currency-aware price formatter — 통화 기호 + native 포맷.

Usage:
    from currency_format import format_price
    format_price(270.06, "USD")    # "$270.06"
    format_price(688000, "KRW")    # "₩688,000"
    format_price(1500, "JPY")      # "¥1,500"
"""
SYMBOLS = {
    "USD": "$", "KRW": "₩", "JPY": "¥", "EUR": "€",
    "GBP": "£", "HKD": "HK$", "CNY": "¥", "TWD": "NT$",
    "CAD": "C$", "AUD": "A$",
}
NO_DECIMAL = {"KRW", "JPY"}  # 소수점 없음

def format_price(price, currency: str = "USD") -> str:
    """Format price with currency symbol. Falls back to '<num> <CODE>' on unknown currency."""
    if price is None or price == "":
        return "-"
    try:
        p = float(price)
    except (TypeError, ValueError):
        return str(price)
    sym = SYMBOLS.get(currency)
    if sym is None:
        return f"{p:,.2f} {currency}"
    fmt = "{:,.0f}" if currency in NO_DECIMAL else "{:,.2f}"
    return f"{sym}{fmt.format(p)}"

def format_amount_local(value, currency: str = "KRW") -> str:
    """Format larger amounts (positions, AUM) — KRW: 억/만 단위, USD: M/B 등."""
    if value is None: return "-"
    try: v = float(value)
    except: return str(value)
    sym = SYMBOLS.get(currency, "")
    if currency == "KRW":
        if abs(v) >= 1e8: return f"{sym}{v/1e8:,.2f}억"
        if abs(v) >= 1e4: return f"{sym}{v/1e4:,.0f}만"
        return f"{sym}{v:,.0f}"
    if currency == "USD":
        if abs(v) >= 1e9: return f"{sym}{v/1e9:.2f}B"
        if abs(v) >= 1e6: return f"{sym}{v/1e6:.2f}M"
        if abs(v) >= 1e3: return f"{sym}{v/1e3:.1f}K"
        return f"{sym}{v:,.2f}"
    return f"{sym}{v:,.2f}" if sym else f"{v:,.2f} {currency}"
