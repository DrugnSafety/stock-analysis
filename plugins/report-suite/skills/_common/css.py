"""3개 보고서 공통 CSS — 한글 폰트 + 일관된 스타일.

폰트 자동 bootstrap (2026-05-11): chart_utils import 시 ~/.fonts/NotoSansKR-*.otf 자동 다운로드되므로,
이 모듈을 import하기 전 chart_utils가 먼저 import되어야 폰트가 보장됨.
직접 import해도 폰트가 누락된 sandbox에서 깨지지 않도록 본 모듈도 lazy bootstrap 시도.
"""
import os
import sys
import warnings
from pathlib import Path

_FONT_REGULAR = Path.home() / ".fonts" / "NotoSansKR-Regular.otf"
_FONT_BOLD = Path.home() / ".fonts" / "NotoSansKR-Bold.otf"


def _bootstrap_fonts_if_missing():
    """WeasyPrint @font-face의 NotoSansKR 파일을 sandbox에서 자동 다운로드."""
    if os.environ.get("SKIP_FONT_BOOTSTRAP") == "1":
        return
    if _FONT_REGULAR.exists() and _FONT_BOLD.exists():
        return
    fonts_dir = _FONT_REGULAR.parent
    fonts_dir.mkdir(parents=True, exist_ok=True)
    urls = {
        _FONT_REGULAR: "https://github.com/notofonts/noto-cjk/raw/main/Sans/SubsetOTF/KR/NotoSansKR-Regular.otf",
        _FONT_BOLD: "https://github.com/notofonts/noto-cjk/raw/main/Sans/SubsetOTF/KR/NotoSansKR-Bold.otf",
    }
    try:
        import urllib.request
    except ImportError:
        return
    for target, url in urls.items():
        if target.exists() and target.stat().st_size > 100000:
            continue
        try:
            urllib.request.urlretrieve(url, str(target))
            print(f"[css] bootstrapped {target.name}", file=sys.stderr)
        except Exception as e:
            warnings.warn(f"[css] font bootstrap failed for {target.name}: {e}")


_bootstrap_fonts_if_missing()

_FONT_FACE = ""
if _FONT_REGULAR.exists():
    _FONT_FACE += f"""
@font-face {{ font-family: 'Noto Sans KR'; font-weight: normal; font-style: normal;
              src: url('file://{_FONT_REGULAR}') format('opentype'); }}
@font-face {{ font-family: 'Noto Sans KR'; font-weight: normal; font-style: italic;
              src: url('file://{_FONT_REGULAR}') format('opentype'); }}
"""
if _FONT_BOLD.exists():
    _FONT_FACE += f"""
@font-face {{ font-family: 'Noto Sans KR'; font-weight: bold; font-style: normal;
              src: url('file://{_FONT_BOLD}') format('opentype'); }}
@font-face {{ font-family: 'Noto Sans KR'; font-weight: bold; font-style: italic;
              src: url('file://{_FONT_BOLD}') format('opentype'); }}
"""

CSS_BASE = _FONT_FACE + """
@page { size: A4; margin: 18mm 14mm; @bottom-center { content: counter(page) " / " counter(pages); font-size: 9pt; color: #6b7280; } }
* { font-family: 'Noto Sans KR', 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif; }
body { font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif; color: #1f2937; line-height: 1.5; font-size: 10pt; }
h1, h2, h3, h4, h5, h6, p, div, span, td, th, li, em, i, strong, b, label, button {
  font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
}
h1 { color: #111; font-size: 22pt; border-bottom: 2pt solid #2563eb; padding-bottom: 8pt; }
h2 { color: #111827; margin-top: 22pt; border-left: 4pt solid #2563eb; padding-left: 8pt; font-size: 16pt; }
h3 { margin-top: 16pt; font-size: 12pt; color: #1f2937; }
h4 { font-size: 11pt; margin-top: 14pt; color: #374151; }

.cover { page-break-after: always; padding-top: 3cm; text-align: center; }
.cover h1 { border: none; font-size: 28pt; }
.cover-meta { color: #6b7280; font-size: 11pt; margin: 0.5cm 0; }

.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10pt; margin: 12pt 0; }
.kpi { background: #f9fafb; padding: 14pt; border-left: 3pt solid #2563eb; text-align: center; }
.kpi .num { font-size: 22pt; font-weight: 700; color: #111; }
.kpi .num.green { color: #16a34a; } .kpi .num.red { color: #dc2626; } .kpi .num.amber { color: #ca8a04; }
.kpi .label { font-size: 9pt; color: #6b7280; margin-top: 4pt; }

table.dt { width: 100%; border-collapse: collapse; font-size: 9.5pt; margin: 8pt 0; }
table.dt th, table.dt td { border: 1pt solid #e5e7eb; padding: 5pt 7pt; text-align: left; vertical-align: top; }
table.dt th { background: #f3f4f6; }

.note { background: #fef3c7; padding: 8pt 12pt; border-left: 3pt solid #f59e0b; margin: 6pt 0; font-size: 9.5pt; }
.win { background: #f0fdf4; padding: 8pt 12pt; border-left: 3pt solid #16a34a; margin: 6pt 0; }
.warn { background: #fef2f2; padding: 8pt 12pt; border-left: 3pt solid #dc2626; margin: 6pt 0; }
.info { background: #eff6ff; padding: 8pt 12pt; border-left: 3pt solid #2563eb; margin: 6pt 0; }

code, pre, kbd { background: #f3f4f6; padding: 1pt 4pt; border-radius: 3pt; font-family: 'Noto Sans KR', 'DejaVu Sans Mono', monospace; font-size: 0.92em; }

.bull { color: #16a34a; font-weight: 600; }
.bear { color: #dc2626; font-weight: 600; }
.neutral { color: #ca8a04; font-weight: 600; }

.tag-actual { background: #dcfce7; color: #14532d; padding: 1pt 5pt; border-radius: 3pt; font-size: 8pt; }
.tag-inference { background: #fef3c7; color: #78350f; padding: 1pt 5pt; border-radius: 3pt; font-size: 8pt; }
.tag-assumption { background: #fee2e2; color: #7f1d1d; padding: 1pt 5pt; border-radius: 3pt; font-size: 8pt; }
.tag-derived { background: #ede9fe; color: #4c1d95; padding: 1pt 5pt; border-radius: 3pt; font-size: 8pt; }
"""


VERDICT_COLOR = {"lean_bullish": "#16a34a", "BUY": "#16a34a",
                 "neutral": "#ca8a04", "HOLD": "#ca8a04",
                 "lean_bearish": "#dc2626", "SELL": "#dc2626"}

VERDICT_KOR = {"lean_bullish": "🟢 매수 성향", "BUY": "🟢 매수",
               "neutral": "🟡 중립", "HOLD": "🟡 관망",
               "lean_bearish": "🔴 매도 성향", "SELL": "🔴 매도"}


def fmt_money_krw(v: float) -> str:
    if v is None: return "-"
    if abs(v) >= 100_000_000: return f"₩{v/100_000_000:.2f}억"
    if abs(v) >= 10_000: return f"₩{v/10_000:.0f}만"
    return f"₩{v:,.0f}"


def fmt_pct(v: float, sign: bool = True) -> str:
    if v is None: return "-"
    s = "+" if sign and v >= 0 else ""
    return f"{s}{v:.2f}%"
