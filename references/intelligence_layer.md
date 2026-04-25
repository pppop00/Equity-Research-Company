# Intelligence Layer Reference

This reference defines the lightweight report-facing intelligence layer used by Agent 3, Agent 4, Phase 2, Phase 2.5, and Phase 6 validation. Use it to turn scattered public information into executable investment intelligence.

## Purpose

Each intelligence signal must answer five questions:

1. What happened or what was disclosed?
2. Why does the raw fact matter economically?
3. Which investment variable or metric does it affect?
4. How does it support, weaken, or reframe the thesis?
5. What should be monitored next, and what would falsify the thesis?

Do not create generic signals such as "AI demand is strong" or "the company is a leader." A valid signal needs a traceable source, an economic mechanism, and a monitorable variable.

## Signal Types

Use exactly one of these values in `signal_type`:

| signal_type | Use when |
|-------------|----------|
| `filing_disclosure` | A filing footnote, accounting policy, segment recast, geographic basis, backlog/RPO, concentration, or KPI definition changes how a number should be read. |
| `industry_shift` | A measurable industry change affects demand, supply, pricing, capacity, or competitive structure. |
| `company_event` | A contract, product launch, acquisition, guidance change, capacity move, customer win/loss, restructuring, or litigation event changes company economics. |
| `policy_regulation` | Law, regulation, tariff, export control, subsidy, reimbursement, licensing, or enforcement action changes market access or economics. |
| `customer_supply_chain` | Customer identity, ODM/distributor behavior, procurement flow, inventory, bill-to/ship-to, or supply bottleneck changes interpretation of demand. |
| `pricing_margin` | Price, mix, utilization, input cost, discounting, rebates, or operating leverage affects revenue quality or margin direction. |
| `consensus_trap` | Public commentary or a headline metric is likely to be misread; the signal states the better read and evidence needed. |

## Canonical Shape

`news_intel.json -> intelligence_signals[]` uses this shape:

```json
{
  "id": "sig-001",
  "theme": "AI server demand geography",
  "signal_type": "customer_supply_chain",
  "fact": "Taiwan-headquartered customers represented a large reported revenue share, but a filing note attributes most related data-center demand to U.S. and European end customers.",
  "source": "Company Form 10-K, revenue note",
  "source_date": "2026-02-26",
  "affected_metric": "data-center revenue growth and geographic risk exposure",
  "direction": "positive|negative|mixed|neutral",
  "magnitude_hint": "High reported Taiwan share may overstate Taiwan end-demand exposure; no direct percentage-point revenue adjustment without additional source data.",
  "confidence": "high|medium|low",
  "watch_metric": "Hyperscaler capex, ODM inventory days, and geographic revenue note wording in the next 10-Q",
  "thesis_implication": "Demand should be tracked through end-customer deployment and cloud capex rather than customer-headquarters revenue alone."
}
```

## Field Rules

- `id`: Stable within the run; use `sig-001`, `sig-002`, etc.
- `theme`: Short human-readable theme, not a sentence.
- `fact`: Raw sourced fact. Do not include unsourced interpretation here.
- `source`: Original publisher or filing; do not cite only a script or intermediate JSON.
- `source_date`: ISO `YYYY-MM-DD` when available; otherwise use a clear period label and explain in `notes[]`.
- `affected_metric`: Revenue, margin, cash flow, market share, valuation driver, risk exposure, or Porter force affected by the signal.
- `direction`: `positive`, `negative`, `mixed`, or `neutral` from the investment thesis perspective.
- `magnitude_hint`: Quantified if defensible; otherwise state the qualitative magnitude and why it is not directly quantifiable.
- `confidence`: `high` only when source and mechanism are both strong; use `medium` or `low` for thin disclosure or indirect evidence.
- `watch_metric`: A concrete item a reader can monitor in future filings, earnings calls, macro series, industry trackers, or policy updates.
- `thesis_implication`: One concise sentence explaining how the signal supports, weakens, or reframes the investment case.

## Downstream Use

- Agent 4 selects the strongest edge insight from `intelligence_signals[]` or `financial_data.json -> disclosure_quirks[]`.
- Phase 2 uses selected signals to write `summary_para_2`, `summary_para_3`, trend cards, risk bullets, and `investment_thesis`.
- Phase 2.5 may link `prediction_waterfall.json -> company_events_detail[].source_signal_id` to a signal when a company event drives the revenue bridge.
- Phase 6 warns when the final report thesis, trend cards, risks, or edge insight are generic and cannot be traced to at least one signal, disclosure quirk, or cited source.
