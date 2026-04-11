# English equity research report style guide

For **Agent 4A** (`agents/report_writer_en.md`). Tone: institutional sell-side / buy-side research (concise, third person, no hype).

---

## Voice and tone

**Do:**
- Lead with the conclusion, then support with numbers
- Use precise figures; avoid vague intensifiers (“significant”, “strong”) without data
- Prefer active voice sparingly; neutral institutional register

**Avoid:**
- **Markdown in HTML placeholders** — the final report is static HTML; `**bold**` and `` `code` `` are not rendered and will show as raw characters. Use plain prose in all narrative fields pasted into `{{…}}` slots; use `<strong>…</strong>` only sparingly if emphasis is truly needed.
- Casual language, fluff, exclamation marks
- Unsubstantiated superlatives (“industry-leading”) unless cited
- Machine translation from Chinese — write natively in English

---

## Number and unit conventions

| Type | Format | Example |
|------|--------|---------|
| Large USD revenue | $XX.XB / $XXXM | $391.0B, $840M |
| Percent | XX.X% | 24.6% |
| YoY change | +X.X% YoY | +7.2% YoY |
| Negative KPI headline (`{{KPI*_VALUE}}`) | Leading minus on the number | **-22.3%**, **-$164M**, **~-$120M** — do **not** spell out “negative” or “approx. negative” in place of the minus sign |
| ppt / bps | +X.X pp / X bps | +1.2 pp |
| P/E | XX.x× | 28.5× |
| EPS | $X.XX (diluted) | $6.43 |

Use commas for billions where helpful: **$2,817M** or **$2.8B** — pick one style per report and stay consistent.

---

## Terminology (UI labels)

Use standard U.S. / IFRS-friendly labels in KPIs and tables: **Revenue**, **Cost of revenue**, **Gross profit**, **R&D**, **Sales & marketing**, **G&A**, **Operating income**, **Net income**, **Free cash flow (FCF)**, **Net margin**, **Gross margin**, **Operating margin**, **ROE**, **ROA**, **D/E**, **Interest coverage**, **EPS`.

**KPI row 3 (FCF) — `{{KPI3_DIRECTION}}` / `{{KPI3_CHANGE}}`:** If **FCF is negative in both** the current and prior fiscal year **but** the current period is **less negative** (cash burn narrowed), do **not** use `up` (green) with vague “significant improvement.” Use **`neutral-kpi`** on both the card and `.kpi-change`, and write **`{{KPI3_CHANGE}}`** with a **quantified** YoY change (e.g. narrower loss in **$M** or **$B**) plus **“still negative”**. Reserve `up` for **positive** FCF that exceeds the prior year. **`neutral-kpi`** uses the **same red KPI card chrome** as `down` (only the **semantic** rule differs: never green while FCF is still negative); `.kpi-change` for `neutral-kpi` uses neutral body color so the sub-line does not read like “deterioration” when the story is burn narrowing.

Sankey node labels (English): **Revenue**, **Cost of revenue**, **Gross profit**, **R&D expense**, **Sales & marketing**, **General & administrative**, **Operating income**, **Taxes & other**, **Net income** (adjust to match your line-item split).

Porter list labels (English): **Supplier power**, **Buyer power**, **Threat of new entrants**, **Threat of substitutes**, **Competitive rivalry**.

---

## Section I — Investment summary (fourth paragraph, `{{SUMMARY_PARA_4}}`)

**Paragraph 4 (~55–90 words):** Industry **niche / sub-industry scope**, **market share** with a **multi-year series when credible** (state the **metric scope** and **source** — IDC/Gartner/Omdia/company-cited trackers, etc.; if unavailable, say so and use segment revenue or qualitative position). **Main operating footprint** (HQ, manufacturing, R&D hubs) vs **largest revenue geographies** — **must align** with **`financial_data.json`** geographic disclosure when present; reconcile with **`news_intel.json` → `industry_position`**. **Reputation / market recognition** (awards, marquee customers) only with sources. Plain text in the placeholder; no Markdown. Phase 2 writes the final prose to **`financial_analysis.json` → `summary_para_4`**.

---

## Section II — Latest operating update (`{{LATEST_OPERATING_UPDATE_TEXT}}`)

**Fourth trend card** (between **Free cash flow trend** and **Geographic revenue mix**). Use the **latest filed 10-Q / interim / TTM** (or formal guidance), not a repeat of full-year FY YoY.

**Metrics table final column (`YoY movement`):** This is a qualitative verdict column, not a numeric delta column. Do not put raw cells like `+0.62%`, `-1.4pct`, or `+0.00%` in the final column. Use the controlled labels from `references/financial_metrics.md`: `Significantly improved`, `Improved`, `Stable`, `Deteriorated`, `Significantly deteriorated`, `Equity deficit narrowed`, `Equity deficit widened`, `Ending equity negative`, or `N/A`. Put precise deltas in the value columns, trend card prose, or notes.

- **Data ownership:** Agent 1 (`agents/financial_data_collector.md`) **must** fetch the latest qualifying filing and populate **`financial_data.json` → `latest_interim`**. Downstream steps **do not fabricate** quarterly figures when that object is absent.
- **YoY vs QoQ:** **Default to YoY** — latest fiscal quarter **vs. the same quarter last year**, or **YTD vs. prior-year YTD** (aligned to the issuer’s fiscal calendar). **Add QoQ vs. the immediately prior quarter** only as a **secondary** clause when sequential inflection matters; label it **sequential** and do not let QoQ **replace** YoY as the headline growth stat unless the narrative is explicitly quarter-on-quarter.
- **Lead with the period** (e.g., “Per Form 10-Q for the quarter ended …”, “YTD through Q2 FY20XX”). Readers must not confuse this block with the **full-fiscal-year** narratives in the cards above.
- Focus on **marginal** changes: revenue momentum, gross margin, cash conversion, one-offs, management outlook.
- If no reliable interim filing exists, say so briefly.

---

## Porter Five Forces

**Applies to company-level, industry-level, and forward-looking tabs.**

- **~300 words per perspective**, all five forces covered.
- **HTML shape (Phase 5 — required, all three tabs):** Fill `{{PORTER_COMPANY_TEXT}}`, `{{PORTER_INDUSTRY_TEXT}}`, and `{{PORTER_FORWARD_TEXT}}` each as **one unordered list**: `<ul style="margin:0;padding-left:1.25em;">` containing **exactly five `<li>` items**, in this fixed order: **Supplier power → Buyer power → Threat of new entrants → Threat of substitutes → Competitive rivalry** (same order as the radar axes and the score list). No Markdown in values.
- **Do not repeat scores in list items** — do **not** open a bullet with "Supplier power is strong (4/5)" or similar; the numeric score and force label already appear in the radar and the right-hand score list. Each `<li>` is **analysis only** (may use multiple sentences).
- **Source text:** `porter_analysis.json` fields under `company_perspective`, `industry_perspective`, and `forward_perspective` should store **substantive lines without score-prefixed openings**, so they map cleanly into the five `<li>` elements.
- **Name names:** Whenever you refer to **incumbents**, **leading players**, **the oligopoly**, or **existing giants**—including in *Threat of new entrants* when the real story is process-node races and capacity expansion among established firms—**list the top 3–5 relevant firms** in the same sentence or the next. Phrases like "existing giants" with no names are **not** acceptable. If the peer set truly cannot be identified from public sources, say that in one short clause instead of using empty collectives.
- **Industry vs company tab:** The industry tab describes **sector structure**; it still names the main global (or report-relevant) players. The company tab adds **issuer-specific** facts (joint ventures, customer mix, share vs named peers). Industry tab does **not** mean "stay abstract."

---

Rating text for `{{RATING_EN}}`: **Overweight**, **Neutral**, **Underweight** (or **Not applicable** for non-listed entities).

Confidence for `{{CONFIDENCE_EN}}`: **High**, **Medium**, **Low**.

---

## Date format

Use unambiguous English dates for `{{REPORT_DATE}}`, e.g. **April 8, 2026** (not slash-only numeric if avoidable).

---

## Appendix and header: **Specific source** column (required)

Readers care about the **original publisher** of the information, not intermediate repo filenames. In **`{{APPENDIX_SOURCE_ROWS}}`** and the header **`{{DATA_SOURCE}}`**, use the **authoritative origin**.

| How the data was obtained | Suggested **Specific source** text | Avoid |
|-----------------------------|-----------------------------------|--------|
| `scripts/sec_edgar_fetch.py` → `sec_edgar_bundle.json` ( `data.sec.gov` / EDGAR APIs ) | **U.S. SEC EDGAR** (optional parenthetical: `data.sec.gov`, fetched via this skill’s script) | Listing only the script or `sec_edgar_bundle.json` as if it were separate from SEC |
| Reading **Form 10-K / 10-Q** on **sec.gov** Archives (**MD&A**, **Note 16 Revenue**, etc.) | **U.S. SEC EDGAR** (parenthetical: Form 10-K MD&A, Note 16 Revenue) | Implying MD&A/notes are a non-SEC “third source”; they are **part of the SEC filing** |
| Company **IR** press release / PDF (not hosted on sec.gov) | **Company IR** (domain if helpful) | SEC |
| **Bloomberg** / **Reuters** / other press | **Bloomberg**, **Reuters**, etc. | SEC |
| Secondary aggregators (Yahoo Finance, etc.) | Name the aggregator; **Medium** confidence is usually appropriate | SEC |

**Rule of thumb:** If the line item ultimately ties to the **EDGAR-filed statutory disclosure**, label the source **SEC** (optionally name the form and section). Use **Bloomberg**, **Reuters**, **Company IR**, etc. **only** when that channel is where the figure or narrative first appears.

For `{{DATA_SOURCE}}`, use a short parallel summary, e.g. `Primary financials: U.S. SEC EDGAR; Macro: …`.
