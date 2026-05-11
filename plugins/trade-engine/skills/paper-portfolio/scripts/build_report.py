#!/usr/bin/env python3
"""Paper Portfolio PDF — Phase A 결과 시각화."""
import argparse
import json
from pathlib import Path
from weasyprint import HTML, CSS


CSS_TEXT = """
@page { size: A4; margin: 18mm 14mm; @bottom-center { content: counter(page) " / " counter(pages); font-size: 9pt; color: #6b7280; } }
body { font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif; color: #1f2937; line-height: 1.5; font-size: 10pt; }
h1 { color: #111; font-size: 22pt; border-bottom: 2pt solid #2563eb; padding-bottom: 8pt; }
h2 { color: #111827; margin-top: 22pt; border-left: 4pt solid #2563eb; padding-left: 8pt; }
h3 { margin-top: 16pt; font-size: 12pt; }
.cover { page-break-after: always; padding-top: 3cm; text-align: center; }
.cover h1 { border: none; font-size: 28pt; }
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10pt; margin: 12pt 0; }
.kpi { background: #f9fafb; padding: 14pt; border-left: 3pt solid #2563eb; text-align: center; }
.kpi .num { font-size: 22pt; font-weight: 700; color: #111; }
.kpi .num.green { color: #16a34a; } .kpi .num.red { color: #dc2626; }
.kpi .label { font-size: 9pt; color: #6b7280; margin-top: 4pt; }
table.dt { width: 100%; border-collapse: collapse; font-size: 9.5pt; margin: 8pt 0; }
table.dt th, table.dt td { border: 1pt solid #e5e7eb; padding: 5pt 7pt; text-align: left; }
table.dt th { background: #f3f4f6; }
.note { background: #fef3c7; padding: 10pt 14pt; border-left: 3pt solid #f59e0b; margin: 8pt 0; }
.win { background: #f0fdf4; padding: 8pt 12pt; border-left: 3pt solid #16a34a; margin: 6pt 0; }
"""


def fmt_money(v: float) -> str:
    if abs(v) >= 100_000_000:
        return f"₩{v/100_000_000:.2f}억"
    if abs(v) >= 10_000:
        return f"₩{v/10_000:.0f}만"
    return f"₩{v:,.0f}"


def fmt_pct(v: float) -> str:
    sign = "+" if v >= 0 else ""
    return f"{sign}{v:.2f}%"


def render(p: dict) -> str:
    invested = sum(pos["avg_cost"] * pos["qty"] for pos in p["final_positions"].values())
    unrealized_pnl = sum(pos["unrealized_pnl"] for pos in p["final_positions"].values())
    unrealized_return = (unrealized_pnl / invested * 100) if invested > 0 else 0
    cash_ratio = p["final_cash"] / p["final_nav"] * 100

    cover = f"""
    <div class="cover">
      <p style="color:#6b7280;font-size:11pt;">Phase A — Trade Engine Paper Portfolio · {p.get('computed_at', '')[:10]}</p>
      <h1>13 Personas → Risk-Adjusted Trade<br/>모의 포트폴리오 시뮬레이션</h1>
      <p style="color:#6b7280;">{p['start_date']} → {p['end_date']}</p>
      <div class="kpi-grid">
        <div class="kpi">
          <div class="num">{fmt_money(p['start_cash'])}</div>
          <div class="label">Start Capital</div>
        </div>
        <div class="kpi">
          <div class="num">{fmt_money(p['final_nav'])}</div>
          <div class="label">Final NAV</div>
        </div>
        <div class="kpi">
          <div class="num {'green' if p['total_return_pct'] > 0 else 'red'}">{fmt_pct(p['total_return_pct'])}</div>
          <div class="label">Total Return</div>
        </div>
        <div class="kpi">
          <div class="num">{p['total_trades']}</div>
          <div class="label">Trades</div>
        </div>
      </div>
    </div>
    """

    positions_rows = ""
    for t, pos in p["final_positions"].items():
        color = "#16a34a" if pos["unrealized_return_pct"] > 0 else "#dc2626"
        positions_rows += f"""
        <tr>
          <td><strong>{t}</strong></td>
          <td>{pos['qty']:,}주</td>
          <td>₩{pos['avg_cost']:,.0f}</td>
          <td>₩{pos['last_price']:,.0f}</td>
          <td>{fmt_money(pos['market_value'])}</td>
          <td style="color:{color};font-weight:600;">{fmt_pct(pos['unrealized_return_pct'])}</td>
        </tr>
        """

    bench_rows = ""
    for b, m in p["benchmark_comparison"].items():
        alpha_color = "#16a34a" if m['alpha_pct'] > 0 else "#dc2626"
        bench_rows += f"""
        <tr>
          <td><strong>{b}</strong></td>
          <td>{fmt_pct(m['return_pct'])}</td>
          <td style="color:{alpha_color};font-weight:600;">{fmt_pct(m['alpha_pct'])}</td>
        </tr>
        """

    trade_rows = ""
    for t in p["trade_log"]:
        action_icon = {"buy": "🟢", "sell_all": "🔴", "sell_partial": "🟡"}.get(t['action'], "⚪")
        amount_str = fmt_money(t.get('cost') or t.get('proceeds') or 0)
        trade_rows += f"""
        <tr>
          <td>{t['date']}</td>
          <td>{action_icon} {t['action']}</td>
          <td><strong>{t['ticker']}</strong></td>
          <td>{t['qty']:,}주 @ ₩{t['price']:,.0f}</td>
          <td>{amount_str}</td>
        </tr>
        """

    body = f"""
    {cover}

    <h2>1. 핵심 결과 — Phase A 시스템이 만든 alpha</h2>

    <div class="kpi-grid">
      <div class="kpi"><div class="num green">{fmt_pct(unrealized_return)}</div><div class="label">투자된 자본 수익률</div></div>
      <div class="kpi"><div class="num">{fmt_money(invested)}</div><div class="label">투자된 자본</div></div>
      <div class="kpi"><div class="num">{cash_ratio:.0f}%</div><div class="label">Cash 비율 (NAV 대비)</div></div>
      <div class="kpi"><div class="num">{p['n_decisions']}</div><div class="label">Trade Decisions</div></div>
    </div>

    <div class="note">
      <strong>핵심 인사이트</strong>: 시스템이 $1.4B KRW 시작자본 중 약 {100-cash_ratio:.0f}%만 투자(나머지는 Risk Manager의 변동성-조정 한도 때문에 보유 cash). 그러나 <strong>투자된 자본 기준 수익률은 {fmt_pct(unrealized_return)}</strong>. Risk Manager의 보수적 sizing이 absolute return은 낮추지만 risk-adjusted 측면에서는 합리적.
    </div>

    <h2>2. 최종 포지션 (mark-to-market)</h2>
    <table class="dt">
      <thead><tr><th>종목</th><th>수량</th><th>평단</th><th>현재가</th><th>평가액</th><th>미실현 P&amp;L</th></tr></thead>
      <tbody>{positions_rows}</tbody>
    </table>

    <h2>3. 벤치마크 비교</h2>
    <table class="dt">
      <thead><tr><th>Benchmark</th><th>같은 기간 Return</th><th>Alpha (NAV 기준)</th></tr></thead>
      <tbody>{bench_rows}</tbody>
    </table>

    <div class="win">
      <strong>SK하이닉스 (000660.KS)</strong>: signal +0.77로 한도까지 진입 → unrealized {fmt_pct(p['final_positions'].get('000660.KS', {}).get('unrealized_return_pct', 0))}.
      Druckenmiller·Lynch가 모두 lean_bullish 평가한 결과, 1.54억원 투자가 약 3.7억원으로 성장.
    </div>

    <h2>4. Trade Log</h2>
    <table class="dt">
      <thead><tr><th>Date</th><th>Action</th><th>Ticker</th><th>Qty × Price</th><th>금액</th></tr></thead>
      <tbody>{trade_rows}</tbody>
    </table>

    <h2>5. 시스템 작동 방식 — Risk Manager → Portfolio Manager</h2>
    <p>이번 시뮬레이션은 다음 단계를 거쳤습니다:</p>
    <ol>
      <li><strong>분석</strong> (Phase 0): 메르 글 5개에서 18 verdict 생성 (thesis-first + Buffett + Lynch + Druckenmiller)</li>
      <li><strong>Risk Manager</strong> (Phase A.1): 각 (ticker, date) 쌍에 대해 60일 변동성 → position 한도 계산
        <ul>
          <li>SK하이닉스 vol 67% → limit 11.0% (₩1.54억)</li>
          <li>삼성전자 vol 42% → limit 15.2% (₩2.13억)</li>
          <li>한화오션 vol 59% → limit 11.0% (₩1.54억)</li>
          <li>금ETF vol 19% → limit 21.6% (₩3.02억) — 저변동성 보너스</li>
        </ul>
      </li>
      <li><strong>Portfolio Manager</strong> (Phase A.2): verdict aggregate (페르소나별 가중치) → signal_score → action 결정
        <ul>
          <li>signal ≥ +0.7 → buy 한도까지 (SK하이닉스 +0.77, 한화오션 +0.78)</li>
          <li>+0.3 ≤ signal &lt; +0.7 → buy 한도의 50% (삼성전자 +0.45)</li>
          <li>signal ≤ -0.7 → sell_all (금ETF -0.70)</li>
        </ul>
      </li>
      <li><strong>Paper Portfolio</strong> (Phase A.3): 시점별 cash·position 누적, 최종 NAV mark-to-market</li>
    </ol>

    <h2>6. 한계 및 다음 단계</h2>
    <ul>
      <li><strong>샘플 크기</strong>: 5 글 × 4 source = 18 verdict — 통계적 유의미성 확보엔 30+ 글 필요</li>
      <li><strong>Cash drag</strong>: 변동성-조정 한도가 보수적이라 KOSPI 폭등기에 underperform. Phase B(LangGraph) 또는 leveraged 옵션으로 해결 가능</li>
      <li><strong>다중통화</strong>: SLV(USD)와 한국 종목(KRW)이 같은 portfolio_value로 처리됨 — 환율 overlay 필요</li>
      <li><strong>Rebalancing 부재</strong>: 단일 시점 진입 후 보유. 정기 rebalance 로직 미포함</li>
    </ul>

    <div class="note">
      ⚠️ <strong>주의</strong>: 본 결과는 paper portfolio simulation입니다. 실제 거래는 사용자가 별도 증권사 시스템에서 실행해야 하며, 본 시스템은 어떤 자동 거래도 수행하지 않습니다.
    </div>
    """

    return body


def main():
    parser = argparse.ArgumentParser(description="Paper Portfolio PDF")
    parser.add_argument("portfolio_json")
    parser.add_argument("--output", "-o", required=True)
    args = parser.parse_args()

    with open(args.portfolio_json, encoding="utf-8") as f:
        p = json.load(f)

    body = render(p)
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Phase A Paper Portfolio</title></head>
<body>{body}</body></html>"""

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html).write_pdf(args.output, stylesheets=[CSS(string=CSS_TEXT)])

    import os
    print(f"[paper-portfolio-pdf] saved: {args.output} ({os.path.getsize(args.output):,} bytes)")


if __name__ == "__main__":
    main()
