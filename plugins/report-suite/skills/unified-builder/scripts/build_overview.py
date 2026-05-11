#!/usr/bin/env python3
"""Layer 2 — Multi-format overview builder.

Layer 1 (per-stock 44p PDFs)에 대한 overview/summary를 단일 명령으로 생성:
  - overview.md  — 학습용 통합 요약 (Markdown)
  - overview.pdf — Markdown을 WeasyPrint로 PDF 변환 (한글 호환 pdftocairo 후처리)
  - overview.pptx — 8 slides PowerPoint (Cover, Thesis, Top 3, Verdict 종합, Allocation, Risk)

Usage:
  python build_overview.py \\
    --pipeline-dir .analysis-log/bloggers/{blogger}/{slug} \\
    --output-dir .../reports/overview \\
    --formats md pdf pptx
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def build_md(pipeline_dir: Path, output: Path):
    """Generate overview.md."""
    cmd = [sys.executable, str(SCRIPT_DIR / "build_overview_md.py"),
            "--pipeline-dir", str(pipeline_dir),
            "--output", str(output)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[md] failed: {r.stderr}")
        return False
    print(r.stdout.strip())
    return True


def build_pptx(pipeline_dir: Path, output: Path):
    """Generate overview.pptx."""
    cmd = [sys.executable, str(SCRIPT_DIR / "build_overview_pptx.py"),
            "--pipeline-dir", str(pipeline_dir),
            "--output", str(output)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[pptx] failed: {r.stderr}")
        return False
    print(r.stdout.strip())
    return True


def build_pdf_from_md(md_path: Path, pdf_path: Path):
    """Convert Markdown → HTML → PDF (WeasyPrint + pdftocairo)."""
    try:
        from weasyprint import HTML, CSS
    except ImportError:
        print("[pdf] weasyprint not available")
        return False

    # Convert markdown to HTML
    try:
        import markdown as md_lib
    except ImportError:
        print("[pdf] python-markdown not installed — install: pip install markdown")
        return False

    md_text = md_path.read_text()
    html_body = md_lib.markdown(md_text, extensions=["tables", "fenced_code", "nl2br"])

    # Load report-suite CSS for consistent styling
    sys.path.insert(0, str(SCRIPT_DIR.parent.parent / "_common"))
    from css import CSS_BASE  # type: ignore
    from emoji_replace import remove_emoji  # type: ignore

    html_body = remove_emoji(html_body)

    # Wrap with extra CSS for markdown-style content
    extra_css = """
    body { padding: 8mm 12mm; }
    h1 { color: #0d47a1; font-size: 22pt; border-bottom: 3pt solid #0d47a1; padding-bottom: 8pt; }
    h2 { color: #1565c0; font-size: 16pt; border-left: 4pt solid #1565c0; padding-left: 8pt; margin-top: 24pt; }
    h3 { color: #1f2937; font-size: 13pt; margin-top: 16pt; }
    table { width: 100%; border-collapse: collapse; margin: 8pt 0; font-size: 9.5pt; }
    th { background: #f3f4f6; border: 1pt solid #e5e7eb; padding: 6pt 8pt; text-align: left; }
    td { border: 1pt solid #e5e7eb; padding: 5pt 7pt; }
    blockquote { background: #eff6ff; border-left: 3pt solid #2563eb; padding: 6pt 12pt; margin: 6pt 0; font-style: italic; }
    code { background: #f3f4f6; padding: 1pt 4pt; border-radius: 3pt; font-family: 'Noto Sans KR', monospace; font-size: 0.92em; }
    p { line-height: 1.5; }
    """

    html = f"<!doctype html><html><head><meta charset='utf-8'><title>Overview</title></head><body>{html_body}</body></html>"

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".weasy.pdf", delete=False) as tf:
        tmp_pdf = tf.name
    try:
        HTML(string=html).write_pdf(tmp_pdf, stylesheets=[CSS(string=CSS_BASE + extra_css)])
        # pdftocairo post-process for CJK compatibility
        with tempfile.NamedTemporaryFile(suffix=".cairo.pdf", delete=False) as tf2:
            cairo_out = tf2.name
        try:
            subprocess.run(["pdftocairo", "-pdf", tmp_pdf, cairo_out],
                            check=True, capture_output=True, timeout=60)
            import shutil
            shutil.copy(cairo_out, pdf_path)
            Path(cairo_out).unlink(missing_ok=True)
        except Exception as e:
            print(f"[pdf] pdftocairo failed ({e}); using raw WeasyPrint")
            import shutil
            shutil.copy(tmp_pdf, pdf_path)
    finally:
        Path(tmp_pdf).unlink(missing_ok=True)

    import os
    print(f"[pdf] saved {pdf_path} ({os.path.getsize(pdf_path):,} bytes)")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pipeline-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--formats", nargs="+", default=["md", "pdf", "pptx"],
                         choices=["md", "pdf", "pptx"])
    args = parser.parse_args()

    pipeline_dir = Path(args.pipeline_dir)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    md_path = out_dir / "overview.md"
    pdf_path = out_dir / "overview.pdf"
    pptx_path = out_dir / "overview.pptx"

    if "md" in args.formats:
        build_md(pipeline_dir, md_path)

    if "pdf" in args.formats:
        if not md_path.exists():
            build_md(pipeline_dir, md_path)  # PDF needs MD as input
        build_pdf_from_md(md_path, pdf_path)

    if "pptx" in args.formats:
        build_pptx(pipeline_dir, pptx_path)

    print(f"\n[overview] done — {out_dir}")
    for p in (md_path, pdf_path, pptx_path):
        if p.exists():
            import os
            print(f"  ✓ {p.name} ({os.path.getsize(p):,} bytes)")


if __name__ == "__main__":
    main()
