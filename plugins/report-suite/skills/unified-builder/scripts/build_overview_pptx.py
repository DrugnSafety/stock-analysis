#!/usr/bin/env python3
"""Layer 2 — Overview PPT (PowerPoint) builder.

8-10 slide deck — Cover, Thesis, Top 3 picks, Verdict 종합 표, Portfolio,
Risk + 결론. python-pptx 기반, 13.33×7.5 widescreen, Noto Sans CJK KR 폰트.

Usage:
  python build_overview_pptx.py \\
    --pipeline-dir .analysis-log/bloggers/{blogger}/{slug} \\
    --output overview.pptx
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = SCRIPT_DIR.parent.parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "skills" / "_common"))
from ticker_resolver import resolve_ticker  # type: ignore

# Color palette
NAVY = RGBColor(0x0D, 0x47, 0xA1)
BLUE = RGBColor(0x15, 0x65, 0xC0)
LIGHT = RGBColor(0xE3, 0xF2, 0xFD)
DARK = RGBColor(0x21, 0x21, 0x21)
GREEN = RGBColor(0x2E, 0x7D, 0x32)
ORANGE = RGBColor(0xEF, 0x6C, 0x00)
RED = RGBColor(0xC6, 0x28, 0x28)
GRAY = RGBColor(0x66, 0x66, 0x66)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

KOR_FONT = "Noto Sans CJK KR"


def _read_json(path: Path) -> dict | list:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def add_text(slide, left, top, width, height, text, *,
             size=18, bold=False, color=DARK, align=PP_ALIGN.LEFT, font=KOR_FONT):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = str(text)
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return tb


def add_filled_rect(slide, left, top, width, height, fill=NAVY):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    sh.line.fill.background()
    return sh


def add_bullets(slide, left, top, width, height, bullets, *, size=14, color=DARK):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    for i, b in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        run = p.add_run()
        run.text = "• " + str(b)
        run.font.name = KOR_FONT
        run.font.size = Pt(size)
        run.font.color.rgb = color
        p.space_after = Pt(4)


def build_pptx(pipeline_dir: Path, output_path: Path):
    meta = _read_json(pipeline_dir / "meta.json")
    thesis_data = _read_json(pipeline_dir / "thesis_list.json")
    theses = thesis_data.get("theses", [])

    decisions = (_read_json(pipeline_dir / "decisions.json") or {}).get("decisions", [])
    persona_aggs = _read_json(pipeline_dir / "persona_panel" / "_all_aggregates.json")

    prs = Presentation()
    prs.slide_width = Inches(13.33)
    prs.slide_height = Inches(7.5)

    title = meta.get("title", "분석 보고서")
    blog_url = meta.get("blog_url", "")
    blogger = meta.get("blogger", "")
    date = meta.get("date", "")

    # === Slide 1: Cover ===
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_filled_rect(s, 0, 0, prs.slide_width, prs.slide_height, fill=NAVY)
    add_text(s, Inches(0.7), Inches(0.8), Inches(12), Inches(0.5),
             f"블로거 분석 — {blogger}", size=18, color=WHITE)
    add_text(s, Inches(0.7), Inches(1.5), Inches(12), Inches(2),
             title[:80], size=32, bold=True, color=WHITE)
    add_text(s, Inches(0.7), Inches(4.5), Inches(12), Inches(0.4),
             f"원문: {blog_url}", size=12, color=LIGHT)
    add_text(s, Inches(0.7), Inches(5.0), Inches(12), Inches(0.4),
             f"발행일: {date} | 분석 종목: {len(decisions)} | 13명 페르소나 + 4-Analyst",
             size=12, color=LIGHT)

    # Top 3 banner
    sorted_decisions = sorted(decisions, key=lambda d: -abs(d.get("signal_score", 0)))[:3]
    medals = ["🥇", "🥈", "🥉"]
    top_text = " | ".join(
        f"{medals[i]} {d.get('ticker')} {resolve_ticker(d.get('ticker','')).get('kr','')[:6]} {d.get('action','').upper()} ({d.get('signal_score',0):+.2f})"
        for i, d in enumerate(sorted_decisions)
    )
    add_text(s, Inches(0.7), Inches(6.6), Inches(12), Inches(0.5),
             f"Top 3: {top_text}", size=11, color=WHITE)

    # === Slide 2: Thesis 3-line ===
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_filled_rect(s, 0, 0, prs.slide_width, Inches(0.7), fill=NAVY)
    add_text(s, Inches(0.5), Inches(0.13), Inches(12), Inches(0.5),
             "블로거 핵심 Thesis", size=24, bold=True, color=WHITE)

    core_theses = [t for t in theses if t.get("importance") == "core"][:3]
    if not core_theses:
        core_theses = theses[:3]
    positions = [(0.5, 1.0), (4.7, 1.0), (8.9, 1.0)]
    colors = [BLUE, GREEN, ORANGE]
    for i, (t, (x, y), col) in enumerate(zip(core_theses, positions, colors)):
        add_filled_rect(s, Inches(x), Inches(y), Inches(3.9), Inches(0.6), fill=col)
        add_text(s, Inches(x+0.2), Inches(y+0.1), Inches(3.6), Inches(0.5),
                 f"{i+1}. {t.get('claim_id', '')} ({t.get('importance', '')})",
                 size=14, bold=True, color=WHITE)
        add_text(s, Inches(x+0.2), Inches(y+0.8), Inches(3.6), Inches(4),
                 t.get('claim', ''), size=11, color=DARK)

    # Footer summary
    summary = thesis_data.get("summary_one_liner", "")[:200]
    if summary:
        add_filled_rect(s, Inches(0.5), Inches(6.0), Inches(12.3), Inches(0.9), fill=LIGHT)
        add_text(s, Inches(0.7), Inches(6.1), Inches(12), Inches(0.7),
                 f"💡 한 줄 요약: {summary}", size=12, bold=True, color=NAVY)

    # === Slide 3: Top 3 picks (3 column detail) ===
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_filled_rect(s, 0, 0, prs.slide_width, Inches(0.7), fill=NAVY)
    add_text(s, Inches(0.5), Inches(0.13), Inches(12), Inches(0.5),
             "Top 3 Picks (signal 절대값 기준)", size=24, bold=True, color=WHITE)

    for i, d in enumerate(sorted_decisions):
        ticker = d.get("ticker", "")
        info = resolve_ticker(ticker)
        name = info.get("kr", ticker)
        sector = info.get("sector", "")
        action = d.get("action", "-").upper()
        signal = d.get("signal_score", 0)
        agg = persona_aggs.get(ticker, {})
        avg_conf = agg.get("average_confidence", 0)
        dist = agg.get("verdict_distribution", {})
        bull = dist.get("lean_bullish", {}).get("count", 0)
        neu = dist.get("neutral", {}).get("count", 0)
        bear = dist.get("lean_bearish", {}).get("count", 0)
        risk = (d.get("primary_risks") or [""])[0][:120]
        action_color = GREEN if action == "BUY" else RED if action.startswith("SELL") else ORANGE

        x = 0.5 + i * 4.3
        # Header
        add_filled_rect(s, Inches(x), Inches(1.0), Inches(4.0), Inches(0.7), fill=action_color)
        add_text(s, Inches(x+0.15), Inches(1.05), Inches(0.6), Inches(0.6),
                 medals[i], size=24, color=WHITE)
        add_text(s, Inches(x+0.95), Inches(1.0), Inches(3), Inches(0.4),
                 ticker, size=15, bold=True, color=WHITE)
        add_text(s, Inches(x+0.95), Inches(1.4), Inches(3), Inches(0.3),
                 name[:18], size=11, color=WHITE)

        # Body
        add_filled_rect(s, Inches(x), Inches(1.7), Inches(4.0), Inches(0.5), fill=LIGHT)
        add_text(s, Inches(x+0.2), Inches(1.75), Inches(3.6), Inches(0.4),
                 f"{action} · Signal {signal:+.2f} · 신뢰도 {avg_conf*100:.0f}%",
                 size=12, bold=True, color=NAVY)

        add_filled_rect(s, Inches(x), Inches(2.2), Inches(4.0), Inches(3.7), fill=WHITE)
        add_text(s, Inches(x+0.15), Inches(2.3), Inches(3.7), Inches(0.4),
                 f"매수 {bull} / 중립 {neu} / 매도 {bear}",
                 size=11, bold=True, color=DARK)
        add_text(s, Inches(x+0.15), Inches(2.7), Inches(3.7), Inches(0.4),
                 f"Sector: {sector[:30]}", size=10, color=GRAY)
        add_text(s, Inches(x+0.15), Inches(3.2), Inches(3.7), Inches(2),
                 f"핵심 risk:\n{risk}", size=10, color=DARK)

    add_filled_rect(s, Inches(0.5), Inches(6.5), Inches(12.3), Inches(0.5), fill=LIGHT)
    add_text(s, Inches(0.7), Inches(6.55), Inches(12), Inches(0.4),
             "📊 Layer 1 (per-stock 44p PDF)에 페르소나별 reasoning 상세 포함",
             size=11, color=NAVY)

    # === Slide 4: 전체 Verdict 종합 표 ===
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_filled_rect(s, 0, 0, prs.slide_width, Inches(0.7), fill=NAVY)
    add_text(s, Inches(0.5), Inches(0.13), Inches(12), Inches(0.5),
             f"전체 {len(decisions)}종목 Verdict 종합", size=24, bold=True, color=WHITE)

    # Headers
    cols = ["#", "Ticker", "종목명", "Sector", "Bull/Neu/Bear", "Conf", "Action", "Signal"]
    col_widths = [0.5, 1.5, 2.3, 3.0, 1.6, 0.8, 1.2, 1.6]
    header_y = 1.0
    x_cum = 0.5
    for c, w in zip(cols, col_widths):
        add_filled_rect(s, Inches(x_cum), Inches(header_y), Inches(w), Inches(0.4), fill=BLUE)
        add_text(s, Inches(x_cum+0.05), Inches(header_y+0.05), Inches(w-0.1), Inches(0.3),
                 c, size=11, bold=True, color=WHITE)
        x_cum += w

    for i, d in enumerate(decisions[:11]):
        ticker = d.get("ticker", "")
        info = resolve_ticker(ticker)
        name = info.get("kr", ticker)[:14]
        sector = info.get("sector", "")[:30]
        agg = persona_aggs.get(ticker, {})
        dist = agg.get("verdict_distribution", {})
        bull = dist.get("lean_bullish", {}).get("count", 0)
        neu = dist.get("neutral", {}).get("count", 0)
        bear = dist.get("lean_bearish", {}).get("count", 0)
        avg_conf = agg.get("average_confidence", 0)
        action = d.get("action", "-").upper()
        signal = d.get("signal_score", 0)
        is_buy = action == "BUY"
        is_sell = action.startswith("SELL")
        col = GREEN if is_buy else RED if is_sell else ORANGE

        row = [str(i+1), ticker, name, sector, f"{bull}/{neu}/{bear}",
               f"{avg_conf*100:.0f}%", action, f"{signal:+.2f}"]
        y = header_y + 0.45 + i * 0.45
        bg = LIGHT if i % 2 == 0 else WHITE
        x_cum = 0.5
        for cell, w in zip(row, col_widths):
            add_filled_rect(s, Inches(x_cum), Inches(y), Inches(w), Inches(0.4), fill=bg)
            cell_color = col if cell in (action, f"{signal:+.2f}") else DARK
            cell_bold = cell in (action,)
            add_text(s, Inches(x_cum+0.05), Inches(y+0.06), Inches(w-0.1), Inches(0.3),
                     cell, size=10, bold=cell_bold, color=cell_color)
            x_cum += w

    # === Slide 5: Portfolio Allocation ===
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_filled_rect(s, 0, 0, prs.slide_width, Inches(0.7), fill=NAVY)
    add_text(s, Inches(0.5), Inches(0.13), Inches(12), Inches(0.5),
             "Portfolio Allocation 권고", size=24, bold=True, color=WHITE)

    buy_decisions = [d for d in decisions if d.get("action") == "buy"]
    total_target = sum(d.get("target_value", 0) for d in buy_decisions)
    sell_decisions = [d for d in decisions if d.get("action", "").startswith("sell")]

    add_text(s, Inches(0.5), Inches(1.0), Inches(12), Inches(0.5),
             f"BUY 종목 ({len(buy_decisions)}개)  |  Total target value: ₩{total_target:,}",
             size=16, bold=True, color=GREEN)

    for i, d in enumerate(buy_decisions[:8]):
        ticker = d.get("ticker", "")
        info = resolve_ticker(ticker)
        name = info.get("kr", ticker)
        val = d.get("target_value", 0)
        signal = d.get("signal_score", 0)
        pct = (val / total_target * 100) if total_target else 0

        y = 1.6 + i * 0.55
        add_filled_rect(s, Inches(0.5), Inches(y), Inches(0.15), Inches(0.45), fill=GREEN)
        add_text(s, Inches(0.7), Inches(y), Inches(3), Inches(0.45),
                 f"{ticker} {name[:14]}", size=12, bold=True, color=DARK)
        add_text(s, Inches(3.7), Inches(y), Inches(2), Inches(0.45),
                 f"signal {signal:+.2f}", size=11, color=GRAY)
        # Bar
        bar_w = max(0.5, min(7, pct / 100 * 7))
        add_filled_rect(s, Inches(5.7), Inches(y+0.08), Inches(bar_w), Inches(0.3), fill=GREEN)
        add_text(s, Inches(5.7+bar_w+0.1), Inches(y+0.05), Inches(2), Inches(0.4),
                 f"₩{val:,.0f} ({pct:.0f}%)", size=11, bold=True, color=DARK)

    if sell_decisions:
        y = 1.6 + len(buy_decisions[:8]) * 0.55 + 0.3
        add_text(s, Inches(0.5), Inches(y), Inches(12), Inches(0.4),
                 f"⚠ SELL 종목 ({len(sell_decisions)}): " +
                 ", ".join(f"{d.get('ticker')} ({resolve_ticker(d.get('ticker','')).get('kr','')[:8]})"
                            for d in sell_decisions),
                 size=12, bold=True, color=RED)

    # === Slide 6: Risk + 결론 ===
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_filled_rect(s, 0, 0, prs.slide_width, Inches(0.7), fill=NAVY)
    add_text(s, Inches(0.5), Inches(0.13), Inches(12), Inches(0.5),
             "핵심 Risk + 결론", size=24, bold=True, color=WHITE)

    # Aggregate top 5 risks
    all_risks = []
    seen = set()
    for d in decisions:
        for r in d.get("primary_risks", []):
            key = r[:50]
            if key not in seen:
                seen.add(key)
                all_risks.append(r)

    add_text(s, Inches(0.5), Inches(1.0), Inches(6), Inches(0.4),
             "주요 Risk 요인", size=18, bold=True, color=RED)
    add_bullets(s, Inches(0.5), Inches(1.5), Inches(6), Inches(4),
                all_risks[:5], size=12, color=DARK)

    # Conclusion
    add_text(s, Inches(7), Inches(1.0), Inches(6), Inches(0.4),
             "분석 결론", size=18, bold=True, color=GREEN)
    n_buy = sum(1 for d in decisions if d.get("action") == "buy")
    n_hold = sum(1 for d in decisions if d.get("action") == "hold")
    n_sell = sum(1 for d in decisions if d.get("action", "").startswith("sell"))
    conclusions = [
        f"분석 종목 {len(decisions)}개: BUY {n_buy} / HOLD {n_hold} / SELL {n_sell}",
        f"Top pick: {sorted_decisions[0].get('ticker') if sorted_decisions else '-'}",
        "Layer 1 (per-stock 44p PDF) 참조 권고",
        "분기 thesis 검증 + 가격 monitoring",
        "변동성 30%+ 종목은 분할 매수 권장",
    ]
    add_bullets(s, Inches(7), Inches(1.5), Inches(6), Inches(4),
                conclusions, size=12, color=DARK)

    # Disclaimer
    add_text(s, Inches(0.5), Inches(7.0), Inches(12), Inches(0.3),
             "본 보고서는 paper portfolio simulation 자료이며 투자 권유가 아닙니다.",
             size=9, color=GRAY, align=PP_ALIGN.CENTER)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(output_path))
    return len(prs.slides)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pipeline-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    n = build_pptx(Path(args.pipeline_dir), Path(args.output))
    import os
    print(f"[pptx] saved {args.output} ({n} slides, {os.path.getsize(args.output):,} bytes)")


if __name__ == "__main__":
    main()
