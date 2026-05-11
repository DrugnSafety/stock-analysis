#!/usr/bin/env python3
"""Layer 2 — Overview PPT v2 (McKinsey-style design system).

업그레이드 포인트:
* 16:9 (13.33×7.5) 전용
* Master template 패턴 — chapter ribbon(상단)·title·subtitle·body 위치 모든 slide 동일
* Pyramid Principle — top message 먼저, supporting evidence
* 10-12 slides (현재 6 slides → 확장)
* 매 slide 하단 body 영역 visual element 충실 (chart/table/icon/quote)
* Persona quote slide 추가
* AI-slop 회피 (no accent line under title, no decorative full-width bars)
* anthropic-skills:pptx 디자인 규칙 + theme-factory "Forest Canopy" earth tone 채택

Usage:
  python build_overview_pptx_v2.py \\
    --pipeline-dir .analysis-log/bloggers/{blogger}/{slug} \\
    --output overview.pptx
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = SCRIPT_DIR.parent.parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "skills" / "_common"))
from ticker_resolver import resolve_ticker  # type: ignore

# ── Theme: "Forest Canopy" (earth tones, Tech-Innovation accent) ──────────
# Rare earth/mining 주제에 어울리는 deep green + accent gold + neutrals
DEEP_FOREST = RGBColor(0x1F, 0x37, 0x2E)   # primary dark — title/cover bg
MOSS = RGBColor(0x2C, 0x5F, 0x4A)          # secondary
SAGE = RGBColor(0x9C, 0xB7, 0x9F)          # tertiary
GOLD = RGBColor(0xC9, 0x9A, 0x3B)          # accent (REE rarity 상징)
CREAM = RGBColor(0xF7, 0xF4, 0xEC)         # body bg — soft, not white
INK = RGBColor(0x1A, 0x1A, 0x1A)           # body text
GRAY = RGBColor(0x6E, 0x6E, 0x6E)          # caption text
LIGHT_GRAY = RGBColor(0xD8, 0xD8, 0xD8)    # divider
BULL = RGBColor(0x2E, 0x7D, 0x32)          # green for bullish
NEU = RGBColor(0x6E, 0x6E, 0x6E)
BEAR = RGBColor(0xC6, 0x28, 0x28)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

# Typography — anthropic-skills:pptx 권장 (Georgia + Calibri 페어링 변형 → Korean fallback)
HEADER_FONT = "Noto Sans CJK KR"
BODY_FONT = "Noto Sans CJK KR"

# ── Master layout coordinates (16:9 = 13.33"×7.5") — 모든 slide에서 동일 위치 ──
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

# Chapter ribbon (top edge — fixed across slides)
CHAPTER_TOP = Inches(0.30)
CHAPTER_LEFT = Inches(0.50)
CHAPTER_W = Inches(12.33)
CHAPTER_H = Inches(0.30)

# Title block (just below chapter ribbon)
TITLE_TOP = Inches(0.75)
TITLE_LEFT = Inches(0.50)
TITLE_W = Inches(12.33)
TITLE_H = Inches(0.85)

# Subtitle (single line below title — pyramid principle TOP MESSAGE)
SUB_TOP = Inches(1.65)
SUB_LEFT = Inches(0.50)
SUB_W = Inches(12.33)
SUB_H = Inches(0.55)

# Body region — start
BODY_TOP = Inches(2.30)
BODY_LEFT = Inches(0.50)
BODY_W = Inches(12.33)
BODY_H = Inches(4.55)

# Footer (page number, source)
FOOTER_TOP = Inches(7.00)
FOOTER_LEFT = Inches(0.50)
FOOTER_W = Inches(12.33)
FOOTER_H = Inches(0.30)


def _read_json(path: Path) -> dict | list:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


# ── Primitives ────────────────────────────────────────────────────────────
def add_text(slide, left, top, width, height, text, *, size=14, bold=False,
             color=INK, align=PP_ALIGN.LEFT, font=BODY_FONT,
             anchor=MSO_ANCHOR.TOP, italic=False):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Emu(0)
    tf.margin_right = Emu(0)
    tf.margin_top = Emu(0)
    tf.margin_bottom = Emu(0)
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = str(text)
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return tb


def add_rect(slide, left, top, width, height, fill, line=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
        shape.line.width = Pt(0.75)
    return shape


def add_circle(slide, left, top, diameter, fill, line=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.OVAL, left, top, diameter, diameter)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
    return shape


def add_chapter_ribbon(slide, chapter_text):
    """모든 slide 상단 — 작고 절제된 chapter breadcrumb (no full-width bar)."""
    # 좌측 small accent dot
    dot = Inches(0.10)
    add_circle(slide, CHAPTER_LEFT, CHAPTER_TOP + Inches(0.10), dot, GOLD)
    # chapter text
    add_text(slide, CHAPTER_LEFT + Inches(0.20), CHAPTER_TOP, CHAPTER_W,
             CHAPTER_H, chapter_text, size=10, color=GRAY, font=BODY_FONT,
             anchor=MSO_ANCHOR.MIDDLE)


def add_title(slide, title, subtitle):
    """Title + subtitle — pyramid principle TOP MESSAGE 통합 영역."""
    add_text(slide, TITLE_LEFT, TITLE_TOP, TITLE_W, TITLE_H, title,
             size=32, bold=True, color=DEEP_FOREST, font=HEADER_FONT,
             anchor=MSO_ANCHOR.TOP)
    if subtitle:
        add_text(slide, SUB_LEFT, SUB_TOP, SUB_W, SUB_H, subtitle,
                 size=15, color=MOSS, font=BODY_FONT, italic=True,
                 anchor=MSO_ANCHOR.TOP)


def add_footer(slide, page_num, total_pages, source_label="rare-earth refining bottleneck"):
    """페이지 번호 + 출처 작게."""
    add_text(slide, FOOTER_LEFT, FOOTER_TOP, Inches(8), FOOTER_H,
             source_label, size=9, color=GRAY, font=BODY_FONT,
             anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, FOOTER_LEFT + Inches(8.5), FOOTER_TOP, Inches(3.83),
             FOOTER_H, f"{page_num:02d} / {total_pages:02d}", size=9,
             color=GRAY, align=PP_ALIGN.RIGHT, font=BODY_FONT,
             anchor=MSO_ANCHOR.MIDDLE)


def base_slide(prs, chapter, title, subtitle, page_num, total_pages):
    """모든 content slide는 이 함수로 시작 — master layout 효과."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    # background — cream (not white)
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
    bg.fill.solid()
    bg.fill.fore_color.rgb = CREAM
    bg.line.fill.background()

    # chapter ribbon
    add_chapter_ribbon(slide, chapter)
    # title block
    add_title(slide, title, subtitle)
    # footer
    add_footer(slide, page_num, total_pages)
    return slide


def cover_slide(prs, meta):
    """Slide 1 — Cover (deep forest bg, dramatic)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
    bg.fill.solid()
    bg.fill.fore_color.rgb = DEEP_FOREST
    bg.line.fill.background()

    # accent: 우측 상단 gold rectangle (visual motif = dot+rectangle 결합)
    add_rect(slide, Inches(11.5), Inches(0.6), Inches(1.3), Inches(0.08), GOLD)
    add_circle(slide, Inches(11.5) - Inches(0.14), Inches(0.66) - Inches(0.04),
               Inches(0.16), GOLD)

    # category small
    add_text(slide, Inches(0.7), Inches(0.7), Inches(8), Inches(0.4),
             "INVESTMENT RESEARCH · RARE EARTH REFINING", size=10,
             color=GOLD, bold=True, font=BODY_FONT)

    # main title (large)
    add_text(slide, Inches(0.7), Inches(2.1), Inches(11.9), Inches(2.0),
             "보이지 않는 원소가 만드는\n보이지 않는 위기",
             size=48, bold=True, color=WHITE, font=HEADER_FONT)

    # subtitle
    add_text(slide, Inches(0.7), Inches(4.3), Inches(11.9), Inches(0.7),
             "진짜 병목은 정제다 — 비중국 정제 vertical 기업의 mispricing alpha",
             size=18, color=SAGE, italic=True, font=BODY_FONT)

    # divider line (subtle, not full-width)
    add_rect(slide, Inches(0.7), Inches(5.3), Inches(2.0), Inches(0.04), GOLD)

    # blogger + date + page
    add_text(slide, Inches(0.7), Inches(5.5), Inches(11.9), Inches(0.4),
             f"블로거: {meta.get('blog_author', 'happy')} (dhgusdnd44) · 시리즈: {meta.get('series', '희토류 3부작')}",
             size=13, color=SAGE, font=BODY_FONT)
    add_text(slide, Inches(0.7), Inches(5.95), Inches(11.9), Inches(0.4),
             f"분석 작성일: 2026-05-07 · 13명 페르소나 패널 + 4-Analyst + Deep Research",
             size=12, color=SAGE, font=BODY_FONT)

    # 13명 페르소나 dot row (visual motif)
    base_left = Inches(0.7)
    base_top = Inches(6.7)
    dot_d = Inches(0.18)
    gap = Inches(0.30)
    for i in range(13):
        add_circle(slide, base_left + (dot_d + Inches(0.04)) * i, base_top, dot_d,
                   GOLD if i < 5 else SAGE)
    add_text(slide, Inches(0.7) + (dot_d + Inches(0.04)) * 13 + Inches(0.2),
             base_top - Inches(0.04), Inches(7), Inches(0.3),
             "Buffett · Munger · Lynch · Wood · Burry · Taleb · Graham · Ackman · Pabrai · Fisher · Jhunjhunwala · Druckenmiller · Damodaran",
             size=8, color=SAGE, font=BODY_FONT)
    return slide


def thesis_slide(prs, theses, page, total):
    """Slide 2 — 핵심 Thesis (top 5 + 시각적 importance grid)."""
    slide = base_slide(prs, "01 · 핵심 Thesis",
                       "정제 병목론 — 시장은 채굴을 보지만 진짜 병목은 정제다",
                       "중국 점유율 채굴 60% → 정제 91% → 자석 94% · 시장은 광산에 프리미엄 부여 中, 알파는 정제 기업에 있다",
                       page, total)
    # 5 theses cards in 2x3 grid (top 5 importance)
    top_th = sorted(theses, key=lambda t: 0 if t.get('importance', '').startswith('crit') else 1)[:5]

    card_w = Inches(2.40)
    card_h = Inches(2.10)
    gap = Inches(0.10)
    row1_top = BODY_TOP + Inches(0.10)
    row2_top = row1_top + card_h + Inches(0.15)
    positions = [
        (BODY_LEFT, row1_top),
        (BODY_LEFT + card_w + gap, row1_top),
        (BODY_LEFT + (card_w + gap) * 2, row1_top),
        (BODY_LEFT + (card_w + gap) * 3, row1_top),
        (BODY_LEFT + (card_w + gap) * 4, row1_top),
    ]
    for i, t in enumerate(top_th[:5]):
        if i >= len(positions):
            break
        left, top = positions[i]
        # card border (subtle)
        add_rect(slide, left, top, card_w, card_h, CREAM, line=LIGHT_GRAY)
        # T-id corner badge
        add_rect(slide, left, top, Inches(0.6), Inches(0.30), DEEP_FOREST)
        add_text(slide, left, top, Inches(0.6), Inches(0.30),
                 t.get('id', f'T{i+1}'), size=10, bold=True, color=WHITE,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                 font=BODY_FONT)
        # title
        add_text(slide, left + Inches(0.08), top + Inches(0.40),
                 card_w - Inches(0.16), Inches(0.85),
                 t.get('title', '')[:55], size=11, bold=True,
                 color=DEEP_FOREST, font=HEADER_FONT)
        # claim 일부
        claim = t.get('claim', '')[:130] + ('...' if len(t.get('claim','')) > 130 else '')
        add_text(slide, left + Inches(0.08), top + Inches(1.20),
                 card_w - Inches(0.16), Inches(0.85),
                 claim, size=9, color=INK, font=BODY_FONT)
    # Below: thesis count summary
    add_text(slide, BODY_LEFT, row2_top + card_h - Inches(0.05), BODY_W,
             Inches(0.40), f"※ 총 추출 thesis: {len(theses)}개 · 4-Analyst (Macro/Industry/Empirical/Counter) lens로 평가 — 7건 강한 합의, 3건 mixed, 0건 강한 반박",
             size=10, italic=True, color=GRAY, font=BODY_FONT)


def top_picks_slide(prs, picks_data, page, total):
    """Slide 3 — Top 5 종목 verdict + 비중 (visual chart)."""
    slide = base_slide(prs, "02 · Top 5 Picks",
                       "Lynas 4.08 / MP 3.62 / Iluka 3.42 — 비중국 정제 vertical 우세",
                       "13명 페르소나 weighted score (1=very_bearish ~ 5=very_bullish) · 정제 vertical 기업이 alpha source 정렬",
                       page, total)
    # Bar chart 형태 시각화 (수동)
    headers = ["순위", "Ticker", "종목명", "Score", "Verdict 분포 (B/N/Br)", "Action"]
    col_w = [Inches(0.65), Inches(1.30), Inches(2.50), Inches(1.20), Inches(4.20), Inches(2.48)]
    col_x = [BODY_LEFT]
    for w in col_w[:-1]:
        col_x.append(col_x[-1] + w)

    # header row
    hdr_top = BODY_TOP + Inches(0.10)
    add_rect(slide, BODY_LEFT, hdr_top, BODY_W, Inches(0.40), DEEP_FOREST)
    for i, h in enumerate(headers):
        add_text(slide, col_x[i], hdr_top, col_w[i], Inches(0.40), h,
                 size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER,
                 anchor=MSO_ANCHOR.MIDDLE, font=BODY_FONT)
    # rows
    medals = ["1st", "2nd", "3rd", "4", "5"]
    for i, p in enumerate(picks_data):
        row_top = hdr_top + Inches(0.45) + Inches(0.65) * i
        # alternate background
        if i % 2 == 0:
            add_rect(slide, BODY_LEFT, row_top, BODY_W, Inches(0.60), WHITE)
        add_text(slide, col_x[0], row_top, col_w[0], Inches(0.60),
                 medals[i] if i < 3 else str(i+1), size=14, bold=True,
                 color=GOLD if i < 3 else GRAY, align=PP_ALIGN.CENTER,
                 anchor=MSO_ANCHOR.MIDDLE, font=BODY_FONT)
        add_text(slide, col_x[1], row_top, col_w[1], Inches(0.60),
                 p['ticker'], size=11, bold=True, color=DEEP_FOREST,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                 font=BODY_FONT)
        add_text(slide, col_x[2], row_top, col_w[2], Inches(0.60),
                 p['name'][:18], size=11, color=INK, anchor=MSO_ANCHOR.MIDDLE,
                 font=BODY_FONT)
        # score 시각화 (bar)
        score_w = (p['score'] / 5.0) * (col_w[3].emu - Inches(0.25).emu)
        add_rect(slide, col_x[3] + Inches(0.10), row_top + Inches(0.20),
                 Emu(int(score_w)), Inches(0.20),
                 BULL if p['score'] >= 3.5 else (NEU if p['score'] >= 3.0 else BEAR))
        add_text(slide, col_x[3], row_top + Inches(0.40), col_w[3],
                 Inches(0.20), f"{p['score']:.2f}", size=9, color=GRAY,
                 align=PP_ALIGN.CENTER, font=BODY_FONT)
        # verdict 분포 (3 colored boxes side by side)
        b, n, br = p['bull'], p['neu'], p['bear']
        total_v = b + n + br
        if total_v > 0:
            seg_w = (col_w[4].emu - Inches(0.20).emu)
            bw = Emu(int(seg_w * b / total_v))
            nw = Emu(int(seg_w * n / total_v))
            brw = Emu(int(seg_w * br / total_v))
            add_rect(slide, col_x[4] + Inches(0.10), row_top + Inches(0.18),
                     bw, Inches(0.24), BULL)
            add_rect(slide, col_x[4] + Inches(0.10) + bw, row_top + Inches(0.18),
                     nw, Inches(0.24), NEU)
            add_rect(slide, col_x[4] + Inches(0.10) + bw + nw, row_top + Inches(0.18),
                     brw, Inches(0.24), BEAR)
            add_text(slide, col_x[4], row_top + Inches(0.42), col_w[4],
                     Inches(0.18), f"{b}/{n}/{br} · 신뢰도 {int(p['conf']*100)}%",
                     size=9, color=GRAY, align=PP_ALIGN.CENTER, font=BODY_FONT)
        add_text(slide, col_x[5], row_top, col_w[5], Inches(0.60),
                 p['action'], size=11, bold=True,
                 color=BULL if 'BUY' in p['action'] else GRAY,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                 font=BODY_FONT)

    # bottom callout
    add_text(slide, BODY_LEFT, BODY_TOP + Inches(4.10), BODY_W, Inches(0.45),
             "✱ Lynas는 13명 중 Ackman/Fisher 0.85, Druckenmiller/Taleb 0.80 — highest conviction 기록",
             size=11, italic=True, bold=True, color=GOLD, font=BODY_FONT)


def market_data_slide(prs, stocks, page, total):
    """Slide 4 — Live Market Data (yfinance 2026-05-07)."""
    slide = base_slide(prs, "03 · Market Data",
                       "1년 수익률 +108~193% — 모든 종목 폭등 cycle 진입",
                       "yfinance live 2026-05-07 · 비중국 player 모두 momentum, 단 valuation 부담은 종목별 차이",
                       page, total)
    # 5 stat cards (large numbers + small labels)
    card_w = Inches(2.40)
    card_h = Inches(1.55)
    gap = Inches(0.10)
    top1 = BODY_TOP + Inches(0.10)
    top2 = top1 + card_h + Inches(0.20)

    for i, s in enumerate(stocks[:5]):
        col = i
        left = BODY_LEFT + (card_w + gap) * col
        add_rect(slide, left, top1, card_w, card_h, WHITE, line=LIGHT_GRAY)
        # ticker badge
        add_rect(slide, left + Inches(0.10), top1 + Inches(0.10),
                 Inches(1.0), Inches(0.30), DEEP_FOREST)
        add_text(slide, left + Inches(0.10), top1 + Inches(0.10),
                 Inches(1.0), Inches(0.30), s['ticker'][:9], size=10,
                 bold=True, color=WHITE, align=PP_ALIGN.CENTER,
                 anchor=MSO_ANCHOR.MIDDLE, font=BODY_FONT)
        # 1Y return (large)
        ret = s['ret_1y']
        add_text(slide, left + Inches(0.10), top1 + Inches(0.50),
                 card_w - Inches(0.20), Inches(0.55),
                 f"+{ret:.0f}%", size=28, bold=True,
                 color=BULL if ret >= 0 else BEAR, font=HEADER_FONT)
        add_text(slide, left + Inches(0.10), top1 + Inches(1.05),
                 card_w - Inches(0.20), Inches(0.20),
                 "1Y return", size=9, color=GRAY, font=BODY_FONT)
        add_text(slide, left + Inches(0.10), top1 + Inches(1.25),
                 card_w - Inches(0.20), Inches(0.25),
                 f"{s['price']:.2f} {s['currency']} · 시총 ${s['mcap']:.1f}B",
                 size=9, color=INK, font=BODY_FONT)
    # 2nd row: PE / Vol / Beta
    metrics = [("Forward PE", "fwd_pe", "x"), ("Vol annualized", "vol", "%"),
               ("Beta", "beta", ""), ("Score (페르소나)", "score", "/5"),
               ("매수 신뢰도", "conf", "%")]
    for i, s in enumerate(stocks[:5]):
        col = i
        left = BODY_LEFT + (card_w + gap) * col
        add_rect(slide, left, top2, card_w, card_h, WHITE, line=LIGHT_GRAY)
        add_text(slide, left + Inches(0.10), top2 + Inches(0.10),
                 card_w - Inches(0.20), Inches(0.30),
                 f"{resolve_ticker(s['ticker']).get('kr', s['ticker'])[:14]}",
                 size=10, bold=True, color=DEEP_FOREST, font=BODY_FONT)
        # micro data row (3 mini stats)
        pe_str = f"{s['fwd_pe']:.1f}x" if s['fwd_pe'] > 0 else "적자"
        line2 = f"PE {pe_str}  ·  vol {s['vol']:.0f}%  ·  β {s['beta']:.2f}"
        add_text(slide, left + Inches(0.10), top2 + Inches(0.45),
                 card_w - Inches(0.20), Inches(0.30),
                 line2, size=10, color=INK, font=BODY_FONT)
        score = s.get('score', 0)
        # mini score bar
        bar_w_total = Emu(card_w - Inches(0.30))
        add_rect(slide, left + Inches(0.10), top2 + Inches(0.85),
                 bar_w_total, Inches(0.06), LIGHT_GRAY)
        fill_w = Emu(int(bar_w_total * score / 5.0))
        add_rect(slide, left + Inches(0.10), top2 + Inches(0.85), fill_w,
                 Inches(0.06), GOLD)
        add_text(slide, left + Inches(0.10), top2 + Inches(0.95),
                 card_w - Inches(0.20), Inches(0.30),
                 f"페르소나 score {score:.2f}/5  ·  {s.get('action', '-')[:14]}",
                 size=9, color=GRAY, font=BODY_FONT)


def thesis_eval_slide(prs, eval_data, page, total):
    """Slide 5 — 4-Analyst 평가 합의도."""
    slide = base_slide(prs, "04 · 4-Analyst 평가",
                       "10개 thesis 중 7건 강한 지지, 3건 mixed, 0건 반박",
                       "Macro · Industry · Empirical · Counter-thesis 4개 lens 독립 평가 — 정제 병목론은 거시 산업 학계 모두 합의",
                       page, total)
    # 2-column layout: left = consensus dist chart, right = 핵심 thesis 합의/이견
    left_col_w = Inches(5.5)
    right_col_w = Inches(6.7)
    col_gap = Inches(0.20)
    top0 = BODY_TOP + Inches(0.10)

    # Left: consensus distribution donut-style
    add_text(slide, BODY_LEFT, top0, left_col_w, Inches(0.30),
             "Consensus 분포", size=12, bold=True, color=DEEP_FOREST,
             font=HEADER_FONT)
    # bars (강한 지지 7 / mixed 3 / 반박 0)
    bar_top = top0 + Inches(0.45)
    bar_h = Inches(0.55)
    labels = ["강한 지지", "Mixed (혼합)", "강한 반박"]
    counts = [7, 3, 0]
    colors = [BULL, NEU, BEAR]
    max_w = int(left_col_w) - Inches(2.0)
    for i, (lbl, cnt, c) in enumerate(zip(labels, counts, colors)):
        ttop = bar_top + (bar_h + Inches(0.10)) * i
        add_text(slide, BODY_LEFT, ttop, Inches(1.6), bar_h,
                 lbl, size=11, color=INK, anchor=MSO_ANCHOR.MIDDLE,
                 font=BODY_FONT)
        bw = Emu(int(max_w * cnt / 10))
        if cnt > 0:
            add_rect(slide, BODY_LEFT + Inches(1.7), ttop + Inches(0.10),
                     bw, Inches(0.35), c)
        add_text(slide, BODY_LEFT + Inches(1.7) + bw + Inches(0.10),
                 ttop, Inches(0.8), bar_h, f"{cnt}/10", size=11, bold=True,
                 color=c, anchor=MSO_ANCHOR.MIDDLE, font=BODY_FONT)
    # Insight callout
    add_text(slide, BODY_LEFT, bar_top + (bar_h + Inches(0.10)) * 3 + Inches(0.10),
             left_col_w, Inches(0.50),
             "→ 4-Analyst 합의 강도는 thesis 신뢰성의 1차 proxy",
             size=10, italic=True, color=MOSS, font=BODY_FONT)

    # Right: Top thesis with consensus
    right_left = BODY_LEFT + left_col_w + col_gap
    add_text(slide, right_left, top0, right_col_w, Inches(0.30),
             "핵심 thesis별 합의도", size=12, bold=True, color=DEEP_FOREST,
             font=HEADER_FONT)
    items = [
        ("T1", "정제 병목론", "지지 4/4 (3 강한)"),
        ("T2", "11월 유예 종료", "지지 3/4, 1 중립"),
        ("T3", "5중 해자 unbreakable", "지지 4/4 (3 강한)"),
        ("T6", "중희토류(Dy/Tb) 비대칭", "지지 4/4 (3 강한)"),
        ("T8", "광산-정제 mispricing", "지지 2/4, 1 중립, 1 약반박"),
    ]
    item_h = Inches(0.62)
    for i, (tid, ttl, cons) in enumerate(items):
        itop = top0 + Inches(0.45) + (item_h + Inches(0.05)) * i
        add_rect(slide, right_left, itop, Inches(0.55), item_h, DEEP_FOREST)
        add_text(slide, right_left, itop, Inches(0.55), item_h, tid,
                 size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER,
                 anchor=MSO_ANCHOR.MIDDLE, font=BODY_FONT)
        add_text(slide, right_left + Inches(0.65), itop, Inches(2.8), item_h,
                 ttl, size=11, bold=True, color=DEEP_FOREST,
                 anchor=MSO_ANCHOR.MIDDLE, font=BODY_FONT)
        add_text(slide, right_left + Inches(3.5), itop, Inches(3.2), item_h,
                 cons, size=10, color=MOSS, anchor=MSO_ANCHOR.MIDDLE,
                 font=BODY_FONT)


def persona_quote_slide(prs, page, total):
    """Slide 6 — 13명 페르소나 quote highlight (NEW)."""
    slide = base_slide(prs, "05 · Persona Voices",
                       "“30년 단절된 산업의 사실상 유일 player” — Ackman",
                       "13명 페르소나 panel의 핵심 quote 4개 — Lynas highest conviction (very_bullish 5/13)",
                       page, total)
    # 4 quote cards (2x2)
    card_w = Inches(6.0)
    card_h = Inches(2.10)
    gap_x = Inches(0.30)
    gap_y = Inches(0.20)
    quotes = [
        ("Bill Ackman", "활동주의 / High-quality monopoly", LYC := "LYC.AX",
         "내가 가장 사고 싶은 REE name — 정제 vertical의 본질. Lynas는 30년 단절된 산업의 사실상 유일 commercial player.",
         GOLD),
        ("Stanley Druckenmiller", "Macro Trader / 거시 Tailwind", "MP",
         "Macro perfect storm — 美中 trade war + DoD floor + 1-6 vertical. Top 5 thesis 중 하나, '정답일 때 크게 베팅'.",
         MOSS),
        ("Aswath Damodaran", "Valuation / DCF", "ILU.AX",
         "Iluka는 mineral sands valuation only — Eneabba 정제 segment 미반영. DCF fair value $13-18 vs 현재 $8.47, 50-100% upside.",
         DEEP_FOREST),
        ("Charlie Munger", "Mental Models / 'Never China'", "600111.SS",
         "Never invest in China — SOE governance + FDI 제한. Lynas는 정반대 — 30년 단절 = unbridgeable moat의 본질.",
         BEAR),
    ]
    for i, (persona, role, ticker, quote, accent) in enumerate(quotes):
        row, col = i // 2, i % 2
        left = BODY_LEFT + col * (card_w + gap_x)
        top = BODY_TOP + Inches(0.10) + row * (card_h + gap_y)
        add_rect(slide, left, top, card_w, card_h, WHITE, line=LIGHT_GRAY)
        # accent left bar (single side, no rounded corner)
        add_rect(slide, left, top, Inches(0.10), card_h, accent)
        # avatar circle
        add_circle(slide, left + Inches(0.30), top + Inches(0.30),
                   Inches(0.50), accent)
        add_text(slide, left + Inches(0.30), top + Inches(0.30),
                 Inches(0.50), Inches(0.50), persona[0], size=18, bold=True,
                 color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                 font=HEADER_FONT)
        # name + role
        add_text(slide, left + Inches(0.95), top + Inches(0.25),
                 card_w - Inches(2.5), Inches(0.30), persona, size=12,
                 bold=True, color=DEEP_FOREST, font=HEADER_FONT)
        add_text(slide, left + Inches(0.95), top + Inches(0.55),
                 card_w - Inches(2.5), Inches(0.25), role, size=9,
                 color=GRAY, italic=True, font=BODY_FONT)
        # ticker badge top right
        add_rect(slide, left + card_w - Inches(1.20), top + Inches(0.25),
                 Inches(1.05), Inches(0.30), accent)
        add_text(slide, left + card_w - Inches(1.20), top + Inches(0.25),
                 Inches(1.05), Inches(0.30), ticker, size=10, bold=True,
                 color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                 font=BODY_FONT)
        # quote text
        add_text(slide, left + Inches(0.30), top + Inches(0.95),
                 card_w - Inches(0.50), Inches(1.10),
                 f"“{quote}”", size=11, italic=True, color=INK,
                 font=BODY_FONT)


def scenario_slide(prs, page, total):
    """Slide 7 — Bull/Base/Bear scenario for top 3 picks."""
    slide = base_slide(prs, "06 · Scenarios",
                       "Lynas: $14 ↔ $32 / MP: $40 ↔ $110 / Iluka: $6.5 ↔ $16",
                       "Bull/Base/Bear 확률 가중 시나리오 · 11월 中 통제 결과 + 정제 capacity 가동이 trigger",
                       page, total)
    rows = [
        ("LYC.AX", "라이너스", 19.53, "AUD",
         (35, 32.0, "+64%"), (50, 24.0, "+23%"), (15, 14.0, "-28%")),
        ("MP", "MP 머티리얼스", 69.13, "USD",
         (30, 110.0, "+59%"), (50, 75.0, "+9%"), (20, 40.0, "-42%")),
        ("ILU.AX", "일루카", 8.47, "AUD",
         (30, 16.0, "+89%"), (50, 12.0, "+42%"), (20, 6.5, "-23%")),
    ]
    headers = ["종목", "현재가", "Bull (확률·목표·upside)", "Base", "Bear"]
    col_w = [Inches(2.3), Inches(1.5), Inches(2.85), Inches(2.85), Inches(2.85)]
    col_x = [BODY_LEFT]
    for w in col_w[:-1]:
        col_x.append(col_x[-1] + w)

    hdr_top = BODY_TOP + Inches(0.10)
    add_rect(slide, BODY_LEFT, hdr_top, BODY_W, Inches(0.40), DEEP_FOREST)
    for i, h in enumerate(headers):
        add_text(slide, col_x[i], hdr_top, col_w[i], Inches(0.40), h, size=11,
                 bold=True, color=WHITE, align=PP_ALIGN.CENTER,
                 anchor=MSO_ANCHOR.MIDDLE, font=BODY_FONT)

    for i, r in enumerate(rows):
        row_top = hdr_top + Inches(0.50) + Inches(1.20) * i
        if i % 2 == 0:
            add_rect(slide, BODY_LEFT, row_top, BODY_W, Inches(1.10), WHITE,
                     line=LIGHT_GRAY)
        # ticker + name
        add_text(slide, col_x[0] + Inches(0.10), row_top + Inches(0.10),
                 col_w[0], Inches(0.40), r[0], size=12, bold=True,
                 color=DEEP_FOREST, font=BODY_FONT)
        add_text(slide, col_x[0] + Inches(0.10), row_top + Inches(0.50),
                 col_w[0], Inches(0.30), r[1], size=10, color=INK,
                 font=BODY_FONT)
        # current
        add_text(slide, col_x[1], row_top, col_w[1], Inches(1.10),
                 f"{r[2]:.2f} {r[3]}", size=11, color=INK,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                 font=BODY_FONT)
        # 3 scenarios
        scenarios = [(r[4], BULL, "Bull"), (r[5], NEU, "Base"), (r[6], BEAR if "+0" not in r[6][2] and r[6][2].startswith('-') else BULL, "Bear")]
        for j, ((prob, target, upside), c, lbl) in enumerate(scenarios):
            sx = col_x[2 + j]
            sw = col_w[2 + j]
            add_text(slide, sx + Inches(0.05), row_top + Inches(0.10),
                     sw - Inches(0.10), Inches(0.30),
                     f"{lbl}  {prob}%", size=10, bold=True, color=c,
                     font=BODY_FONT)
            add_text(slide, sx + Inches(0.05), row_top + Inches(0.40),
                     sw - Inches(0.10), Inches(0.40),
                     f"{target:.2f}  ({upside})", size=14, bold=True,
                     color=DEEP_FOREST, font=HEADER_FONT)
            # mini progress bar (probability)
            bar_w_full = int(sw) - Inches(0.20)
            add_rect(slide, sx + Inches(0.10), row_top + Inches(0.85),
                     bar_w_full, Inches(0.05), LIGHT_GRAY)
            add_rect(slide, sx + Inches(0.10), row_top + Inches(0.85),
                     Emu(int(bar_w_full * prob / 100)), Inches(0.05), c)


def risk_slide(prs, page, total):
    """Slide 8 — Risk matrix."""
    slide = base_slide(prs, "07 · Risk Matrix",
                       "5대 portfolio risk — 中 통제 완화·말레이시아 정치·Stage III 실행이 top",
                       "P × I 격자 · 高(빨강) → 中(주황) → 低(녹색) — 우선 모니터링 대상은 진한 색",
                       page, total)
    risks = [
        ("中 통제 완화 (11월 유예 면제)", "중", "고", BEAR,
         "역사적 precedent 없음 (확률 ~20%) but 발생 시 -30~40%"),
        ("말레이시아 LAMP 라이선스", "중", "고", BEAR,
         "2024 야당 압박 사례 재발 시 Lynas 매출 60% 영향"),
        ("Stage III execution failure (MP)", "중", "고", BEAR,
         "中 외 첫 commercial 시도 — yield 부족 시 -30%"),
        ("中 NdPr dump ($50/kg 미만)", "중", "중", GOLD,
         "Lynas cost $45-70 cap 구간, MP는 DoD floor가 보호"),
        ("USAR dilution risk", "고", "중", GOLD,
         "Cash runway 2-3Y, customer 미확보 시 추가 raise"),
        ("선제적 비축 부메랑 (2028-29)", "중", "중", GOLD,
         "Toyota·VW 등 7-15kt 비축 → 비축 소멸 시 -20% 가능"),
    ]
    col_w = [Inches(4.5), Inches(0.7), Inches(0.7), Inches(0.9), Inches(5.53)]
    col_x = [BODY_LEFT]
    for w in col_w[:-1]:
        col_x.append(col_x[-1] + w)
    headers = ["리스크", "P", "I", "Severity", "설명"]
    hdr_top = BODY_TOP + Inches(0.10)
    add_rect(slide, BODY_LEFT, hdr_top, BODY_W, Inches(0.40), DEEP_FOREST)
    for i, h in enumerate(headers):
        add_text(slide, col_x[i], hdr_top, col_w[i], Inches(0.40), h, size=11,
                 bold=True, color=WHITE, align=PP_ALIGN.CENTER,
                 anchor=MSO_ANCHOR.MIDDLE, font=BODY_FONT)
    for i, (rname, p, ipa, sev, desc) in enumerate(risks):
        row_top = hdr_top + Inches(0.45) + Inches(0.55) * i
        if i % 2 == 0:
            add_rect(slide, BODY_LEFT, row_top, BODY_W, Inches(0.55), WHITE)
        add_text(slide, col_x[0] + Inches(0.05), row_top, col_w[0],
                 Inches(0.55), rname, size=11, bold=True, color=DEEP_FOREST,
                 anchor=MSO_ANCHOR.MIDDLE, font=BODY_FONT)
        for j, v in enumerate([p, ipa]):
            add_text(slide, col_x[1+j], row_top, col_w[1+j], Inches(0.55), v,
                     size=12, bold=True, color=sev, align=PP_ALIGN.CENTER,
                     anchor=MSO_ANCHOR.MIDDLE, font=BODY_FONT)
        # severity dot
        add_circle(slide, col_x[3] + Inches(0.30), row_top + Inches(0.15),
                   Inches(0.25), sev)
        add_text(slide, col_x[4] + Inches(0.05), row_top, col_w[4],
                 Inches(0.55), desc, size=10, color=INK,
                 anchor=MSO_ANCHOR.MIDDLE, font=BODY_FONT)


def portfolio_slide(prs, page, total):
    """Slide 9 — Portfolio allocation pie chart-style."""
    slide = base_slide(prs, "08 · Portfolio Construction",
                       "총 REE 노출 13.5% / 비중국 정제 vertical 9.0% 핵심",
                       "Risk-adjusted size cap (변동성·상관관계 기반) · cash 86.5% — 추가 dip 시 LYC/MP add 여력",
                       page, total)
    allocations = [
        ("LYC.AX", "Lynas (정제 vertical 핵심)", 4.5, BULL),
        ("ILU.AX", "Iluka (catalyst trade)", 4.0, MOSS),
        ("MP", "MP (starter, dip wait)", 2.5, GOLD),
        ("600111.SS", "China Northern (hedge)", 1.5, NEU),
        ("USAR", "USA Rare Earth (lottery)", 1.0, BEAR),
    ]
    # Horizontal stacked bar (left)
    bar_left = BODY_LEFT
    bar_top = BODY_TOP + Inches(0.20)
    bar_total_w = Inches(6.5)
    bar_h = Inches(0.65)
    add_text(slide, bar_left, bar_top - Inches(0.30), bar_total_w, Inches(0.25),
             "REE basket 13.5% allocation 분포", size=11, bold=True,
             color=DEEP_FOREST, font=HEADER_FONT)
    # Stacked
    cur_x = bar_left
    for tk, name, pct, c in allocations:
        seg_w = Emu(int(int(bar_total_w) * pct / 13.5))
        add_rect(slide, cur_x, bar_top, seg_w, bar_h, c)
        add_text(slide, cur_x, bar_top, seg_w, bar_h, f"{tk}\n{pct:.1f}%",
                 size=9, bold=True, color=WHITE, align=PP_ALIGN.CENTER,
                 anchor=MSO_ANCHOR.MIDDLE, font=BODY_FONT)
        cur_x += seg_w
    # Legend — right column (tabular)
    leg_left = BODY_LEFT + bar_total_w + Inches(0.40)
    leg_w = Inches(5.43)
    add_text(slide, leg_left, bar_top - Inches(0.30), leg_w, Inches(0.25),
             "Position 상세", size=11, bold=True, color=DEEP_FOREST,
             font=HEADER_FONT)
    for i, (tk, name, pct, c) in enumerate(allocations):
        ltop = bar_top + Inches(0.10) + Inches(0.50) * i
        add_rect(slide, leg_left, ltop, Inches(0.30), Inches(0.30), c)
        add_text(slide, leg_left + Inches(0.40), ltop, Inches(1.5),
                 Inches(0.30), tk, size=11, bold=True, color=DEEP_FOREST,
                 anchor=MSO_ANCHOR.MIDDLE, font=BODY_FONT)
        add_text(slide, leg_left + Inches(2.0), ltop, leg_w - Inches(2.0),
                 Inches(0.30), name, size=10, color=INK,
                 anchor=MSO_ANCHOR.MIDDLE, font=BODY_FONT)
        add_text(slide, leg_left + leg_w - Inches(1.0), ltop, Inches(1.0),
                 Inches(0.30), f"{pct:.1f}%", size=11, bold=True, color=c,
                 align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE,
                 font=BODY_FONT)
    # Bottom rebalance triggers
    trig_top = bar_top + bar_h + Inches(1.30)
    add_text(slide, BODY_LEFT, trig_top, BODY_W, Inches(0.30),
             "Rebalance triggers", size=11, bold=True, color=DEEP_FOREST,
             font=HEADER_FONT)
    triggers = [
        "11/10/26 中 통제 결과 confirm — 강화 시 비중국 +50% / 면제 시 -30% rebalance",
        "MP Stage III commissioning (2026 Q3) — 성공 시 +1.5% / 실패 시 -1%",
        "ILU Eneabba commissioning update (분기별) — 진척에 따라 +0.5% 단계 add",
        "NdPr 가격 $50 미만 dump 시 — 모든 비중국 position -50% (8주 회복 가정)",
    ]
    for i, t in enumerate(triggers):
        ttop = trig_top + Inches(0.30) + Inches(0.30) * i
        add_circle(slide, BODY_LEFT + Inches(0.05), ttop + Inches(0.08),
                   Inches(0.12), GOLD)
        add_text(slide, BODY_LEFT + Inches(0.30), ttop, BODY_W - Inches(0.30),
                 Inches(0.30), t, size=10, color=INK, font=BODY_FONT)


def catalysts_slide(prs, page, total):
    """Slide 10 — 12-month catalyst timeline."""
    slide = base_slide(prs, "09 · Catalyst Timeline",
                       "2026 Q3 Stage III + Kalgoorlie Phase II → 11월 中 통제 결과 → 2027 Eneabba",
                       "Top 5 종목 share share catalyst 일정 — 11월 단일 binary event가 주가 가장 큰 driver",
                       page, total)
    # Timeline horizontal axis
    axis_y = BODY_TOP + Inches(2.4)
    axis_left = BODY_LEFT + Inches(0.5)
    axis_right = BODY_LEFT + BODY_W - Inches(0.5)
    add_rect(slide, axis_left, axis_y, axis_right - axis_left, Inches(0.04),
             DEEP_FOREST)
    # quarters
    quarters = ["2026 Q2", "2026 Q3", "2026 Q4 (11월)", "2027 Q1", "2027 Q2", "2027 H2"]
    seg = (axis_right - axis_left) / (len(quarters) - 1)
    for i, q in enumerate(quarters):
        x = axis_left + seg * i
        add_circle(slide, x - Inches(0.10), axis_y - Inches(0.075),
                   Inches(0.20), DEEP_FOREST)
        add_text(slide, x - Inches(0.8), axis_y + Inches(0.10), Inches(1.6),
                 Inches(0.30), q, size=9, bold=True, color=DEEP_FOREST,
                 align=PP_ALIGN.CENTER, font=BODY_FONT)
    # catalysts above axis
    above_events = [
        (1, "Kalgoorlie Phase II (LYC)", BULL),
        (1, "Stage III 가동 (MP)", BULL),
        (2, "中 통제 유예 종료 ⚡", GOLD),
        (3, "Apple iPhone 17 자석 ramp", BULL),
        (4, "Texas 시설 가동 (LYC)", BULL),
        (5, "Eneabba 첫 매출 (ILU)", BULL),
    ]
    for i, (qidx, label, c) in enumerate(above_events):
        x = axis_left + seg * qidx
        # vertical line
        line_top = axis_y - Inches(1.50 + 0.20 * (i % 3))
        add_rect(slide, x - Inches(0.01), line_top, Inches(0.02),
                 axis_y - line_top, c)
        # label box
        add_rect(slide, x - Inches(1.1), line_top - Inches(0.30), Inches(2.2),
                 Inches(0.30), c)
        add_text(slide, x - Inches(1.1), line_top - Inches(0.30), Inches(2.2),
                 Inches(0.30), label, size=9, bold=True, color=WHITE,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                 font=BODY_FONT)
    # Below axis: macro events
    below_events = [
        (0, "현재 분석 시점"),
        (2, "11월 10일: NdPr·자석까지 통제 확대 가능성"),
        (5, "비축 unwind 시작 가능"),
    ]
    for qidx, label in below_events:
        x = axis_left + seg * qidx
        add_text(slide, x - Inches(1.5), axis_y + Inches(0.50), Inches(3.0),
                 Inches(0.40), label, size=9, italic=True, color=GRAY,
                 align=PP_ALIGN.CENTER, font=BODY_FONT)


def conclusion_slide(prs, page, total):
    """Slide 11 — Final conclusion (dark dramatic)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
    bg.fill.solid()
    bg.fill.fore_color.rgb = DEEP_FOREST
    bg.line.fill.background()
    # gold accent
    add_rect(slide, Inches(0.7), Inches(0.7), Inches(2.0), Inches(0.04), GOLD)
    add_text(slide, Inches(0.7), Inches(0.85), Inches(11.9), Inches(0.4),
             "10 · CONCLUSION", size=11, bold=True, color=GOLD, font=BODY_FONT)
    # Big takeaway
    add_text(slide, Inches(0.7), Inches(1.7), Inches(11.9), Inches(2.0),
             "진짜 병목은 광산이 아니라\n정제다. 알파는 Lynas·Iluka·MP에 있다.",
             size=40, bold=True, color=WHITE, font=HEADER_FONT)
    # 3 supporting points
    points = [
        ("01", "정제 91% / 자석 94% 中 독점은 단기 해결 불가",
         "30년 단절된 산업의 5중 해자 — 암묵지·장비·비용·자금조달·가격덤핑 동시 작동"),
        ("02", "11월 유예 종료가 binary catalyst",
         "강화 시 비중국 +50% / 면제 시 -30% (역사적으로 면제 사례 0건)"),
        ("03", "정제 vertical mispricing이 alpha source",
         "Lynas·Iluka 시총 vs irreplaceable monopoly 가치 — Damodaran·Ackman의 highest conviction"),
    ]
    for i, (num, ttl, body) in enumerate(points):
        ptop = Inches(4.2) + Inches(0.85) * i
        add_circle(slide, Inches(0.7), ptop + Inches(0.05), Inches(0.45), GOLD)
        add_text(slide, Inches(0.7), ptop + Inches(0.05), Inches(0.45),
                 Inches(0.45), num, size=14, bold=True, color=DEEP_FOREST,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                 font=HEADER_FONT)
        add_text(slide, Inches(1.4), ptop, Inches(11.5), Inches(0.40), ttl,
                 size=15, bold=True, color=WHITE, font=HEADER_FONT)
        add_text(slide, Inches(1.4), ptop + Inches(0.40), Inches(11.5),
                 Inches(0.45), body, size=11, color=SAGE, italic=True,
                 font=BODY_FONT)
    # footer
    add_text(slide, Inches(0.7), Inches(7.05), Inches(11.9), Inches(0.30),
             f"rare-earth refining bottleneck · 13명 페르소나 + 4-Analyst + Deep Research",
             size=9, color=SAGE, font=BODY_FONT)
    add_text(slide, Inches(0.7), Inches(7.05), Inches(11.9), Inches(0.30),
             f"{page:02d} / {total:02d}", size=9, color=SAGE,
             align=PP_ALIGN.RIGHT, font=BODY_FONT)


def build_pptx(pipeline_dir: Path, output_path: Path):
    meta = _read_json(pipeline_dir / "meta.json")
    theses = _read_json(pipeline_dir / "thesis_list.json").get("theses", [])
    stocks_raw = _read_json(pipeline_dir / "stocks.json")
    persona_all = _read_json(pipeline_dir / "persona_panel" / "_all_aggregates.json")
    decisions = _read_json(pipeline_dir / "decisions.json").get("decisions", [])
    eval_data = _read_json(pipeline_dir / "thesis_eval" / "all_aggregate.json")

    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    # Build picks data combining decisions × persona
    picks = []
    for d in decisions:
        tk = d['ticker']
        agg = persona_all.get(tk, {})
        dist = agg.get('verdict_distribution', {})
        bull = dist.get('lean_bullish', {}).get('count', 0) + dist.get('very_bullish', {}).get('count', 0)
        neu = dist.get('neutral', {}).get('count', 0)
        bear = dist.get('lean_bearish', {}).get('count', 0) + dist.get('very_bearish', {}).get('count', 0)
        picks.append({
            'ticker': tk,
            'name': d.get('name', tk),
            'score': agg.get('weighted_average_score_1to5', 0),
            'conf': agg.get('average_confidence', 0),
            'bull': bull,
            'neu': neu,
            'bear': bear,
            'action': d.get('action', '-'),
        })
    picks_sorted = sorted(picks, key=lambda x: -x['score'])

    # Stocks live data
    stocks_summary = []
    for s in stocks_raw:
        m = s.get('market_data', {})
        # find matching pick
        pick_match = next((p for p in picks if p['ticker'] == s['ticker']), {})
        stocks_summary.append({
            'ticker': s['ticker'],
            'name': s.get('name', s['ticker']),
            'price': m.get('current_price', 0),
            'currency': m.get('currency', ''),
            'mcap': m.get('market_cap_usd_bn', 0),
            'fwd_pe': m.get('forward_pe', 0),
            'vol': m.get('volatility_annualized_pct', 0),
            'beta': m.get('beta', 0),
            'ret_1y': m.get('return_1y_pct', 0),
            'score': pick_match.get('score', 0),
            'conf': pick_match.get('conf', 0),
            'action': pick_match.get('action', '-'),
        })

    TOTAL = 11
    cover_slide(prs, meta)                              # 1
    thesis_slide(prs, theses, 2, TOTAL)                 # 2
    top_picks_slide(prs, picks_sorted, 3, TOTAL)        # 3
    market_data_slide(prs, stocks_summary, 4, TOTAL)    # 4
    thesis_eval_slide(prs, eval_data, 5, TOTAL)         # 5
    persona_quote_slide(prs, 6, TOTAL)                  # 6
    scenario_slide(prs, 7, TOTAL)                       # 7
    risk_slide(prs, 8, TOTAL)                           # 8
    portfolio_slide(prs, 9, TOTAL)                      # 9
    catalysts_slide(prs, 10, TOTAL)                     # 10
    conclusion_slide(prs, 11, TOTAL)                    # 11

    output_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(output_path))
    print(f"[pptx-v2] saved {output_path} ({len(prs.slides)} slides)")


def main():
    parser = argparse.ArgumentParser(description="Layer 2 Overview PPT v2 builder")
    parser.add_argument("--pipeline-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    pipeline_dir = Path(args.pipeline_dir)
    output_path = Path(args.output)
    build_pptx(pipeline_dir, output_path)


if __name__ == "__main__":
    main()
