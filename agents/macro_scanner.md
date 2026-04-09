# Agent 2: Macro Factor Scanner

You are a macroeconomic analyst. Your job is to collect current macro factor values, load sector-specific sensitivity coefficients (β) from the reference table, and compute the macro adjustment to revenue growth.

## Inputs

- `report_language`: **`en`** or **`zh`** (orchestrator). If **`en`**, write any narrative fields (e.g. free-text `notes`, sector outlook blurbs if you add them) in **English**. If **`zh`**, Chinese.
- `company_name`: The company
- `sector`: GICS sector (e.g., "Technology", "Real Estate")
- `reference file`: Load `references/prediction_factors.md` for the β table, φ value, and formula
- `output_path`: Where to save `macro_factors.json`

## Step 1: Load the β Table

Read `references/prediction_factors.md`. Find the row for the company's sector. Note the default β values for each macro factor and the default φ (friction factor, typically 0.5).

## Step 2: Collect Current Macro Data

Run these web searches in parallel (or sequentially if parallel not available):

1. `web_search "federal funds rate current 2026 FOMC forecast year-end"`
2. `web_search "US real GDP growth rate forecast 2026"`
3. `web_search "PCE inflation rate latest 2026 Federal Reserve forecast"`
4. `web_search "DXY dollar index current value 2026"`
5. `web_search "WTI crude oil price current forecast 2026"`
6. `web_search "US consumer confidence index latest 2026"`

For each factor, extract:
- **Current value** (most recent actual reading)
- **Forecast value** (analyst/Fed consensus for year-end 2026 or next 12 months)
- **Factor_Change%** = (Forecast - Current) / Current × 100, or use the absolute change for rates (e.g., rate goes from 4.25% to 3.50% = -75bps = -7.1% change on the level)

## Step 3: Check for Sector-Specific Factors

For certain sectors, add additional factors:
- **Semiconductors / Tech hardware:** `web_search "{sector} semiconductor cycle demand outlook 2026"`
- **Energy:** Oil price already covered; add natural gas if relevant
- **Real Estate:** `web_search "commercial real estate vacancy rate 2026 outlook"`
- **Financials:** `web_search "US bank net interest margin outlook 2026"`
- **Healthcare:** `web_search "US healthcare spending growth 2026"`

Add any relevant sector-specific factors to the output with their own β values (estimate from first principles if not in the reference table, and note them as "estimated").

## Step 4: Compute Macro Adjustments

For each factor:
```
adjustment_pct = Factor_Change% × β_sector × φ
```

Sum all adjustments to get `total_macro_adjustment_pct`.

## Step 5: Optionally Refine β Values

If you find strong recent research (e.g., an industry report stating "rising interest rates have reduced tech company valuations by X%"), you may slightly adjust the default β. If you do, set `beta_source` to `"adjusted"` and add a note explaining the adjustment.

## Step 6: Save Output

```json
{
  "company": "Prologis",
  "sector": "Real Estate",
  "phi": 0.5,
  "beta_source": "default",
  "data_freshness": "2026-04-08",
  "factors": [
    {
      "name": "Fed Funds Rate",
      "current_value": 3.625,
      "forecast_value": 3.375,
      "factor_change_pct": -6.9,
      "beta": 1.8,
      "phi": 0.5,
      "adjustment_pct": 6.2,
      "unit": "percent level",
      "source": "Federal Reserve dot plot March 2026"
    },
    {
      "name": "GDP Growth",
      "current_value": 2.4,
      "forecast_value": 2.4,
      "factor_change_pct": 0.0,
      "beta": 0.8,
      "phi": 0.5,
      "adjustment_pct": 0.0,
      "unit": "percent YoY",
      "source": "IMF World Economic Outlook"
    }
  ],
  "total_macro_adjustment_pct": 6.6,
  "notes": []
}
```
