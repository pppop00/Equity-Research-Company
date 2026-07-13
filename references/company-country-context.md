# Company quality, country lens, and metric basis

## Product boundary

These artifacts support a company-to-country knowledge map. They describe mechanisms and evidence; they do not issue an investment recommendation, CFA lesson, composite company score, or national stereotype.

## P1 raw evidence — `company_context_research.json`

```json
{
  "schema_version": 1,
  "company": "Example",
  "as_of_date": "YYYY-MM-DD",
  "exposure_map": {
    "incorporation": {"value": "...", "source_refs": []},
    "listing": {"value": "...", "source_refs": []},
    "operations": {"value": "...", "source_refs": []},
    "revenue": {"value": "...", "source_refs": []}
  },
  "valuation_evidence": [],
  "governance_incentive_evidence": [],
  "capital_allocation_evidence": [],
  "accounting_quality_evidence": [],
  "country_evidence": {
    "tax": [], "fx_inflation": [], "regulation": [], "labor": [],
    "consumer_culture": [], "minority_shareholder_protection": []
  },
  "evidence_gaps": []
}
```

Every evidence item includes `fact`, `as_of_date`, `source_refs`, and the original metric/period/currency/unit where relevant.

## P2 `company_quality.json`

Root: `schema_version`, `company`, `as_of_date`, four observations, and `unknowns`.

The observations are `valuation`, `governance_incentives`, `capital_allocation`, `accounting_quality`. Each includes:

- `finding`
- `evidence`
- `watch_item`
- `status`: `supported | not_disclosed | not_comparable`
- `source_refs`
- optional `metrics[]` with `label`, `value`, `basis_id`, `as_of_date`

No aggregate score. Accounting quality must not be concluded from a single ratio without disclosure/audit/cash-flow context.

## P2 `country_lens.json`

Root includes the four-part `exposure_map`, fixed six `dimensions`, `top_warnings` (1–2), `company_to_country_insight`, and `unknowns`.

Each dimension uses:

```json
{
  "key": "tax",
  "country_fact": "...",
  "company_transmission": "...",
  "watch_metric": "...",
  "source_refs": [],
  "status": "supported | not_disclosed | not_comparable"
}
```

Fixed order: `tax`, `fx_inflation`, `regulation`, `labor`, `consumer_culture`, `minority_shareholder_protection`.

The insight must be bounded to the mechanisms evidenced by this company. Registration, listing, operations, and revenue location are not interchangeable.

## P2 `metric_basis.json`

Registry coverage is mandatory for:

`fcf`, `roe`, `capex`, `net_debt`, `fiscal_year`, `currency_unit`, `geographic_revenue`, `valuation`.

```json
{
  "schema_version": 1,
  "company": "Example",
  "as_of_date": "YYYY-MM-DD",
  "bases": [
    {
      "basis_id": "fcf_ocf_minus_capex",
      "metric_key": "fcf",
      "company_label": "Free cash flow",
      "company_definition": "...",
      "standardized_formula": "OCF - purchases_of_property_plant_equipment",
      "period": "FY2025",
      "currency": "USD",
      "unit": "millions",
      "source_refs": [],
      "comparability": "comparable | adjusted | not_comparable",
      "adjustment_note": "..."
    }
  ]
}
```

Every required metric key needs one registry entry. `not_comparable` is a valid honest result with a reason; a missing entry is not. Calculated card/report claims reference `basis_id`.

## Normalization rules

- Preserve original company definition and separately state standardized formula.
- Normalize currency and unit without hiding translation math.
- State fiscal calendar and period endpoints.
- Geographic revenue records the company's disclosed attribution basis (customer location, billing entity, destination, headquarters, etc.).
- Valuation records market-data time point, denominator period, share-count basis, and source.
- Do not label two companies comparable merely because their display labels match.
