"""정량 metric 교육용 설명 — 학습 친화적 용어 풀이."""

METRIC_GLOSSARY = {
    "forward_pe": {
        "name": "Forward PE (예상 주가수익비율)",
        "formula": "현재 주가 ÷ 향후 12개월 추정 EPS",
        "interpretation": "낮을수록 저평가, 높을수록 고평가. 보통 PE < 12면 deep value, 12-20은 fair, 20-30은 premium, 30+는 expensive growth.",
        "caveats": "Cyclical 주식의 PE가 매우 낮으면 함정 — 시장이 EPS 하락(mean reversion)을 가격화한 신호일 수 있습니다. 'PE 3'은 절대 저평가가 아니라 EPS peak 의심 신호.",
        "rule_of_thumb": "성장주는 PEG로 보완. PEG = PE / EPS 성장률. PEG < 1: undervalued, > 2: overvalued."
    },
    "beta": {
        "name": "베타 (Beta)",
        "formula": "(Cov(주가, 시장) / Var(시장))",
        "interpretation": "1.0 = 시장과 동일 변동성. 1.5 = 시장 대비 1.5배 변동성. 음수 = 시장과 역상관 (시장이 오를 때 떨어짐).",
        "caveats": "베타는 historical — 미래를 보장하지 않습니다. 베타 -0.3 같은 음수는 매우 특이 — idiosyncratic risk(개별 종목 risk) 우세 신호 (예: 임상 결과·M&A 등에 의해 결정).",
        "rule_of_thumb": "보수적 portfolio = 평균 베타 < 1, aggressive = > 1.2. 하지만 베타 외 변동성·drawdown도 함께 봐야 합니다."
    },
    "annualized_volatility": {
        "name": "연환산 변동성 (Annualized Volatility)",
        "formula": "일별 수익률 stdev × √252 거래일",
        "interpretation": "<15% = 저변동성 (대형 우량주), 15-30% = 중간 (시장 평균), 30-50% = 고변동성 (성장주·소형), 50%+ = 매우 고변동성 (bio·commodity·신규 IPO).",
        "caveats": "Risk Manager는 변동성에 따라 position size 한도를 조정 — 변동성 50%+ 종목은 최대 10%까지만 (단일 종목 최대 한도가 base 20% × 0.5 multiplier).",
        "rule_of_thumb": "변동성 10%p 차이는 drawdown 기대치 ~5%p 차이로 대체로 환산."
    },
    "return_1m": {
        "name": "1개월 수익률 (Return 1M)",
        "formula": "(현재가 / 22 거래일 전 가격 - 1) × 100",
        "interpretation": "단기 모멘텀 지표. +20% 이상은 강한 상승세, -20% 이하는 강한 하락세.",
        "caveats": "단기 수익률만 보면 mean reversion 위험 무시. 1M +20%인 종목은 차익실현 매물 + 단기 과열 주의.",
        "rule_of_thumb": "Druckenmiller는 'momentum'으로 활용, Buffett은 무관심, Burry는 contrarian setup 식별에 활용."
    },
    "return_3m_6m_1y": {
        "name": "3M / 6M / 1Y 수익률",
        "formula": "(현재가 / N 거래일 전 가격 - 1) × 100",
        "interpretation": "중장기 추세 확인. 1M·3M·6M·1Y가 모두 양수면 'all-time accumulation' 패턴.",
        "caveats": "1Y +200%+는 cycle 정점 근접 신호일 수 있음 (mean reversion 위험).",
        "rule_of_thumb": "긴 horizon일수록 mean reversion 적용. 1Y +300%는 historically -50% drawdown 동반."
    },
    "vol_multiplier": {
        "name": "변동성-조정 multiplier (vol_multiplier)",
        "formula": "ai-hedge-fund 공식: 변동성<15%→1.25, <30%→점진감소, 50%+→0.50",
        "interpretation": "Risk Manager가 종목의 연환산 변동성에 따라 단일 종목 최대 한도를 조정. 저변동성 → bonus, 고변동성 → penalty.",
        "caveats": "변동성만으로는 불충분 — drawdown·tail risk·correlation 종합 평가.",
        "rule_of_thumb": "기본 한도 20%에 multiplier 곱: 저변동성 = 25%, 고변동성 = 10%."
    },
    "combined_limit_pct": {
        "name": "종합 포지션 한도 (combined limit %)",
        "formula": "base_limit (20%) × vol_multiplier × correlation_multiplier",
        "interpretation": "이 종목에 portfolio 가치 대비 최대 몇 %까지 집중 가능한지. 11%면 ₩14억 portfolio 기준 ₩1.54억 한도.",
        "caveats": "한도는 cap. 실제 진입 size는 signal_score에 따라 한도의 50%·100% 등 조정.",
        "rule_of_thumb": "변동성 + 활성 포지션과의 상관관계로 결정. 보수적 운영은 11-16% 한도가 일반적."
    },
}


VERDICT_INTERPRETATION = {
    "lean_bullish": "약한 매수 성향. 대가가 매수를 권하지만 강한 conviction은 아님. position size는 한도의 50% 정도가 적절.",
    "lean_bearish": "약한 매도 성향. 대가가 신중을 권함. 보유 중이면 partial sell 검토.",
    "neutral": "중립. 대가가 buy/sell 모두 어려움. Hold 또는 진입 보류.",
    "BUY": "강한 매수 권고. 한도까지 진입 가능.",
    "SELL": "강한 매도 권고. 보유 중이면 청산.",
    "HOLD": "보유. 신규 진입 X.",
}


CONFIDENCE_INTERPRETATION = {
    "very_high": "(80%+) 매우 강한 conviction. 시장에 alpha 있는 신호. Druckenmiller 'bet the ranch' zone.",
    "high": "(60-80%) 일반적인 high-conviction. 표준 position size.",
    "medium": "(40-60%) 보수적 신뢰도. 한도의 50% 또는 분할 매수.",
    "low": "(<40%) 약한 신호. 진입 회피 또는 매우 작은 position.",
}


def render_metric_glossary() -> str:
    """R1·R3에 추가할 정량 metric 학습 박스."""
    rows = ""
    for k, v in METRIC_GLOSSARY.items():
        rows += f"""
        <tr>
          <td><strong>{v['name']}</strong></td>
          <td><code style="font-size:8.5pt;">{v['formula']}</code></td>
          <td style="font-size:9pt;"><strong>해석</strong>: {v['interpretation']}<br/>
              <strong>주의</strong>: {v['caveats']}<br/>
              <strong>Rule of thumb</strong>: {v['rule_of_thumb']}</td>
        </tr>
        """
    return f"""
    <h2>📚 정량 Metric 용어 풀이 (학습용)</h2>
    <div class="info">이 보고서에 등장하는 정량 지표들의 의미·계산식·해석 방법·주의점을 정리했습니다. 처음 보시는 metric은 본 표를 참고하세요.</div>
    <table class="dt">
      <thead><tr><th style="width:18%">Metric</th><th style="width:25%">계산식</th><th>해석·주의·Rule of Thumb</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    """


def render_data_tag_education() -> str:
    """데이터 태깅 시스템 교육."""
    return """
    <h2>📚 데이터 태깅 시스템 — [actual] / [inference] / [assumption]</h2>
    <div class="info">우리 시스템은 모든 분석 숫자에 의무적으로 출처 태그를 붙입니다. 이는 환각 방지와 분석 신뢰도 측정의 핵심입니다.</div>
    <table class="dt">
      <thead><tr><th>태그</th><th>의미</th><th>예시</th></tr></thead>
      <tbody>
        <tr>
          <td><span class="tag-actual">[actual]</span></td>
          <td><strong>검증된 사실</strong>. 사업보고서·정부 공시·yfinance 등 1차 출처 확인 가능.</td>
          <td>"forward PE 3.76 [actual]" — yfinance 직접 확인</td>
        </tr>
        <tr>
          <td><span class="tag-inference">[inference]</span></td>
          <td><strong>사실에서 도출한 추론</strong>. 데이터에서 합리적으로 유추 가능하나 직접 측정 안 됨.</td>
          <td>"향후 10년 ROE 18%+ 유지 가능 [inference]" — historical pattern 기반 추론</td>
        </tr>
        <tr>
          <td><span class="tag-assumption">[assumption]</span></td>
          <td><strong>분석가 가정</strong>. 사실로 검증되지 않은 미래 가정. 가정이 깨지면 verdict 변경.</td>
          <td>"정유 마진 정상화 [assumption]" — 만약 마진 회복이 안 되면 verdict 약화</td>
        </tr>
        <tr>
          <td><span class="tag-derived">[derived]</span></td>
          <td><strong>계산된 값</strong>. 직접 측정은 아니나 정량 데이터로 도출.</td>
          <td>"PEG 0.5 [derived]" — PE 7 / EPS 성장률 14%로 직접 계산</td>
        </tr>
        <tr>
          <td><span class="tag-actual" style="background:#e5e7eb;color:#374151;">[unavailable]</span></td>
          <td><strong>데이터 부재</strong>. 평가에 필요한 데이터가 없어 추론 불가.</td>
          <td>"NCAV [unavailable]" — 사업보고서 미공시</td>
        </tr>
      </tbody>
    </table>
    <p style="font-size:9pt;color:#6b7280;margin-top:6pt;">
      <strong>왜 중요한가</strong>: [actual] 비율이 높을수록 분석이 사실 기반. [assumption] 비율이 높으면
      가정 fragility 위험 — 가정 하나가 깨지면 verdict 전체가 흔들립니다. 우리 시스템은 모든 verdict의
      [actual]/[assumption] 비율을 추적해 분석 강도를 측정합니다.
    </p>
    """
