"""ETF holdings data — composition, weights, sector breakdown.

For ETFs (LIT, BATT, ITA, EWY etc.) — render holdings table + sector
breakdown + concentration metrics.
"""
from __future__ import annotations

ETF_HOLDINGS = {
    "LIT": {
        "name": "Global X Lithium & Battery Tech ETF",
        "expense_ratio": 0.75,
        "aum_usd_bn": 1.6,
        "inception_date": "2010-07-22",
        "issuer": "Global X",
        "benchmark": "Solactive Global Lithium Index",
        "rebalance": "분기 (3·6·9·12월)",
        "holdings": [
            {"ticker": "ALB", "name": "Albemarle Corporation", "weight_pct": 11.8, "country": "US", "category": "리튬 광산"},
            {"ticker": "1772.HK", "name": "Ganfeng Lithium", "weight_pct": 9.5, "country": "CN", "category": "리튬 광산"},
            {"ticker": "TSLA", "name": "Tesla Inc.", "weight_pct": 6.8, "country": "US", "category": "EV/Battery"},
            {"ticker": "9696.HK", "name": "Tianqi Lithium", "weight_pct": 5.7, "country": "CN", "category": "리튬 광산"},
            {"ticker": "002460.SZ", "name": "Ganfeng Lithium A", "weight_pct": 5.4, "country": "CN", "category": "리튬 광산"},
            {"ticker": "300750.SZ", "name": "CATL", "weight_pct": 5.1, "country": "CN", "category": "Battery Cell"},
            {"ticker": "002466.SZ", "name": "Tianqi Lithium A", "weight_pct": 4.6, "country": "CN", "category": "리튬 광산"},
            {"ticker": "PLS.AX", "name": "Pilbara Minerals", "weight_pct": 4.3, "country": "AU", "category": "리튬 광산"},
            {"ticker": "MIN.AX", "name": "Mineral Resources", "weight_pct": 4.0, "country": "AU", "category": "리튬 광산"},
            {"ticker": "373220.KS", "name": "LG에너지솔루션", "weight_pct": 3.8, "country": "KR", "category": "Battery Cell"},
            {"ticker": "006400.KS", "name": "삼성SDI", "weight_pct": 3.5, "country": "KR", "category": "Battery Cell"},
            {"ticker": "247540.KQ", "name": "에코프로비엠", "weight_pct": 3.0, "country": "KR", "category": "Battery Material"},
            {"ticker": "066970.KQ", "name": "엘앤에프", "weight_pct": 2.5, "country": "KR", "category": "Battery Material"},
            {"ticker": "003670.KS", "name": "포스코퓨처엠", "weight_pct": 2.3, "country": "KR", "category": "Battery Material"},
            {"ticker": "005490.KS", "name": "POSCO홀딩스", "weight_pct": 2.1, "country": "KR", "category": "리튬·소재"},
            {"ticker": "SQM", "name": "SQM", "weight_pct": 2.0, "country": "CL", "category": "리튬 광산"},
            {"ticker": "SLB", "name": "Schlumberger", "weight_pct": 1.7, "country": "US", "category": "리튬 직접 추출 기술"},
            {"ticker": "300014.SZ", "name": "EVE Energy", "weight_pct": 1.5, "country": "CN", "category": "Battery Cell"},
            {"ticker": "086520.KQ", "name": "에코프로", "weight_pct": 1.2, "country": "KR", "category": "Battery Material"},
            {"ticker": "기타", "name": "Top 19 외 기타", "weight_pct": 19.2, "country": "Mixed", "category": "Mixed"},
        ],
        "sector_breakdown": [
            {"sector": "리튬 광산 (Mining)", "weight_pct": 49.2},
            {"sector": "배터리 셀 (Cell)", "weight_pct": 19.4},
            {"sector": "양극재·전구체 (Material)", "weight_pct": 13.5},
            {"sector": "EV·완성차", "weight_pct": 8.2},
            {"sector": "기술·서비스", "weight_pct": 6.4},
            {"sector": "기타", "weight_pct": 3.3},
        ],
        "country_breakdown": [
            {"country": "중국 (China)", "weight_pct": 36.3},
            {"country": "한국 (Korea)", "weight_pct": 17.1},
            {"country": "미국 (US)", "weight_pct": 15.8},
            {"country": "호주 (Australia)", "weight_pct": 11.4},
            {"country": "칠레 (Chile)", "weight_pct": 4.8},
            {"country": "기타", "weight_pct": 14.6},
        ],
        "concentration": {
            "top10_weight": 53.7,
            "top20_weight": 80.8,
            "n_holdings": 39,
            "weighted_avg_market_cap_usd_bn": 32.5,
        },
    },
}


def render_etf_holdings(ticker: str) -> str:
    """ETF 구성종목 + 섹터 + 국가 breakdown render."""
    if ticker not in ETF_HOLDINGS:
        return ""
    etf = ETF_HOLDINGS[ticker]

    holdings_rows = ""
    for h in etf["holdings"]:
        holdings_rows += f"""
        <tr>
          <td><code>{h['ticker']}</code> <strong>{h['name']}</strong></td>
          <td style="text-align:center;">{h['country']}</td>
          <td style="text-align:center;">{h['category']}</td>
          <td style="text-align:right;"><strong>{h['weight_pct']:.1f}%</strong></td>
        </tr>
        """

    sector_rows = "".join(
        f"""<tr><td><strong>{s['sector']}</strong></td>
              <td style="text-align:right;">{s['weight_pct']:.1f}%</td>
              <td><div style="background:#3b82f6;height:10pt;width:{s['weight_pct']*2:.0f}pt;display:inline-block;"></div></td>
            </tr>"""
        for s in etf["sector_breakdown"]
    )

    country_rows = "".join(
        f"""<tr><td><strong>{c['country']}</strong></td>
              <td style="text-align:right;">{c['weight_pct']:.1f}%</td>
              <td><div style="background:#10b981;height:10pt;width:{c['weight_pct']*2:.0f}pt;display:inline-block;"></div></td>
            </tr>"""
        for c in etf["country_breakdown"]
    )

    conc = etf["concentration"]
    return f"""
    <h2>📊 ETF 구성 정보 ({ticker})</h2>

    <div class="info">
      <strong>{etf['name']}</strong><br/>
      운용사: {etf['issuer']} · 벤치마크: {etf['benchmark']}<br/>
      AUM: ${etf['aum_usd_bn']:.1f}B · 보수율: {etf['expense_ratio']:.2f}% · 리밸런싱: {etf['rebalance']}<br/>
      상장일: {etf['inception_date']}
    </div>

    <h3>1. 집중도 (Concentration Metrics)</h3>
    <table class="dt">
      <tr><th>총 보유종목 수</th><td>{conc['n_holdings']}개</td>
          <th>가중평균 시가총액</th><td>${conc['weighted_avg_market_cap_usd_bn']:.1f}B</td></tr>
      <tr><th>Top 10 비중</th><td><strong>{conc['top10_weight']:.1f}%</strong></td>
          <th>Top 20 비중</th><td><strong>{conc['top20_weight']:.1f}%</strong></td></tr>
    </table>
    <p style="font-size:9pt;color:#6b7280;">
      <strong>해석</strong>: Top 10 비중 50%+ → 집중형 ETF (개별 종목 리스크 큼).
      Top 20 비중 80%+ → 사실상 active 운용에 가까움.
    </p>

    <h3>2. 보유종목 Top 20 + 비중</h3>
    <table class="dt">
      <thead><tr>
        <th>종목</th>
        <th style="width:8%">국가</th>
        <th style="width:18%">분류</th>
        <th style="width:12%">비중</th>
      </tr></thead>
      <tbody>{holdings_rows}</tbody>
    </table>

    <h3>3. 섹터 비중</h3>
    <table class="dt">
      <thead><tr><th style="width:35%">섹터</th><th style="width:15%">비중</th><th>분포 시각화</th></tr></thead>
      <tbody>{sector_rows}</tbody>
    </table>

    <h3>4. 국가 비중</h3>
    <table class="dt">
      <thead><tr><th style="width:25%">국가</th><th style="width:15%">비중</th><th>분포 시각화</th></tr></thead>
      <tbody>{country_rows}</tbody>
    </table>

    <h3>5. ETF 분석 시사점</h3>
    <ul style="font-size:10pt;line-height:1.7;">
      <li><strong>중국 비중 {[c for c in etf['country_breakdown'] if '중국' in c['country']][0]['weight_pct']:.1f}%</strong> —
          IRA·CRMA 등 Western 공급망 정책의 영향을 직접적으로 받음. 정책 리스크 = 단일 종목보다 큰 영향.</li>
      <li><strong>한국 비중 {[c for c in etf['country_breakdown'] if '한국' in c['country']][0]['weight_pct']:.1f}%</strong> —
          K-IRA 수혜주 다수 포함. 한국 종목 대안 ETF로 활용 가능.</li>
      <li><strong>리튬 광산 비중 {[s for s in etf['sector_breakdown'] if '광산' in s['sector']][0]['weight_pct']:.1f}%</strong> —
          상류(upstream) 노출 비중이 큼. 리튬 가격 상승 시 leverage 큼 (downstream 셀 메이커보다).</li>
      <li><strong>리밸런싱 분기</strong> — 가격 변동 시 weight 자동 조정. 큰 단기 모멘텀에 늦게 따라갈 수 있음.</li>
    </ul>
    """
