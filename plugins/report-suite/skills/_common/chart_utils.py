"""차트 helper — matplotlib PNG → base64 inline embed.

한글 폰트(Noto Sans KR) 자동 로드. 모든 차트는 base64 PNG로 HTML에 embed.

자동 bootstrap 정책 (2026-05-11 추가):
- ~/.fonts/NotoSansKR-{Regular,Bold}.otf 가 없으면 GitHub raw에서 자동 다운로드.
- Cowork sandbox·CI 같은 신규 환경에서 한글 □(tofu) 깨짐을 영구 방지.
- 다운로드 실패해도 silent skip — 기존 fallback chain 유지.
"""
import base64
import io
import os
import sys
import warnings
from pathlib import Path
import matplotlib
matplotlib.use("Agg")  # non-interactive
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm


# 한글 폰트 자동 다운로드 (sandbox/CI에서 폰트 미존재 시)
_FONT_DOWNLOAD_URLS = {
    "NotoSansKR-Regular.otf": "https://github.com/notofonts/noto-cjk/raw/main/Sans/SubsetOTF/KR/NotoSansKR-Regular.otf",
    "NotoSansKR-Bold.otf": "https://github.com/notofonts/noto-cjk/raw/main/Sans/SubsetOTF/KR/NotoSansKR-Bold.otf",
}


def _ensure_korean_font_files():
    """~/.fonts/NotoSansKR-*.otf 가 없으면 자동 다운로드 시도.

    환경변수 SKIP_FONT_BOOTSTRAP=1 시 스킵. 다운로드 실패 시 silent.
    """
    if os.environ.get("SKIP_FONT_BOOTSTRAP") == "1":
        return
    fonts_dir = Path.home() / ".fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)
    needs_download = any(not (fonts_dir / fname).exists() for fname in _FONT_DOWNLOAD_URLS)
    if not needs_download:
        return
    try:
        import urllib.request
    except ImportError:
        return
    for fname, url in _FONT_DOWNLOAD_URLS.items():
        target = fonts_dir / fname
        if target.exists() and target.stat().st_size > 100000:
            continue
        try:
            urllib.request.urlretrieve(url, str(target))
            print(f"[chart_utils] bootstrapped {fname} ({target.stat().st_size:,} bytes)", file=sys.stderr)
        except Exception as e:
            warnings.warn(f"[chart_utils] font bootstrap failed for {fname}: {e}")


# 한글 폰트 자동 등록
def _register_korean_font():
    _ensure_korean_font_files()
    candidates = [
        Path.home() / ".fonts" / "NotoSansKR-Regular.otf",
        Path.home() / ".fonts" / "NotoSansKR-Regular.ttf",
        Path.home() / ".fonts" / "NotoSansCJKkr-Regular.otf",
        Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.otf"),
        Path("/Library/Fonts/AppleGothic.ttf"),
        Path("/System/Library/Fonts/AppleSDGothicNeo.ttc"),
    ]
    for p in candidates:
        if p.exists():
            try:
                fm.fontManager.addfont(str(p))
                # Also register Bold variant if available
                bold = p.parent / p.name.replace("-Regular", "-Bold")
                if bold.exists() and bold != p:
                    try: fm.fontManager.addfont(str(bold))
                    except Exception: pass
                # font name
                font_name = fm.FontProperties(fname=str(p)).get_name()
                plt.rcParams["font.family"] = [font_name, "DejaVu Sans"]
                plt.rcParams["font.sans-serif"] = [font_name, "DejaVu Sans"]
                return font_name
            except Exception:
                continue
    warnings.warn("[chart_utils] No Korean font found — Korean text will render as □ (tofu). "
                  "Bootstrap auto-downloads ~/.fonts/NotoSansKR-*.otf from GitHub on first import.")
    return None


_KOREAN_FONT = _register_korean_font()
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 100


COLORS = {
    "bull": "#16a34a", "bear": "#dc2626", "neutral": "#ca8a04",
    "support": "#16a34a", "challenge": "#dc2626",
    "primary": "#2563eb", "secondary": "#8b5cf6",
    "warn": "#f59e0b", "info": "#0ea5e9",
}


def fig_to_base64(fig, dpi: int = 80) -> str:
    """matplotlib Figure → base64-encoded PNG (HTML embed용).

    DPI 80 — 80 PPI is 'sufficient for 컴퓨터 화면 + 인쇄' compromise.
    한글 폰트 subsetting 비용 절감을 위해 dpi 100 → 80 조정 (2026-05-03 기준).
    """
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("ascii")


def img_tag(b64: str, width: str = "100%") -> str:
    return f'<img src="data:image/png;base64,{b64}" style="width:{width};max-width:600pt;display:block;margin:8pt auto;"/>'


# ============================================================
# Bar charts
# ============================================================

def bar_chart(labels: list, values: list, title: str = "",
              ylabel: str = "", colors: list = None,
              h_line: float = None, figsize: tuple = (8, 4)) -> str:
    """단순 bar chart."""
    fig, ax = plt.subplots(figsize=figsize)
    bars = ax.bar(labels, values, color=colors or [COLORS["primary"]] * len(labels),
                   edgecolor="white", linewidth=1)
    if title:
        ax.set_title(title, fontsize=11, fontweight="bold", pad=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=9)
    if h_line is not None:
        ax.axhline(h_line, color="#6b7280", linestyle="--", linewidth=1, alpha=0.7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=9)
    plt.xticks(rotation=15, ha="right")

    # value labels on top
    for bar, val in zip(bars, values):
        height = bar.get_height()
        sign = "+" if (isinstance(val, (int, float)) and val >= 0) else ""
        ax.annotate(f"{sign}{val:.1f}" if isinstance(val, float) else f"{val}",
                     xy=(bar.get_x() + bar.get_width()/2, height),
                     xytext=(0, 3), textcoords="offset points",
                     ha="center", va="bottom", fontsize=8.5)
    plt.tight_layout()
    return img_tag(fig_to_base64(fig))


# ============================================================
# Pie / Donut
# ============================================================

def pie_chart(labels: list, values: list, title: str = "",
              colors: list = None, donut: bool = True,
              figsize: tuple = (5, 5)) -> str:
    if not values or sum(values) == 0:
        return f'<p style="color:#6b7280;font-size:9pt;">[{title}: 데이터 없음]</p>'
    fig, ax = plt.subplots(figsize=figsize)
    wedge_props = {"width": 0.4, "edgecolor": "white"} if donut else {}
    wedges, texts, autotexts = ax.pie(
        values, labels=labels,
        autopct="%1.0f%%",
        colors=colors or [COLORS["bull"], COLORS["neutral"], COLORS["bear"]][:len(values)],
        wedgeprops=wedge_props,
        textprops={"fontsize": 10},
    )
    if title:
        ax.set_title(title, fontsize=11, fontweight="bold", pad=15)
    plt.setp(autotexts, size=9, weight="bold", color="white")
    return img_tag(fig_to_base64(fig), width="60%")


# ============================================================
# Heatmap
# ============================================================

def heatmap(matrix: list[list[float]], row_labels: list, col_labels: list,
             title: str = "", cmap: str = "RdYlGn",
             vmin: float = -1, vmax: float = 1,
             figsize: tuple = None,
             annotate: bool = True) -> str:
    """숫자 매트릭스 heatmap."""
    if not matrix or not matrix[0]:
        return ""
    n_rows, n_cols = len(matrix), len(matrix[0])
    figsize = figsize or (max(8, n_cols * 0.7), max(4, n_rows * 0.5 + 1))

    fig, ax = plt.subplots(figsize=figsize)
    import numpy as np
    arr = np.array(matrix, dtype=float)
    im = ax.imshow(arr, cmap=cmap, vmin=vmin, vmax=vmax, aspect="auto")

    ax.set_xticks(range(n_cols))
    ax.set_xticklabels(col_labels, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(n_rows))
    ax.set_yticklabels(row_labels, fontsize=8)

    if title:
        ax.set_title(title, fontsize=11, fontweight="bold", pad=10)

    if annotate:
        for i in range(n_rows):
            for j in range(n_cols):
                val = matrix[i][j]
                if val is None or (isinstance(val, float) and (val != val)):
                    continue
                color = "white" if abs(val) > 0.5 else "black"
                txt = f"{val:.0f}" if abs(val - round(val)) < 0.01 else f"{val:.2f}"
                ax.text(j, i, txt, ha="center", va="center", color=color, fontsize=7)

    fig.colorbar(im, ax=ax, shrink=0.6, aspect=20)
    plt.tight_layout()
    return img_tag(fig_to_base64(fig))


# ============================================================
# Stacked bar (verdict 분포 종목별)
# ============================================================

def stacked_bar(categories: list, series: dict[str, list[float]],
                 title: str = "", colors: dict = None,
                 figsize: tuple = (8, 4)) -> str:
    """예: tickers × {bull, neutral, bear} stacked counts."""
    fig, ax = plt.subplots(figsize=figsize)
    import numpy as np
    bottom = np.zeros(len(categories))
    default_colors = {"bull": COLORS["bull"], "lean_bullish": COLORS["bull"],
                      "neutral": COLORS["neutral"],
                      "bear": COLORS["bear"], "lean_bearish": COLORS["bear"]}
    for label, values in series.items():
        c = (colors or default_colors).get(label, COLORS["primary"])
        ax.bar(categories, values, bottom=bottom, label=label, color=c,
                edgecolor="white", linewidth=1)
        bottom += np.array(values, dtype=float)

    if title:
        ax.set_title(title, fontsize=11, fontweight="bold", pad=10)
    ax.legend(loc="upper right", fontsize=8, framealpha=0.9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=9)
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    return img_tag(fig_to_base64(fig))


# ============================================================
# Confidence histogram
# ============================================================

def confidence_histogram(confidences: list[float], title: str = "Confidence 분포",
                          figsize: tuple = (8, 3.5)) -> str:
    fig, ax = plt.subplots(figsize=figsize)
    bins = [0, 0.4, 0.6, 0.8, 1.01]
    colors_per_bin = ["#dc2626", "#f59e0b", "#16a34a", "#15803d"]
    n, edges, patches = ax.hist(confidences, bins=bins, edgecolor="white", linewidth=1)
    for patch, color in zip(patches, colors_per_bin):
        patch.set_facecolor(color)
    ax.set_title(title, fontsize=11, fontweight="bold", pad=10)
    ax.set_xlabel("Confidence", fontsize=9)
    ax.set_ylabel("페르소나 수", fontsize=9)
    ax.set_xticks(bins)
    ax.set_xticklabels([f"{int(b*100)}%" for b in bins])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    return img_tag(fig_to_base64(fig))


# ============================================================
# KPI gauge-like horizontal bar
# ============================================================

def kpi_horizontal_bars(items: list[dict], title: str = "",
                         figsize: tuple = None) -> str:
    """items: [{label, value, max, color, format}, ...]"""
    if not items:
        return ""
    if figsize is None or figsize[1] is None:
        figsize = (8, 0.6 + len(items) * 0.5)
    fig, ax = plt.subplots(figsize=figsize)

    labels = [it["label"] for it in items]
    values = [it["value"] for it in items]
    maxes = [it.get("max", 100) for it in items]
    colors = [it.get("color", COLORS["primary"]) for it in items]
    formats = [it.get("format", "{:.1f}") for it in items]

    y = range(len(items))
    # Background (max range)
    ax.barh(y, maxes, color="#e5e7eb", edgecolor="white", linewidth=1)
    # Foreground (value)
    ax.barh(y, values, color=colors, edgecolor="white", linewidth=1)

    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    if title:
        ax.set_title(title, fontsize=11, fontweight="bold", pad=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(left=False, bottom=False, labelbottom=False)

    for i, (v, m, fmt) in enumerate(zip(values, maxes, formats)):
        try:
            txt = fmt.format(v)
        except Exception:
            txt = str(v)
        ax.text(min(v, m) + m * 0.02, i, txt, va="center", fontsize=8.5,
                color="#1f2937")

    plt.tight_layout()
    return img_tag(fig_to_base64(fig))
