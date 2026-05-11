---
name: list-analyses
description: 지금까지 수행된 모든 분석 (블로거별 + standalone) 리스트 출력 + 각 분석의 핵심 verdict 요약.
---

수행된 모든 분석을 조회합니다:

```bash
cd "/Users/mingyukang/Documents/Claude/Projects/주식 분석"

echo "=== 블로거별 분석 ==="
find .analysis-log/bloggers -maxdepth 2 -type d -mindepth 2 2>/dev/null | sort | while read dir; do
    blogger=$(echo "$dir" | awk -F/ '{print $(NF-1)}')
    slug=$(basename "$dir")
    pdf_count=$(find "$dir/reports" -name "*.pdf" 2>/dev/null | wc -l)
    echo "  📂 $blogger / $slug — $pdf_count PDFs"
done

echo ""
echo "=== Standalone 분석 ==="
find .analysis-log/standalone -maxdepth 1 -type d -mindepth 1 2>/dev/null | sort | while read dir; do
    slug=$(basename "$dir")
    pdf_count=$(find "$dir/reports" -name "*.pdf" 2>/dev/null | wc -l)
    echo "  📂 $slug — $pdf_count PDFs"
done
```

각 분석의 verdict 요약은 `decisions.json`에서:

```bash
for f in .analysis-log/*/*/*/decisions.json; do
    echo "$f:"
    python3 -c "
import json
d = json.load(open('$f'))
for x in d.get('decisions',[]):
    print(f'  {x.get(\"ticker\")}: {x.get(\"action\")} (signal {x.get(\"signal_score\",0):+.2f})')"
done
```
