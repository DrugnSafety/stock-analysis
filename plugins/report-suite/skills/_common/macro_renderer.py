"""Macro Anchor section renderer — Deep Research 직전에 삽입되는 거시·정책 anchor.

Data source: plugins/macro-economic-integration/scripts/macro_dashboard.py
Schema: macro_snapshot.json (Sprint 1.1 산출)

Renders:
  • 미국 매크로 (FRED 5종): 실업률·CPI·연방기금금리·yield curve·10Y
  • 글로벌 전망 (IMF WEO): N개 국가 × GDP·경상수지·CPI·정부부채
  • Auto-generated regime narrative (rule-based, LLM 미사용)
  • Flag badges (MONETARY_TIGHTENING·INFLATION_ABOVE_TARGET·RECESSION_LEADING_INDICATOR·...)

Style:
  deep_research.py · financial_statements_us_gaap.py와 동일한 inline-style HTML.
  외부 CSS dependency 없음 (PDF 변환 안정성).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional


# ── Flag → 한글 배지 매핑 ───────────────────────────────────────────────
FLAG_BADGES = {
    "MONETARY_TIGHTENING": ("긴축 통화정책", "#dc2626", "위험자산·valuation 하방 압력"),
    "INFLATION_ABOVE_TARGET": ("CPI 목표 초과", "#ea580c", "Fed 2% 목표보다 높음"),
    "RECESSION_LEADING_INDICATOR": ("경기침체 leading", "#991b1b", "10Y-2Y 역전 — 12~18m 시차"),
    "KR_UNDERPERFORM_US": ("한국 < 美 성장", "#7c3aed", "IMF WEO 전망 격차 >0.5%p"),
}


# ── Country code → 한자/약어 라벨 (weasyprint emoji 폰트 미지원 회피, Sprint B-1) ──
# 기존 🇺🇸/🇰🇷 emoji는 PDF에서 ⬜로 깨짐. CJK 한자 + 영문 약어로 대체.
COUNTRY_FLAGS = {
    "USA": "美", "KOR": "韓", "CHN": "中", "JPN": "日",
    "DEU": "獨", "GBR": "英", "IND": "印", "FRA": "佛",
    "ITA": "伊", "CAN": "加", "AUS": "濠", "BRA": "巴",
}


def render_macro_anchor_section(
    snapshot: Dict[str, Any],
    sector: Optional[str] = None,
    ticker: str = "",
    company_name: str = "",
) -> str:
    """Top-level renderer — macro_snapshot.json 전체를 HTML section으로 변환.

    Args:
        snapshot: macro_snapshot.json
        sector: GICS 11-sector 이름 (Sprint B-2 추가). 있으면 sector impact narrative 자동 삽입
        ticker: 종목 ticker (sector impact narrative 라벨용)
        company_name: 종목 한글명
    """
    if not snapshot or "us_macro" not in snapshot:
        return ""

    parts: List[str] = []

    # ── Section header ──────────────────────────────────────────────
    # NOTE: page-break-before는 build_combined.py의 <div>가 담당 — 중복 시 빈 페이지 발생
    # emoji는 weasyprint에서 깨지므로 텍스트로 대체 ([글로벌] 같은 한글 prefix)
    parts.append(
        '<h1>[글로벌] Macro Anchor — 거시·정책 환경</h1>'
    )
    parts.append(
        '<div class="info" style="background:#f0f9ff;border-left:4px solid #0284c7;'
        'padding:10px 14px;margin:10px 0;font-size:12px;color:#475569;">'
        'FRED + IMF WEO 공식 데이터 기반의 거시 환경 anchor. '
        '본 종목 분석의 외부 환경 baseline으로 사용 — 페르소나 평가(R2) 시 Macro Analyst lens의 입력 데이터.'
        '</div>'
    )

    # ── 1. Auto-generated narrative + flags ─────────────────────────
    regime = snapshot.get("regime_summary") or {}
    parts.append(_render_narrative(regime))

    # ── 2. US Macro table (FRED 5종) ────────────────────────────────
    us_macro = snapshot.get("us_macro") or {}
    parts.append(_render_us_macro(us_macro))

    # ── 3. Global Outlook table (IMF) ───────────────────────────────
    global_outlook = snapshot.get("global_outlook") or {}
    parts.append(_render_global_outlook(global_outlook))

    # ── 4-pre. Sprint 1.2: ECB Eurozone snapshot (있을 때만) ──
    ecb_data = snapshot.get("ecb_eurozone") or {}
    if any(d.get("latest") for d in ecb_data.values()):
        parts.append(_render_ecb(ecb_data))

    # ── 4-pre. Sprint 1.2: World Bank demographic 비교 (있을 때만) ──
    wb_data = snapshot.get("wb_demographic") or {}
    if wb_data:
        parts.append(_render_wb(wb_data))

    # ── 4-pre. Sprint 1.2: OECD leading indicators (있을 때만) ──
    oecd_data = snapshot.get("oecd_leading") or {}
    if any(ind.get("data_by_country") for ind in oecd_data.values()):
        parts.append(_render_oecd(oecd_data))

    # ── 4-pre. Sprint 1.2: BIS credit cycle (있을 때만) ──
    bis_data = snapshot.get("bis_credit") or {}
    if any(ind.get("data_by_country") for ind in bis_data.values()):
        parts.append(_render_bis(bis_data))

    # ── 4. Sector-aware Impact Narrative (Sprint B-2 신설, 2026-05-28) ──
    # 종목이 속한 sector에 활성 macro factor가 어떤 영향을 미치는지 자동 분석
    if sector:
        try:
            # Lazy import — circular dependency 방지
            from macro_sector_impact import build_sector_impact_narrative
            sector_html = build_sector_impact_narrative(
                snapshot, sector=sector, ticker=ticker, company_name=company_name
            )
            if sector_html:
                parts.append(sector_html)
        except ImportError:
            pass  # macro_sector_impact 미설치 시 silent skip

    # ── 5. Data quality footer ──────────────────────────────────────
    dq = snapshot.get("data_quality") or {}
    parts.append(_render_data_quality(dq, snapshot.get("built_at", "?")))

    return "".join(parts)


# ──────────────────────────────────────────────────────────────────────
# Subsection renderers
# ──────────────────────────────────────────────────────────────────────
def _render_narrative(regime: Dict[str, Any]) -> str:
    narrative = regime.get("narrative") or "데이터 부족 — FRED/IMF fetch 실패"
    flags = regime.get("flags") or []

    flag_html = ""
    if flags:
        badges = []
        for f in flags:
            label, color, desc = FLAG_BADGES.get(f, (f, "#64748b", ""))
            badges.append(
                f'<span style="display:inline-block;background:{color};color:white;'
                f'padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600;'
                f'margin:2px 4px 2px 0;" title="{desc}">{label}</span>'
            )
        flag_html = (
            f'<div style="margin-top:10px;"><strong style="font-size:11px;color:#64748b;">'
            f'⚠️ Regime Flags:</strong> {"".join(badges)}</div>'
        )

    return (
        '<h2 style="font-size:15px;color:#0f172a;margin-top:16px;">'
        '[차트] Regime Summary (자동 생성)</h2>'
        f'<div style="background:#fefce8;border-left:3px solid #ca8a04;'
        f'padding:12px 16px;margin:8px 0;font-size:13px;line-height:1.6;">'
        f'{narrative}{flag_html}</div>'
    )


def _render_us_macro(us_macro: Dict[str, Any]) -> str:
    if not us_macro:
        return ""

    rows: List[str] = []
    field_order = ["unemployment", "cpi", "fed_funds", "yield_curve_2s10s", "us_10y"]
    for field in field_order:
        item = us_macro.get(field)
        if not item or not item.get("latest"):
            rows.append(
                f'<tr><td colspan="5" style="text-align:center;color:#94a3b8;font-style:italic;'
                f'padding:8px;">{item.get("label", field) if item else field}: 데이터 없음 '
                f'({item.get("source", "?") if item else "미설정"})</td></tr>'
            )
            continue

        latest = item["latest"]
        unit = item.get("unit", "")
        yoy = item.get("yoy_change")
        interp = item.get("interpretation") or {}
        regime_name = interp.get("regime", "-")
        regime_desc = interp.get("description", "-")

        # YoY change color
        yoy_html = "-"
        if yoy is not None:
            color = "#16a34a" if yoy < 0 and field == "fed_funds" else (
                "#dc2626" if yoy > 0 else "#64748b"
            )
            yoy_html = f'<span style="color:{color};font-weight:600;">{yoy:+.2f}%</span>'

        # Regime color
        regime_color = {
            "restrictive": "#dc2626",
            "high": "#dc2626",
            "inverted": "#991b1b",
            "neutral": "#0284c7",
            "normal": "#0284c7",
            "accommodative": "#16a34a",
            "ultra_low": "#16a34a",
            "low": "#16a34a",
            "flat": "#ca8a04",
            "steep": "#16a34a",
        }.get(regime_name, "#64748b")

        rows.append(
            f'<tr style="border-bottom:1px solid #e2e8f0;">'
            f'<td style="padding:8px 10px;font-weight:500;">{item["label"]}</td>'
            f'<td style="padding:8px 10px;text-align:right;font-family:monospace;font-size:13px;">'
            f'{latest["value"]}{unit}</td>'
            f'<td style="padding:8px 10px;text-align:right;">{yoy_html}</td>'
            f'<td style="padding:8px 10px;">'
            f'<span style="background:{regime_color};color:white;padding:2px 8px;'
            f'border-radius:8px;font-size:10px;font-weight:600;">{regime_name}</span></td>'
            f'<td style="padding:8px 10px;font-size:11px;color:#64748b;">{regime_desc}</td>'
            f'</tr>'
        )

    return (
        '<h2 style="font-size:15px;color:#0f172a;margin-top:18px;">'
        '[美] US Macro — FRED 5종 핵심 지표</h2>'
        '<table style="width:100%;border-collapse:collapse;margin-top:8px;font-size:12px;">'
        '<thead><tr style="background:#f1f5f9;text-align:left;">'
        '<th style="padding:8px 10px;font-weight:600;">지표</th>'
        '<th style="padding:8px 10px;text-align:right;font-weight:600;">최신값</th>'
        '<th style="padding:8px 10px;text-align:right;font-weight:600;">YoY 변화</th>'
        '<th style="padding:8px 10px;font-weight:600;">Regime</th>'
        '<th style="padding:8px 10px;font-weight:600;">의미</th>'
        '</tr></thead><tbody>'
        + "".join(rows) +
        '</tbody></table>'
    )


def _render_global_outlook(global_outlook: Dict[str, Any]) -> str:
    if not global_outlook:
        return ""

    rows: List[str] = []
    # Sort by GDP growth desc for visual hierarchy
    sorted_countries = sorted(
        global_outlook.items(),
        key=lambda kv: kv[1].get("gdp_growth_pct", -99) if isinstance(kv[1], dict) else -99,
        reverse=True,
    )

    for country, cdata in sorted_countries:
        if not isinstance(cdata, dict):
            continue
        flag = COUNTRY_FLAGS.get(country, "?")
        name = cdata.get("country_name_ko", country)
        latest_year = cdata.get("latest_year", "-")
        gdp = cdata.get("gdp_growth_pct")
        ca = cdata.get("current_account_pct_gdp")
        cpi = cdata.get("inflation_cpi_pct")
        debt = cdata.get("govt_debt_pct_gdp")

        def _fmt(v, suffix="%", positive_good=True):
            if v is None:
                return '<span style="color:#94a3b8;">N/A</span>'
            color = "#0f172a"  # default
            if positive_good and v > 0:
                color = "#16a34a"
            elif not positive_good and v < 0:
                color = "#16a34a"
            if (positive_good and v < 0) or (not positive_good and v > 0):
                color = "#dc2626"
            return f'<span style="color:{color};font-family:monospace;">{v:+.1f}{suffix}</span>'

        # Specific thresholds for color logic
        gdp_html = _fmt(gdp, positive_good=True) if gdp is not None else "N/A"
        ca_html = _fmt(ca, positive_good=True) if ca is not None else "N/A"
        cpi_html = (
            f'<span style="color:{"#dc2626" if cpi and cpi > 3 else "#0f172a"};font-family:monospace;">'
            f'{cpi:+.1f}%</span>' if cpi is not None else "N/A"
        )
        debt_html = (
            f'<span style="color:{"#dc2626" if debt and debt > 100 else "#0f172a"};font-family:monospace;">'
            f'{debt:.1f}%</span>' if debt is not None else "N/A"
        )

        rows.append(
            f'<tr style="border-bottom:1px solid #e2e8f0;">'
            f'<td style="padding:8px 10px;"><span style="display:inline-block;background:#0284c7;'
            f'color:white;width:24px;height:20px;text-align:center;border-radius:3px;'
            f'font-weight:700;font-size:11px;line-height:20px;">{flag}</span> '
            f'<strong>{name}</strong> <span style="color:#94a3b8;font-size:10px;">({country})</span></td>'
            f'<td style="padding:8px 10px;text-align:center;font-size:11px;color:#64748b;">{latest_year}</td>'
            f'<td style="padding:8px 10px;text-align:right;">{gdp_html}</td>'
            f'<td style="padding:8px 10px;text-align:right;">{ca_html}</td>'
            f'<td style="padding:8px 10px;text-align:right;">{cpi_html}</td>'
            f'<td style="padding:8px 10px;text-align:right;">{debt_html}</td>'
            f'</tr>'
        )

    return (
        '<h2 style="font-size:15px;color:#0f172a;margin-top:18px;">'
        '[글로벌] Global Outlook — IMF WEO 전망</h2>'
        '<table style="width:100%;border-collapse:collapse;margin-top:8px;font-size:12px;">'
        '<thead><tr style="background:#f1f5f9;text-align:left;">'
        '<th style="padding:8px 10px;font-weight:600;">국가</th>'
        '<th style="padding:8px 10px;text-align:center;font-weight:600;">기준 연도</th>'
        '<th style="padding:8px 10px;text-align:right;font-weight:600;">실질 GDP</th>'
        '<th style="padding:8px 10px;text-align:right;font-weight:600;">경상/GDP</th>'
        '<th style="padding:8px 10px;text-align:right;font-weight:600;">CPI</th>'
        '<th style="padding:8px 10px;text-align:right;font-weight:600;">정부부채/GDP</th>'
        '</tr></thead><tbody>'
        + "".join(rows) +
        '</tbody></table>'
        '<div style="font-size:10px;color:#94a3b8;margin-top:4px;">'
        '색상 코드: 녹색 = 우호적 · 빨강 = 우려 신호 (경상수지 적자/CPI > 3%/부채 > 100%)'
        '</div>'
    )


def _render_ecb(ecb_data: Dict[str, Any]) -> str:
    """Sprint 1.2: ECB 유로존 통화·인플레 snapshot."""
    rows = []
    for ind_id, payload in ecb_data.items():
        latest = payload.get("latest")
        if not latest:
            continue
        v = latest.get("value")
        unit = payload.get("unit", "")
        regime = (payload.get("interpretation") or {}).get("regime", "-")
        regime_desc = (payload.get("interpretation") or {}).get("description", "")
        regime_color = {
            "restrictive": "#dc2626", "neutral": "#0284c7", "accommodative": "#16a34a",
            "ultra_low": "#16a34a",
        }.get(regime, "#64748b")
        rows.append(
            f'<tr style="border-bottom:1px solid #e2e8f0;">'
            f'<td style="padding:8px 10px;font-weight:500;">{payload["label"]}</td>'
            f'<td style="padding:8px 10px;text-align:right;font-family:monospace;font-size:13px;">{v}{unit}</td>'
            f'<td style="padding:8px 10px;">'
            f'<span style="background:{regime_color};color:white;padding:2px 8px;'
            f'border-radius:8px;font-size:10px;font-weight:600;">{regime}</span></td>'
            f'<td style="padding:8px 10px;font-size:11px;color:#64748b;">{regime_desc}</td>'
            f'</tr>'
        )
    if not rows:
        return ""
    return (
        '<h2 style="font-size:15px;color:#0f172a;margin-top:18px;">'
        '[歐] Eurozone Macro — ECB SDW</h2>'
        '<table style="width:100%;border-collapse:collapse;margin-top:6px;font-size:12px;">'
        '<thead><tr style="background:#f1f5f9;text-align:left;">'
        '<th style="padding:8px 10px;font-weight:600;">지표</th>'
        '<th style="padding:8px 10px;text-align:right;font-weight:600;">최신값</th>'
        '<th style="padding:8px 10px;font-weight:600;">Regime</th>'
        '<th style="padding:8px 10px;font-weight:600;">의미</th>'
        '</tr></thead><tbody>' + "".join(rows) + '</tbody></table>'
    )


def _render_wb(wb_data: Dict[str, Any]) -> str:
    """Sprint 1.2: World Bank demographic·development 비교."""
    rows = []
    # Sort by GDP per capita descending
    sorted_countries = sorted(
        wb_data.items(),
        key=lambda kv: kv[1].get("gdp_per_capita_usd") or 0,
        reverse=True,
    )
    for country, cdata in sorted_countries:
        if not isinstance(cdata, dict):
            continue
        name = cdata.get("country_name_ko", country)
        gdp_pc = cdata.get("gdp_per_capita_usd")
        pop = cdata.get("population_millions")
        urb = cdata.get("urbanization_pct")
        exp = cdata.get("exports_pct_gdp")

        def _fmt(v, suffix="", precision=0):
            return f"{v:,.{precision}f}{suffix}" if v is not None else "N/A"

        rows.append(
            f'<tr style="border-bottom:1px solid #e2e8f0;">'
            f'<td style="padding:6px 10px;font-weight:500;">{name} <span style="color:#94a3b8;font-size:10px;">({country})</span></td>'
            f'<td style="padding:6px 10px;text-align:right;font-family:monospace;">${_fmt(gdp_pc)}</td>'
            f'<td style="padding:6px 10px;text-align:right;font-family:monospace;">{_fmt(pop, "M")}</td>'
            f'<td style="padding:6px 10px;text-align:right;font-family:monospace;">{_fmt(urb, "%", 1)}</td>'
            f'<td style="padding:6px 10px;text-align:right;font-family:monospace;">{_fmt(exp, "%", 1)}</td>'
            f'</tr>'
        )
    if not rows:
        return ""
    return (
        '<h2 style="font-size:15px;color:#0f172a;margin-top:18px;">'
        '[글로벌] Development Indicators — World Bank</h2>'
        '<div class="info" style="font-size:11px;color:#64748b;margin-bottom:6px;">'
        '국가별 발전 단계 (1인당 GDP)·인구·도시화율·수출 의존도. Jhunjhunwala·Dalio 페르소나의 '
        'demographic dividend·long-cycle anchor.'
        '</div>'
        '<table style="width:100%;border-collapse:collapse;margin-top:6px;font-size:12px;">'
        '<thead><tr style="background:#f1f5f9;text-align:left;">'
        '<th style="padding:6px 10px;font-weight:600;">국가</th>'
        '<th style="padding:6px 10px;text-align:right;font-weight:600;">1인당 GDP</th>'
        '<th style="padding:6px 10px;text-align:right;font-weight:600;">인구</th>'
        '<th style="padding:6px 10px;text-align:right;font-weight:600;">도시화율</th>'
        '<th style="padding:6px 10px;text-align:right;font-weight:600;">수출/GDP</th>'
        '</tr></thead><tbody>' + "".join(rows) + '</tbody></table>'
    )


def _render_oecd(oecd_data: Dict[str, Any]) -> str:
    """Sprint 1.2: OECD leading indicators.

    Sprint E-7 (2026-06): PDF render는 1-line summary로 축약.
    국가별 raw table은 페이지를 너무 많이 차지함 — 분석에는 macro_snapshot.json에서 활용.
    환경변수 OECD_FULL_TABLE=1로 full table 강제 가능.
    """
    import os as _os
    if not oecd_data:
        return ""

    # ── Full table mode (opt-in via env) ──
    if _os.environ.get("OECD_FULL_TABLE") == "1":
        rows = []
        for ind_id, payload in oecd_data.items():
            cdata_dict = payload.get("data_by_country") or {}
            if not cdata_dict:
                continue
            rows.append(
                f'<tr><td colspan="3" style="padding:6px 10px;background:#fafbfc;font-weight:600;">'
                f'{payload["label"]}</td></tr>'
            )
            for country, cd in cdata_dict.items():
                v = cd.get("latest_value")
                p = cd.get("latest_period")
                mom = cd.get("momentum_6m")
                regime = (cd.get("interpretation") or {}).get("regime", "-")
                mom_str = f" (6m: {mom:+.2f})" if mom is not None else ""
                rows.append(
                    f'<tr style="border-bottom:1px solid #e2e8f0;">'
                    f'<td style="padding:6px 10px;padding-left:24px;">{cd.get("country_name_ko", country)}</td>'
                    f'<td style="padding:6px 10px;text-align:right;font-family:monospace;">{p} = {v}{mom_str}</td>'
                    f'<td style="padding:6px 10px;font-size:11px;color:#64748b;">{regime}</td>'
                    f'</tr>'
                )
        if not rows:
            return ""
        return (
            '<h3 style="font-size:13px;color:#0f172a;margin-top:14px;">'
            'OECD Leading Indicators — 경기 선행 지수 (전체)</h3>'
            '<table style="width:100%;border-collapse:collapse;margin-top:6px;font-size:11px;">'
            '<tbody>' + "".join(rows) + '</tbody></table>'
        )

    # ── Default: 1-line summary (G-7 평균 regime만) ──
    summaries = []
    for ind_id, payload in oecd_data.items():
        cdata_dict = payload.get("data_by_country") or {}
        if not cdata_dict:
            continue
        regimes = [(cd.get("interpretation") or {}).get("regime", "") for cd in cdata_dict.values()]
        regimes = [r for r in regimes if r and r != "-"]
        if not regimes:
            continue
        # Most common regime
        from collections import Counter as _C
        top_regime, top_n = _C(regimes).most_common(1)[0]
        summaries.append(
            f"<li><strong>{payload['label']}</strong>: {len(cdata_dict)}국 중 {top_n}국 <em>{top_regime}</em></li>"
        )
    if not summaries:
        return ""
    return (
        '<h3 style="font-size:13px;color:#0f172a;margin-top:14px;">'
        'OECD Leading Indicators — 경기 선행 지수 요약</h3>'
        '<div class="info" style="font-size:10.5px;color:#64748b;margin-bottom:4px;">'
        'CLI 100=장기평균. 국가별 raw data는 macro_snapshot.json에서 활용 (PDF 인쇄 생략). '
        '전체 표 강제: <code>OECD_FULL_TABLE=1</code>'
        '</div>'
        f'<ul style="font-size:11px;line-height:1.7;margin:4pt 0 0 0;padding-left:18pt;">'
        f'{"".join(summaries)}</ul>'
    )


def _render_bis(bis_data: Dict[str, Any]) -> str:
    """Sprint 1.2: BIS 신용 사이클·REER."""
    rows = []
    for ind_id, payload in bis_data.items():
        cdata_dict = payload.get("data_by_country") or {}
        if not cdata_dict:
            continue
        rows.append(
            f'<tr><td colspan="3" style="padding:6px 10px;background:#fafbfc;font-weight:600;">'
            f'{payload["label"]}</td></tr>'
        )
        for country, cd in cdata_dict.items():
            v = cd.get("latest_value")
            p = cd.get("latest_period")
            regime = (cd.get("interpretation") or {}).get("regime", "-")
            regime_desc = (cd.get("interpretation") or {}).get("description", "")
            rows.append(
                f'<tr style="border-bottom:1px solid #e2e8f0;">'
                f'<td style="padding:6px 10px;padding-left:24px;">{cd.get("country_name_ko", country)}</td>'
                f'<td style="padding:6px 10px;text-align:right;font-family:monospace;">{p} = {v}{payload.get("unit", "")}</td>'
                f'<td style="padding:6px 10px;font-size:11px;color:#64748b;">{regime} — {regime_desc[:50]}</td>'
                f'</tr>'
            )
    if not rows:
        return ""
    return (
        '<h2 style="font-size:15px;color:#0f172a;margin-top:18px;">'
        '[글로벌] BIS Credit Cycle — Dalio Debt Cycle Anchor</h2>'
        '<div class="info" style="font-size:11px;color:#64748b;margin-bottom:6px;">'
        '국가별 총신용/GDP — Ray Dalio long-term debt cycle (50~75년) 위치 진단. '
        '250%+ = deleveraging 임박 신호.'
        '</div>'
        '<table style="width:100%;border-collapse:collapse;margin-top:6px;font-size:12px;">'
        '<tbody>' + "".join(rows) + '</tbody></table>'
    )


def _render_data_quality(dq: Dict[str, Any], built_at: str) -> str:
    fred_live = dq.get("fred_series_live", 0)
    fred_total = dq.get("fred_total", 5)
    imf_live = dq.get("imf_cells_live", 0)
    imf_total = dq.get("imf_cells_total", 0)
    imf_coverage = dq.get("imf_coverage_pct", 0)
    warning = dq.get("warning")

    quality_color = "#16a34a" if fred_live == fred_total and imf_coverage >= 90 else (
        "#ca8a04" if fred_live > 0 or imf_coverage >= 50 else "#dc2626"
    )

    warning_html = ""
    if warning:
        warning_html = (
            f'<div style="background:#fef3c7;border-left:3px solid #ca8a04;'
            f'padding:6px 12px;margin:4px 0;font-size:11px;color:#78350f;">⚠️ {warning}</div>'
        )

    return (
        f'<div style="margin-top:14px;padding:8px 12px;background:#f8fafc;'
        f'border-radius:4px;font-size:10px;color:#64748b;">'
        f'<strong style="color:{quality_color};">●</strong> Data quality: '
        f'FRED {fred_live}/{fred_total} live · IMF {imf_live}/{imf_total} cells '
        f'({imf_coverage}%) · Built at {built_at}'
        f'{warning_html}'
        f'</div>'
    )


# ──────────────────────────────────────────────────────────────────────
# Auto-fetch helper for build_combined.py
# ──────────────────────────────────────────────────────────────────────
def ensure_macro_snapshot(
    pipeline_dir: Path,
    stocks: List[Dict[str, Any]],
    force_refresh: bool = False,
) -> Optional[Dict[str, Any]]:
    """build_combined.py에서 호출되는 hook.

    pipeline_dir/macro_snapshot.json이 없으면 자동 생성, 있으면 로드.
    분석 종목의 ticker를 보고 국가 자동 추출.
    """
    import json
    snapshot_file = Path(pipeline_dir) / "macro_snapshot.json"

    if snapshot_file.exists() and not force_refresh:
        try:
            return json.loads(snapshot_file.read_text())
        except Exception as e:
            print(f"[macro_renderer] failed to load existing snapshot ({e}), regenerating")

    # Auto-fetch
    countries = resolve_countries_from_stocks(stocks)
    try:
        # Locate plugins/macro-economic-integration/scripts
        repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        macro_scripts = repo_root / "plugins" / "macro-economic-integration" / "scripts"
        if str(macro_scripts) not in sys.path:
            sys.path.insert(0, str(macro_scripts))
        from macro_dashboard import build_snapshot

        snapshot = build_snapshot(countries=countries, force_refresh=force_refresh)
        snapshot_file.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2))
        print(f"[macro_renderer] generated macro_snapshot.json (countries={countries})")
        return snapshot
    except Exception as e:
        print(f"[macro_renderer] auto-fetch failed: {e} — skipping macro section")
        return None


def resolve_countries_from_stocks(stocks: List[Dict[str, Any]]) -> List[str]:
    """종목 ticker → 국가 ISO3 코드 추출 (분석 대상 국가만 IMF fetch).

    Logic:
      • .KS / .KQ → KOR
      • .T (Tokyo) → JPN
      • .HK → CHN (HK)
      • .L (London) → GBR
      • .DE / .F (Frankfurt) → DEU
      • 그 외 (NYSE/NASDAQ) → USA
    + 항상 USA 포함 (글로벌 환율·금리 anchor)
    """
    countries = {"USA"}
    for s in stocks or []:
        t = (s.get("ticker") or "").upper()
        if t.endswith((".KS", ".KQ")):
            countries.add("KOR")
        elif t.endswith(".T"):
            countries.add("JPN")
        elif t.endswith(".HK"):
            countries.add("CHN")
        elif t.endswith(".L"):
            countries.add("GBR")
        elif t.endswith((".DE", ".F")):
            countries.add("DEU")
    # 한국 시장 관련 종목이 있을 가능성 높으므로 KOR 기본 포함
    if not any(c in countries for c in ("KOR", "JPN", "CHN")):
        countries.add("KOR")  # 우리 plugin은 한국 투자자 대상
    return sorted(countries)
