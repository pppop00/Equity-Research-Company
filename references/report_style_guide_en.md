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
| ppt / bps | +X.X pp / X bps | +1.2 pp |
| P/E | XX.x× | 28.5× |
| EPS | $X.XX (diluted) | $6.43 |

Use commas for billions where helpful: **$2,817M** or **$2.8B** — pick one style per report and stay consistent.

---

## Terminology (UI labels)

Use standard U.S. / IFRS-friendly labels in KPIs and tables: **Revenue**, **Cost of revenue**, **Gross profit**, **R&D**, **Sales & marketing**, **G&A**, **Operating income**, **Net income**, **Free cash flow (FCF)**, **Net margin**, **Gross margin**, **Operating margin**, **ROE**, **ROA**, **D/E**, **Interest coverage**, **EPS**.

Sankey node labels (English): **Revenue**, **Cost of revenue**, **Gross profit**, **R&D expense**, **Sales & marketing**, **General & administrative**, **Operating income**, **Taxes & other**, **Net income** (adjust to match your line-item split).

Porter list labels (English): **Supplier power**, **Buyer power**, **Threat of new entrants**, **Threat of substitutes**, **Competitive rivalry**.

---

## Section II — Latest operating update (`{{LATEST_OPERATING_UPDATE_TEXT}}`)

**Fourth trend card** (between **Free cash flow trend** and **Geographic revenue mix**). Use the **latest filed 10-Q / interim / TTM** (or formal guidance), not a repeat of full-year FY YoY.

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
