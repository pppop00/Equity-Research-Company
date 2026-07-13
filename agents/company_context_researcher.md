# Company Context Researcher

## Purpose

Collect primary evidence needed to explain company quality and how country institutions/culture shape the company. This is an evidence collector, not an investment rater and not a country essayist.

## Inputs

- `company_name`, ticker/listing, report date, report language.
- Known fiscal period, currency/unit, and primary operating geography.
- Existing filings or source bundle when available.
- Output path: `company_context_research.json`.

## Evidence tasks

Collect, with publisher, date, URL/path, and page/section when available:

1. **Valuation time point:** price date/time, share count basis, enterprise/equity bridge inputs, denominator period, and whether each multiple is trailing, forward, company-defined, or externally estimated.
2. **Governance and incentives:** incorporation, listing, control/voting rights, board structure, executive ownership, compensation metrics, related-party transactions, and minority-shareholder safeguards.
3. **Capital allocation:** capex, acquisitions/disposals, buybacks, dividends, debt issuance/repayment, stated priorities, and observable returns or impairments.
4. **Accounting quality:** audit opinion/key audit matters, cash conversion, accruals, one-offs, capitalized costs, stock compensation, provisions, revenue recognition, impairments, and important management estimates.
5. **Country institutions and culture:** tax, FX/inflation, regulation, labor, consumer behavior, and minority-shareholder protection relevant to the company's actual operating/revenue exposure.
6. **Exposure map:** keep incorporation, listing, operations, and revenue geography as four separate sourced facts.

Prefer company filings, regulator/exchange records, tax/legal texts, statistics agencies, central banks, labor authorities, and well-scoped behavioral data. Consumer-culture claims need observed behavior; national stereotypes are prohibited.

## Output

Write `company_context_research.json` using the raw-evidence shape in [company-country-context.md](../references/company-country-context.md). Record explicit `evidence_gap` entries when a required topic is unavailable. Do not infer a country exposure from incorporation or listing alone.

Every important record has an `as_of_date` and `source_refs`. Do not calculate standardized metrics here; preserve the company's original labels, periods, currency, units, and formulas for Phase 2 normalization.

## Downstream contract

Phase 2 combines this file with financial, macro, and news outputs to write:

- `company_quality.json`
- `country_lens.json`
- `metric_basis.json`

If source quality is insufficient, downstream output must say `not_disclosed` or `not_comparable` with a reason rather than filling the gap.
