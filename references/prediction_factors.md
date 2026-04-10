# Prediction Factors Reference

This file defines the macro factor model used in Phase 2.5 of the equity research skill. Update β values and φ over time as you calibrate against actual outcomes.

---

## Core Formula

```
Predicted_Revenue_Growth =
    Baseline_Growth
  + Σ (Factor_Change% × β_sector × φ)
  + Company_Specific_Adjustment
```

**Baseline_Growth:** Annualized growth rate from 10-Q YTD data (`YTD_revenue / quarters_reported × 4` vs prior year full-year), or analyst consensus from web search if no 10-Q available.

**Company_Specific_Adjustment:** Sum of `revenue_impact_pct` from all `company_events` in `news_intel.json`.

---

## φ — Friction Factor (Market Transmission)

```
φ = 0.5  (default)
```

The friction factor represents how much of a macro change actually transmits to company revenue. A value of 0.5 means 50% transmission — accounting for market frictions, hedging, contract lock-ins, and time lags.

| φ Value | Interpretation |
|---------|---------------|
| 0.1–0.2 | High friction: heavily hedged, long-term contracts, regulated industry |
| 0.3–0.5 | Moderate friction: typical corporate exposure ← **default** |
| 0.6–0.8 | Low friction: commodity-linked, unhedged, spot-market exposure |
| 0.9–1.0 | Direct pass-through: fully exposed, commodity producer or pure-play |

---

## β — Sector Sensitivity Coefficients

These are the default starting values. Adjust based on company-specific characteristics and validated predictions over time.

| Sector | Interest Rate β | GDP Growth β | PCE Inflation β | USD Index β | Oil Price β | Consumer Confidence β |
|--------|:--------------:|:------------:|:---------------:|:-----------:|:-----------:|:---------------------:|
| Technology | 0.3 | 1.2 | -0.2 | -0.4 | -0.1 | 0.5 |
| Real Estate / REITs | 1.8 | 0.8 | -0.3 | 0.1 | -0.1 | 0.2 |
| Financials / Banks | -0.8 | 1.0 | 0.2 | 0.2 | 0.0 | 0.6 |
| Healthcare | 0.1 | 0.5 | -0.1 | -0.2 | -0.1 | 0.1 |
| Consumer Discretionary | 0.5 | 1.5 | -0.5 | -0.3 | -0.2 | 1.2 |
| Consumer Staples | 0.05 | 0.3 | 0.3 | -0.3 | -0.1 | 0.2 |
| Energy | -0.2 | 0.8 | 0.1 | -0.5 | 1.5 | 0.0 |
| Industrials | 0.4 | 1.3 | -0.2 | -0.3 | -0.3 | 0.7 |
| Utilities | 1.2 | 0.3 | -0.1 | 0.0 | -0.2 | 0.0 |
| Communication Services | 0.2 | 1.0 | -0.1 | -0.2 | 0.0 | 0.8 |
| Materials | 0.3 | 1.2 | 0.3 | -0.5 | 0.4 | 0.3 |
| Semiconductors (sub-sector) | 0.4 | 1.5 | -0.2 | -0.3 | -0.1 | 0.6 |

**β sign interpretation:**
- Positive: this macro factor rising helps revenue
- Negative: this macro factor rising hurts revenue

**Interest Rate β note:** Measured as the impact of a **1 percentage-point decline** in the **dominant policy rate for the chosen geography** (not basis points). For **`US`**, use the Fed Funds effective / target band. For **`Greater_China`**, use **1-year LPR** or **MLF rate** as the policy-rate proxy (state which in `macro_factors.json` notes). For **`Eurozone`**, use ECB deposit facility rate. Same β column applies — you are measuring sensitivity to *local* monetary easing/tightening.

---

## Macro Factor Registry (US — default labels)

If `primary_operating_geography` = **`US`**, agents search for these **US** series:

| Factor slot | What to search for | Unit | Change direction |
|-------------|-------------------|------|-----------------|
| Policy rate | Fed Funds Rate | "federal funds rate current FOMC forecast year-end 2026" | % level | Lower rates = positive for most sectors |
| Real GDP | US real GDP | "US real GDP growth forecast 2026 IMF Fed" | % YoY | Higher = positive |
| CPI-type inflation | PCE | "PCE inflation rate 2026 Federal Reserve forecast" | % YoY | Higher = raises costs for most sectors |
| FX | USD broad strength | "DXY dollar index current 2026" | Index level | Higher USD = negative for US exporters |
| Oil | Global benchmark | "WTI crude oil price forecast 2026" | $/barrel | Sector-dependent |
| Consumer confidence | US household | "US consumer confidence index Conference Board 2026" | Index level | Higher = positive for consumer sectors |

---

## Primary operating geography — **same β slots, regional instruments**

The sector row in the β table always has **six macro slots** in fixed order: **Interest Rate | GDP | CPI-type inflation | FX | Oil | Consumer confidence**.  
**Do not** apply US data for a company whose revenue is **mainly outside the US** unless `primary_operating_geography` is `US`. Map each slot to the **local** series below; **keep the same β values** from the sector row for that slot index (column 1–6).

| Slot | `US` | `Greater_China` | `Eurozone` | `Japan` | `UK` |
|------|------|-----------------|------------|---------|------|
| Policy rate | Fed Funds / upper bound | 1-year **LPR** or **MLF** (state in notes) | ECB deposit rate | BOJ policy rate / YCC context | Bank Rate |
| Real GDP | US real GDP YoY | **China** real GDP YoY | Euro area real GDP YoY | Japan real GDP YoY | UK real GDP YoY |
| Inflation | PCE YoY | **China CPI** YoY | Euro area **HICP** YoY | Japan CPI YoY | UK CPI YoY |
| FX | **DXY** (or specify) | **CFETS RMB index** and/or **USD/CNY** (explain sign: CNY vs USD move vs margins) | **EUR/USD** or nominal effective EUR | **USD/JPY** | **GBP/USD** or trade-weighted GBP |
| Oil | WTI / Brent | **Brent or WTI** (global; keep one benchmark for comparability) | same | same | same |
| Confidence | **Conference Board** or Michigan | **国家统计局消费者信心指数** or major third-party China consumer index (name the series) | EC consumer confidence / Eurozone | Cabinet Office / confidence | GfK or ONS-related |

**`Emerging_Asia_ex_China`:** Use the **single largest country market** within that bucket for GDP/CPI/confidence if one dominates; otherwise use `Global_other` and document a **composite / regional** choice in `notes`.

**`Global_other` / multi-hub:** Prefer the geography with **>50% revenue**; if none, pick the **headline investment driver** region and state the limitation in `notes`.

**Report language:** `macro_factors.json` → `factors[].name` must read naturally in the report — **Chinese** labels for `zh` (e.g. `中国消费者信心指数`), **English** for `en` (e.g. `China consumer confidence (NBS)`).

---

## Macro Factor Registry (legacy one-line reference)

Agents should search for current values using the **regional mapping** above. The US-only table in older runs maps to `primary_operating_geography = US`.

**Factor_Change% calculation:**
- For rate/index levels: `(Forecast - Current) / |Current| × 100`
- Example: Fed Funds goes from 3.625% to 3.375% → Change% = (3.375 - 3.625) / 3.625 × 100 = -6.9%

---

## Calibration Log

Record prediction outcomes here over time to improve the model:

| Date | Company | Predicted Growth | Actual Growth | Error | Action |
|------|---------|-----------------|---------------|-------|--------|
| — | — | — | — | — | Update φ or β if systematic bias detected |

**Calibration rules:**
- If systematic over-prediction: lower φ by 0.05
- If systematic under-prediction: raise φ by 0.05
- If sector-specific bias: adjust that sector's β values
- Aim to validate predictions 6-12 months after report generation

---

## Worked Example

**Company:** Prologis (PLD) — Logistics REIT | **Sector:** Real Estate / REITs | **φ = 0.5**

| Factor | Current | Forecast | Change% | β | φ | Adjustment% |
|--------|---------|----------|---------|---|---|------------|
| Fed Funds Rate | 3.625% | 3.375% | -6.9% | 1.8 | 0.5 | +6.2% |
| GDP Growth | 2.4% | 2.4% | 0.0% | 0.8 | 0.5 | +0.0% |
| PCE Inflation | 2.7% | 2.7% | 0.0% | -0.3 | 0.5 | +0.0% |
| USD Index | 102 | 99 | -2.9% | 0.1 | 0.5 | -0.1% |
| Oil Price | $78 | $72 | -7.7% | -0.1 | 0.5 | +0.4% |

Total macro adjustment: **+6.5%**
Baseline (10-Q annualized): **+4.2%**
Company-specific (new Amazon contract): **+1.5%**
**Predicted Revenue Growth: +12.2%**
