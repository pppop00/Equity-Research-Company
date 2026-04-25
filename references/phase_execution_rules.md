# Phase Execution Rules (Detailed)

This file stores detailed execution constraints that were intentionally moved out of `SKILL.md`.
`SKILL.md` stays as the orchestration contract (inputs, outputs, agent call, gate), while this file carries cross-cutting rules and orchestrator-inline phase details.

Agent-specific rules live in `agents/*.md` — each agent file now includes a "Downstream Contract" section covering its output obligations and how downstream phases consume it.

---

## Phase 1: Orchestration Details

- Start Agent 1, Agent 2, and Agent 3 in parallel when possible.
- Agent prompts must always include `Report language: {en|zh}`.
- Agent 4 may start after Agent 1 and Agent 3 finish; Agent 2 may still be running.
- Do not leave Phase 1 until all of `financial_data.json`, `macro_factors.json`, and `news_intel.json` exist.
- **Post-collection reconciliation (orchestrator duty):** After `financial_data.json` and `news_intel.json` exist, re-check `macro_factors.json -> macro_regime_context` against filing geography and industry news. If materially inconsistent, revise context/commentary or rerun Agent 2.

---

## Phase 2: Financial Analysis (Orchestrator Inline)

Phase 2 is executed by the orchestrator, not a subagent, so its detailed rules stay here.

### Fiscal-Year Alignment

- Year labels in Section II and KPI cards must align with `financial_data.json`:
  - `income_statement.current_year`
  - `income_statement.prior_year`
- YoY always means these two consecutive full fiscal years.
- If latest year has only interim data, either:
  - keep full-year comparison and include lag explanation in `notes[]`, or
  - add a clearly labeled interim-vs-prior-interim block.

### Table and Card Contracts

- Section II metrics table final column (`同比变动` / `YoY movement`) must be qualitative verdict text, not raw numeric delta. Use controlled vocabulary from `references/financial_metrics.md`.
- Latest operating update must:
  - use `latest_interim` from Agent 1 as primary structured source,
  - lead with covered period,
  - prefer YoY headline unless filing context explicitly centers QoQ.
- Geographic revenue card must be factual and filing-grounded; avoid meta/disclaimer filler text.
- KPI third card (FCF): if both years negative but narrowing toward zero, use `neutral-kpi` class, not `up`. See `references/financial_metrics.md` and `references/report_style_guide_cn.md`.
- Trend cards should behave like monitorable intelligence cards, not generic business commentary. When `news_intel.json -> intelligence_signals[]` or `edge_insights.json` provides a relevant `watch_metric`, at least one trend card should name the metric to monitor and the direction that would support or weaken the thesis.

### Narrative Evidence and Language

- Load `references/intelligence_layer.md` before writing the report-bound narrative.
- Valuation statements require evidence from `financial_analysis.json -> valuation` or explicitly cited appendix data.
- Do not present live-market conclusions as facts when source fields are null.
- `investment_thesis` must be an executable thesis: include the core driver, the affected investment variable, and the main monitor or falsification trigger. Do not write only a company description or generic bullish/bearish sentence.
- Risk bullets should be tied to evidence, a signal, or a monitorable variable where possible; avoid unsupported boilerplate risks.
- All HTML-bound narrative strings must be plain text (no Markdown symbols).
- Language lock:
  - `report_language = en` -> English narrative fields
  - `report_language = zh` -> Chinese narrative fields

### Investment Summary Structure

- `summary_para_1`: business + latest financial performance (zh: 160-200 chars; en: 90-130 words).
- `summary_para_2`: edge insight interpretation and implication from `edge_insights.json -> summary_para_2_draft`; it should map to either `edge_insights.json -> chosen_signal_ids[]` or a cited `financial_data.json -> disclosure_quirks[]` item.
- `summary_para_3`: thesis/catalysts with constraints plus a concrete monitor or falsification trigger from `edge_insights.json -> monitor_metric` / `falsification_trigger` or `news_intel.json -> intelligence_signals[]`.
- `summary_para_4`: industry position reconciled with filings and geography from `news_intel.json -> industry_position`.

---

## Phase 2.5: Revenue Prediction (Orchestrator Inline)

### Model and Label Consistency

- Use formula and factor framework from `references/prediction_factors.md`.
- Keep macro factor names and ordering consistent with `macro_factors.json` and chosen geography.
- `predicted_fiscal_year_label` should default to `FY(latest_actual + 1)E` and match Sankey forecast label.

### Source-of-Truth Split

- `news_intel.json` = raw event layer (`company_events[].revenue_impact_pct`).
- `news_intel.json -> intelligence_signals[]` = report-facing signal layer (source facts, affected metric, thesis implication, watch metric).
- `prediction_waterfall.json` = final model layer (`company_specific_adjustment_pct` and final bridge).
- Do not maintain competing root-level company-adjustment totals across files.

### Event Normalization

If `company_events_detail[]` is present, prefer:

`final_impact_pct = raw_impact_pct * timing_weight * (1 - overlap_ratio) * run_rate_weight * probability_weight * realization_weight`

and keep `company_specific_adjustment_pct` approximately equal to the sum of event-level `final_impact_pct`.

If an event is derived from `news_intel.json -> intelligence_signals[]`, carry its ID into the event object as optional `source_signal_id`. This keeps the forecast bridge traceable from raw event and signal to final model adjustment.

### Section III Table Contract

- Factor table final column is direction text:
  - `zh`: `正向` / `负向` / `中性`
  - `en`: `Positive` / `Negative` / `Neutral`
- Do not repeat numeric percentage values in the direction column.
- Factor table percent-display columns (`宏观变化（%）` / `Macro change (%)` and `调整幅度（%）` / `Adjustment (%)`) have units in the header, so cells must not repeat `%`; nonzero values must include `+` or `-`; zero is exactly `0`; decimals are capped at two places. Examples: `-4.2`, `+8.00`, `-3.1`, `+0.15`, `-0.80`, `0`; invalid: `+8%`, `-4.1667`, `+0.14685`.
- Use existing positive/negative CSS classes only where required by locked template conventions.

### Interim-to-Model Bridge

- Material interim/TTM evidence may adjust company-specific impacts.
- When adjusted value diverges from simple event net sum, explain via assumptions/notes/qc deliberation fields.
- Keep Section III waterfall and Section IV forecast assumptions aligned.

---

## Phase 2.6 / 3.5 / 3.6: QC Phases

Detailed rules for each QC agent live in their respective agent files:
- `agents/qc_macro_peer_a.md` (includes Downstream Contract)
- `agents/qc_macro_peer_b.md` (includes Downstream Contract)
- `agents/qc_porter_peer_a.md` (includes Downstream Contract)
- `agents/qc_porter_peer_b.md` (includes Downstream Contract)
- `agents/qc_resolution_merge.md` (includes Execution Policy: full-run/fast-run, conflict priority)

---

## Phase 4: Sankey Build (Orchestrator Inline)

- Build actual tab from `financial_data.json` current-year P&L basis.
- Build forecast tab from same structure scaled by Phase 2.5 predicted growth and forecast fiscal label.
- Keep Sankey year labels consistent with prediction horizon.
- Node labels must match `report_language` (English names for `en`, Chinese for `zh`).

---

## Phase 5: Report Generation

### Locked Template and Extraction

- Always extract locked skeleton with `scripts/extract_report_template.py` before placeholder filling.
- Only replace `{{PLACEHOLDER}}` values; do not edit HTML/CSS/JS structure.

### Waterfall Data Contract (P0)

- Section III waterfall values are percentage points, not decimals and not currency amounts.
- Build from growth bridge fields (baseline/macro/company/result), not revenue totals.
- Result bar must reconcile with `predicted_revenue_growth_pct` within rounding tolerance.
- Putting `base_revenue` into waterfall produces nonsense like "37296.0%" — that is a unit error.

### Language Branching

- `zh` branch uses `agents/report_writer_cn.md` + `references/report_style_guide_cn.md`.
- `en` branch uses `agents/report_writer_en.md` + `references/report_style_guide_en.md`.

- Porter scores are threat / pressure scores: `1-2` = low threat / green, `3` = mixed / amber, `4-5` = high threat / red. Do not invert this into an attractiveness score; intense competitive rivalry must be high/red.
- Detailed placeholder rules, Porter comment handling, and post-processing cautions live in the respective `agents/report_writer_*.md` files.

---

## Phase 5.2: Card Logo Production (Optional Branch)

Apply this branch only when the run includes card deliverables (`*.card_slots.json`, `01_cover.png`, etc.).

- **Order is mandatory:** run `agents/logo_production_agent.md` **before** any Card1 rendering.
- **Hard requirement:** exported logo resolution must be at least **2x** of Card1 render slot in both dimensions.
- **Card metadata contract (`*.card_slots.json`):**
  - `logo_render_width_px`
  - `logo_render_height_px`
  - `logo_export_width_px`
  - `logo_export_height_px`
  - `logo_scale_factor` (must be `>=2`, default target `2`)
- **Fallback slot:** if render slot is missing, use `276x328`, thus export must be `>=552x656`.
- **Quality rule:** do not pass low-resolution bitmaps through naive upscale; prefer official high-res/vec sources and high-quality antialias resampling.

---

## Phase 5.5 / Phase 6: Validation

- Phase 5.5 (`agents/final_report_data_validator.md`): data/professional validation — recompute formulas, reconcile quantities, fix upstream JSON first.
- Phase 6 (`agents/report_validator.md`): delivery/structure validation — resolve CRITICAL plus designated pre-delivery WARNING blockers.
- Both agent files contain their own detailed checklists and blocker policies.
