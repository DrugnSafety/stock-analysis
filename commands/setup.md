---
name: setup
description: 시스템 초기 셋업 점검 — 환경변수, 폰트, Python packages, 외부 도구 (ghostscript, pdftocairo) 확인.
---

분석 시스템 초기 셋업을 점검합니다:

## 1. 환경변수 확인

```bash
cd "/Users/mingyukang/Documents/Claude/Projects/주식 분석"
echo "=== .env 파일 ==="
[ -f .env ] && echo "  ✓ .env exists" || echo "  ✗ .env MISSING"
grep -c "OPENAI_API_KEY=sk" .env 2>/dev/null && echo "  ✓ OPENAI_API_KEY set" || echo "  ✗ OPENAI_API_KEY missing"
grep -c "DART_API_KEY=" .env 2>/dev/null && echo "  ✓ DART_API_KEY set (한국 종목 공시)" || echo "  ⚠ DART_API_KEY missing (한국 종목 분석 시 필요)"
grep -c "NEWSAPI_KEY=." .env 2>/dev/null && echo "  ✓ NEWSAPI_KEY set (미국 종목 뉴스)" || echo "  ⚠ NEWSAPI_KEY missing (선택 — 미국 종목 뉴스용)"
grep -c "FINNHUB_KEY=." .env 2>/dev/null && echo "  ✓ FINNHUB_KEY set (미국 종목 뉴스)" || echo "  ⚠ FINNHUB_KEY missing (선택 — 미국 종목 뉴스용)"
echo "  ℹ SEC EDGAR — API 키 불필요 (User-Agent header만 필요, 기본값 작동)"
```

## 2. Python 패키지 점검

```bash
python3 -c "
import importlib
for pkg in ['weasyprint', 'matplotlib', 'yfinance', 'pypdf', 'requests', 'openai', 'google.generativeai']:
    try:
        importlib.import_module(pkg)
        print(f'  ✓ {pkg}')
    except ImportError:
        print(f'  ✗ {pkg} — install: pip install --break-system-packages {pkg}')
"
```

## 3. 한글 폰트 확인

```bash
fc-list | grep -i "noto.*kr" | head -3 && echo "  ✓ Noto Sans KR installed" \
  || echo "  ✗ Noto Sans KR MISSING — download from Google Fonts and place in ~/.fonts/"
```

## 4. 외부 도구 확인

```bash
which pdftocairo && echo "  ✓ pdftocairo (Cairo PDF post-processing)" || echo "  ✗ pdftocairo MISSING — install poppler-utils"
which gs && echo "  ✓ ghostscript" || echo "  ⚠ ghostscript optional"
```

## 5. Plugin 디렉토리 점검

```bash
for p in backtester blogger-registry dart-integration sec-edgar-integration news-integration investor-personas multi-model-arena report-suite subagent-orchestrator trade-engine; do
    [ -f "plugins/$p/plugin.json" ] && echo "  ✓ $p/plugin.json" || echo "  ✗ $p/plugin.json MISSING"
done
```

## 6. 설치 명령 (필요 시)

```bash
# Python packages
pip install --break-system-packages weasyprint matplotlib yfinance pypdf requests openai google-generativeai

# Korean font (macOS)
mkdir -p ~/.fonts
curl -L "https://fonts.google.com/download?family=Noto%20Sans%20KR" -o /tmp/notokr.zip
unzip /tmp/notokr.zip -d ~/.fonts/
fc-cache -fv

# Poppler (macOS)
brew install poppler

# Poppler (Ubuntu/Debian)
sudo apt-get install poppler-utils
```
