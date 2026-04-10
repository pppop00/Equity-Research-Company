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

Rating text for `{{RATING_EN}}`: **Overweight**, **Neutral**, **Underweight** (or **Not applicable** for non-listed entities).

Confidence for `{{CONFIDENCE_EN}}`: **High**, **Medium**, **Low**.

---

## Date format

Use unambiguous English dates for `{{REPORT_DATE}}`, e.g. **April 8, 2026** (not slash-only numeric if avoidable).
