"""Emoji → 텍스트 라벨 매핑.

WeasyPrint + Noto Sans KR 환경에서 emoji가 빈 박스로 표시되는 문제 해결을 위해
모든 emoji를 한국어 텍스트 라벨로 교체.
"""
from __future__ import annotations

EMOJI_MAP = {
    "📋": "[브리핑]",
    "📊": "[차트]",
    "📈": "[상승]",
    "📉": "[하락]",
    "📐": "[측정]",
    "📅": "[일정]",
    "📑": "[공시]",
    "📌": "[메모]",
    "📚": "[학습]",
    "📰": "[뉴스]",
    "🔬": "[심층]",
    "🔥": "[중요]",
    "🌐": "[글로벌]",
    "🌍": "[거시]",
    "🏭": "[산업]",
    "🏢": "[기업]",
    "🏛️": "[정책]",
    "🏛": "[정책]",
    "🚀": "[성장]",
    "🤝": "[M&A]",
    "🥊": "[Debate]",
    "💼": "[실적]",
    "💰": "[재무]",
    "💡": "[Tip]",
    "🎯": "[목표]",
    "🧩": "[퍼즐]",
    "⚖️": "[균형]",
    "⚖": "[균형]",
    "⚠️": "[주의]",
    "⚠": "[주의]",
    "✓": "[O]",
    "✗": "[X]",
    "🟢": "[녹]",
    "🟡": "[노]",
    "🔴": "[적]",
    "🔵": "[청]",
    "🗳️": "[투표]",
    "🗳": "[투표]",
    "○": "[중립]",
}


def remove_emoji(text: str) -> str:
    """Replace all known emoji with safe text labels."""
    if not text:
        return text
    out = text
    for emo, label in EMOJI_MAP.items():
        out = out.replace(emo, label)
    return out
