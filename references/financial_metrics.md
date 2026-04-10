# Financial Metrics Reference

Calculation formulas for all metrics used in Phase 2 (Financial Analysis). All inputs come from `financial_data.json`.

---

## Profitability Metrics (盈利能力)

| Metric | Formula | Unit | Notes |
|--------|---------|------|-------|
| Gross Margin | `gross_profit / revenue × 100` | % | Higher = more pricing power |
| Operating Margin | `operating_income / revenue × 100` | % | Before interest & tax |
| Net Margin | `net_income / revenue × 100` | % | Bottom-line profitability |
| EBITDA | `operating_income + D&A` | $ M | D&A from cash flow or notes; estimate if unavailable |
| EBITDA Margin | `EBITDA / revenue × 100` | % | — |
| ROE | `net_income / total_equity × 100` | % | Return on shareholders' equity |
| ROA | `net_income / total_assets × 100` | % | Asset efficiency |

---

## Growth Metrics (增长)

| Metric | Formula | Unit | Notes |
|--------|---------|------|-------|
| Revenue Growth YoY | `(current_revenue - prior_revenue) / prior_revenue × 100` | % | — |
| Net Income Growth YoY | `(current_NI - prior_NI) / prior_NI × 100` | % | Use absolute value of prior if prior is negative |
| EPS Growth YoY | `(current_EPS - prior_EPS) / prior_EPS × 100` | % | Diluted EPS |
| Gross Profit Growth YoY | `(current_GP - prior_GP) / prior_GP × 100` | % | — |

---

## Cash Flow Metrics (现金流)

| Metric | Formula | Unit | Notes |
|--------|---------|------|-------|
| Free Cash Flow | `operating_cash_flow - capex` | $ M | CapEx is negative in JSON; add (subtract the negative) |
| FCF Margin | `free_cash_flow / revenue × 100` | % | — |
| FCF Conversion | `free_cash_flow / net_income × 100` | % | >100% = high quality earnings |
| CapEx Intensity | `|capex| / revenue × 100` | % | Lower = asset-light business model |

---

## Leverage Metrics (杠杆)

| Metric | Formula | Unit | Notes |
|--------|---------|------|-------|
| Debt/Equity | `total_debt / total_equity` | ratio | >2x = highly leveraged |
| Net Debt | `total_debt - cash_and_equivalents - short_term_investments` | $ M | Negative = net cash position |
| Net Debt/EBITDA | `net_debt / EBITDA` | ratio | <2x = comfortable; >4x = stressed |
| Interest Coverage | `operating_income / interest_expense` | ratio | >3x = comfortable; <2x = concerning |

---

## Valuation Metrics (估值，if market data available)

These require additional web searches for current market data. Mark as "N/A (market data unavailable)" if you cannot retrieve reliable figures.

| Metric | Formula | Unit | How to obtain market data |
|--------|---------|------|--------------------------|
| P/E Ratio | `current_stock_price / diluted_EPS` | ratio | `web_search "{ticker} stock price today"` |
| Market Cap | `current_stock_price × diluted_shares` | $ M | Same search |
| Enterprise Value | `market_cap + total_debt - cash - short_term_investments` | $ M | Calculate from above |
| EV/EBITDA | `enterprise_value / EBITDA` | ratio | — |
| P/FCF | `market_cap / free_cash_flow` | ratio | — |

---

## Trend Classification Logic

For Net Income, Net Margin, and FCF, classify the trend and write the corresponding analysis (2–3 sentences of plain prose only — no Markdown asterisk bold/italic in JSON fields; they paste into HTML as-is):

```
IF current_year > prior_year (improvement):
    trend_label = "↑ Increasing"
    trend_class = "positive"
    Write 2-3 sentences on growth drivers:
      - Volume growth? Price increases? Operating leverage?
      - Segment mix shift?
      - Cost reduction / efficiency gains?

ELSE IF current_year < prior_year (decline):
    trend_label = "↓ Decreasing"
    trend_class = "negative"
    Write 2-3 sentences on risk factors:
      - Revenue decline or margin compression?
      - Rising cost pressures?
      - One-time charges or structural issues?

ELSE:
    trend_label = "→ Stable"
    trend_class = "neutral"
```

---

## Geographic revenue mix (地区收入结构)

In Phase 2, after computing ratios and trend narratives, write a short **regional revenue** note for Section II’s fourth trend-card (**标题：地区收入结构**; English template: **Geographic revenue mix**). The card uses CSS class **`trend-geo`** (green left accent); content must stay **descriptive only**.

- Source **regional / country revenue tables** from the latest annual/quarterly filing (or `financial_data.json` geographic breakdown if Agent 1 populated it). If only product segments exist, say geographic disclosure is limited.
- Cover **amounts, % of total**, YoY or organic growth **by region** when disclosed, and **concentration** (e.g. top region share changing).
- **Scope:** Currency translation, hedging, and broad FX/DXY discussion belong in **Section III** / `macro_factors.json`, not in this card.
- **Tone:** Write **only** substantive facts from disclosures — do **not** paste boilerplate such as “this section does not discuss FX/DXY”; that is an author instruction, not reader-facing copy.

Store the prose in **`financial_analysis.json`** → `geographic_revenue.analysis`. Phase 5 pastes it into `{{GEO_REVENUE_TEXT}}`. Use plain text only (no Markdown bold/italic); HTML does not render `**`.

**Phase 5 — `{{TREND1_DIRECTION}}` … `{{TREND3_DIRECTION}}`:** Map `trends.*.class` to the template’s CSS tokens: `positive` → `up`, `negative` → `down`, `neutral` → `up` (or `down` if the narrative fits). Do **not** emit `negative` or `positive` as the div class — those are not styled. All four trend cards use a **green** left border in the locked template; `up`/`down` are semantic only.

---

## Fiscal year convention (和财报表格「当年/上年」对齐)

- **`income_statement.current_year` / `prior_year` in `financial_data.json`** define the two fiscal years used for Section II, KPIs, and YoY narratives.
- **同比** = `prior_year` → `current_year` as **two consecutive full fiscal years** (e.g. FY2024 → FY2025). It is **not** “skip a year” or “FY2024 vs FY2026.”
- **Calendar anchor (`Y_cal`):** See **`SKILL.md` Step 0C**. When the report folder date is in calendar **2026**, Agent 1 **must** first try **`FY2025` vs `FY2024`** (latest **published** annual normally **`FY(Y_cal − 1)`**). Use **FY2024 vs FY2023** only if **FY2025** annual is **not yet published** — and **`notes[]`** must say so.
- **Sankey:** “Actual” tab = **`current_year`** P&L; “Forecast” tab = **`FY(latest_actual + 1)E`** scaled by model growth, aligned with **`prediction_waterfall.json` → `predicted_fiscal_year_label`**.
- Interim periods (e.g. 9M) require explicit labeling if used; default remains **last two complete fiscal years**.

---

## Output Schema

Save to `workspace/{Company}_{Date}/financial_analysis.json`:

```json
{
  "profitability": {
    "gross_margin_current": 46.2,
    "gross_margin_prior": 46.2,
    "operating_margin_current": 29.7,
    "operating_margin_prior": 29.8,
    "net_margin_current": 24.6,
    "net_margin_prior": 24.5,
    "roe_current": 168.7,
    "roa_current": 26.3,
    "ebitda_current": null,
    "ebitda_margin_current": null
  },
  "growth": {
    "revenue_growth_yoy_pct": 2.0,
    "net_income_growth_yoy_pct": 3.6,
    "eps_growth_yoy_pct": 4.9,
    "gross_profit_growth_yoy_pct": 2.1
  },
  "cash_flow": {
    "free_cash_flow": 108807,
    "fcf_margin_pct": 27.8,
    "fcf_conversion_pct": 113.3,
    "capex_intensity_pct": 2.4
  },
  "leverage": {
    "debt_equity_ratio": 1.78,
    "net_debt": -23726,
    "net_debt_ebitda": null,
    "interest_coverage_ratio": 40.4
  },
  "valuation": {
    "stock_price": null,
    "pe_ratio": null,
    "market_cap": null,
    "ev": null,
    "ev_ebitda": null,
    "note": "Market data not retrieved"
  },
  "trends": {
    "net_income": {
      "label": "↑ Increasing",
      "class": "positive",
      "analysis": "Net income rose 3.6% YoY driven by..."
    },
    "net_margin": {
      "label": "→ Stable",
      "class": "neutral",
      "analysis": "Net margin held steady at ~24.6%..."
    },
    "fcf": {
      "label": "↑ Increasing",
      "class": "positive",
      "analysis": "Free cash flow improved to $108.8B..."
    }
  },
  "geographic_revenue": {
    "analysis": "FY2025 net revenue: Americas $X.XB (~43%), Europe ~26%, Greater China ~18%; top region share stable YoY; geographic concentration moderate."
  },
  "unit": "millions USD",
  "notes": []
}
```
