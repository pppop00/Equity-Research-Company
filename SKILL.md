---
name: equity-research
description: >
  Full-stack equity research report generator. Trigger when the user wants to analyze a company, generate an equity research report, fundamental analysis, or stock investment research. Works with a company name (web search) or uploaded filings (10-K / 10-Q PDFs, HK/A-share reports). After the user chooses report language (English or Chinese), outputs one professional interactive HTML report (Sankey revenue flow, macro waterfall, Porter Five Forces).

  TRIGGER on: "equity research", "research report", "analyze [company]", "financial analysis of [company]", "做研报", "研究报告", "分析[公司]", English/Chinese equivalents, or user uploads a 10-K/10-Q and wants full research (not only a revenue-flow diagram).
---

# Equity Research Skill

Generate a professional equity research report for any public company. You are the orchestrator — you coordinate data collection, analysis, and report writing, either via parallel subagents (Claude Code) or sequentially (Claude.ai).

---

## Step 0A: Report language — **mandatory gate (before any Phase 1 work)**

**Do not start Phase 1** (no agents, no `workspace/` writes, no JSON generation) until `report_language` is resolved to exactly one of: **`en`** | **`zh`**.

### When language is already explicit

Treat any of the following as explicit (map and proceed **without** asking):

| Maps to `report_language = en` | Maps to `report_language = zh` |
|--------------------------------|----------------------------------|
| `English`, `EN`, `英文`, `英语`, `in English`, `English report`, `英文研报`, `generate English` | `Chinese`, `ZH`, `中文`, `简体`, `Chinese report`, `中文研报`, `生成中文` |

If the user states both or contradictory cues, ask one short clarification before Phase 1.

### When language is **not** explicit

Reply **only** with this prompt and **stop** until the user answers:

> **What language should the final HTML report use — English or Chinese (中文)?**  
> Reply with **English** or **Chinese**.

After the user answers, map **English** → `en`, **Chinese** / **中文** → `zh`. If the reply is ambiguous, ask again (still **do not** run Phase 1).

### Persist for the whole run

- Store `report_language` for all subsequent phases.
- Every agent task prompt (Phase 1+) **must** include:  
  `Report language: en` **or** `Report language: zh`  
  When `en`: **all narrative text in intermediate JSON and the final HTML must be English** (numbers and tickers as usual).  
  When `zh`: use Chinese for narrative as today; final HTML from `report_writer_cn.md`.

---

## Step 0B: Parse input & setup workspace

**Input mode:**

- **Mode A** — Company name only → Web Search mode  
- **Mode B** — Company name + 10-K PDF → File-based mode  
- **Mode C** — Company name + 10-K + 10-Q PDF → Full File mode  

**Only after Step 0A is satisfied**, create:

```
workspace/{Company}_{Date}/
```

All intermediate JSON files and the final HTML go here. Treat this path as **relative to the root of this skill pack** (the directory that contains `SKILL.md` and the `workspace/` folder). **Do not** create the workspace inside `~/.claude/` or other unrelated trees.

**Detect environment:**

- Claude Code: parallel subagents as below  
- Claude.ai: same phases sequentially  

---

## Step 0C: Report calendar anchor & latest annual (mandatory)

Use this on **every** run so Section II, Section IV (Sankey), and Phase 2.5 use the **same** fiscal baseline — not an arbitrary lag.

1. **`report_calendar_year` (`Y_cal`)**  
   Derive from the **`{Date}`** in `workspace/{Company}_{Date}/` (use the **four-digit calendar year** of that date, e.g. `Envicool_2026-04-10` → **2026**), unless the user gives an explicit **报告日 / as-of date** — then use that date’s year. This is the skill’s default “today” for **filing availability**.

2. **What “latest annual” must be (Agent 1)**  
   - **US 10-K / many HK & A-share 年报:** As of `Y_cal`, the orchestrator and Agent 1 **must first verify** whether the **complete annual** for fiscal **`FY(Y_cal − 1)`** is already **published** (e.g. in **2026** Q1–Q2, prioritize **FY2025** vs **FY2024** for YoY, not FY2024 vs FY2023).  
   - **Non–December fiscal year ends:** The fiscal **label** comes from the filing (e.g. FY ending Mar 2025). `Y_cal − 1` is only a **default search hint** for December FY names; do **not** force the wrong FY — read the report header.

3. **`financial_data.json` pair (Section II)**  
   - **`income_statement.current_year`** = the **latest complete fiscal year** in the filing set (normally **`FY(Y_cal − 1)`** once that annual is out).  
   - **`prior_year`** = the **immediately preceding** full fiscal year.  
   - **If `FY(Y_cal − 1)` annual is not yet published** on the report date, use the **latest two consecutive full fiscal years that *are* published** (e.g. FY2024 vs FY2023) and add a **`notes[]`** line stating that **`FY(Y_cal − 1)` was unavailable** so readers know why the table lags.

4. **Section IV — Sankey (two tabs)**  
   - **Actual tab (`{{SANKEY_YEAR_ACTUAL}}`, `sankeyActualData`):** Built from the **same** P&L basis as **`current_year`** in `financial_data.json` (the latest **full-year** actual in the file). **Do not** label or scale “actual” two years behind `Y_cal` without the note in §3.  
   - **Forecast tab (`{{SANKEY_YEAR_FORECAST}}`, `sankeyForecastData`):** **P&L structure scaled** to the **next fiscal year** after `current_year` using the model’s predicted revenue growth — label **`FY{current_FY + 1}E`** (e.g. actual FY2025 → **FY2026E**). This is the default “次财年 / 相对最新年报的下一完整财年” forecast, not a jump to **FY2027E** unless the model and narrative **explicitly** target that later year and the HTML label matches `prediction_waterfall.json`.

5. **Phase 2.5 — `prediction_waterfall.json`**  
   - **`predicted_fiscal_year_label`** **must match** the Sankey **forecast** tab (default **`FY(latest_actual + 1)E`**). The waterfall “预测财年” line should use the **same** label.

Pass **`Report calendar year: {Y_cal}`** (and **`Report date: {YYYY-MM-DD}`** if known) into **every** Agent 1 task prompt so searches target the correct 10-K / 年报.

---

## Step 0D: Primary operating geography — **for macro factor model (mandatory before Agent 2)**

The Phase 2.5 macro table and Section III must use **macro indicators from the region where the company earns most of its revenue** (or the region that drives the investment thesis), not a blind default to US series.

1. **Set `primary_operating_geography`** to one of: **`US`** | **`Greater_China`** | **`Eurozone`** | **`Japan`** | **`UK`** | **`Emerging_Asia_ex_China`** | **`Global_other`** (use only when revenue is genuinely split; see `references/prediction_factors.md`).

2. **How to decide (in order):**  
   - User explicitly states the main market (e.g. “主业在中国”).  
   - **Uploaded filings:** take the **largest** revenue share from geographic / segment disclosure (MD&A).  
   - Else **one quick web search** (or listing context): e.g. HKEX / 沪深 main listing + “revenue by region” / “largest market”.  
   - If still unclear: default **`US`** for a **US-incorporated, US-market-centric** name; for **known China/HK-heavy** names (e.g. major HK-listed CN internet), prefer **`Greater_China`**.

3. **Pass into Agent 2** every time:  
   `Primary operating geography: {value}`  
   Agent 2 loads **the same β row** from `references/prediction_factors.md` but swaps **which country’s series** fill the six factor **slots** (policy rate, GDP, CPI-type inflation, FX, oil, consumer confidence) — see regional mapping in that file. **Display names** in `macro_factors.json` → `factors[].name` (and thus the HTML factor table) must match the chosen geography (e.g. **中国消费者信心** vs **US Consumer Confidence**).

4. **After `financial_data.json` exists** (post–Phase 1): if **geographic revenue** clearly contradicts Step 0D, adjust the **macro narrative and `macro_factors.json` geography fields** in Phase 2 / 2.5 so Section III is consistent with Section II (or add a one-line note explaining HQ vs revenue mix).

---

## Phase 1 + 2 (Macro) + 3 (News): Parallel data collection

Spawn or run Agents 1–3. **Each task prompt must include `Report language: {en|zh}`.**

### Agent 1 — Financial Data Collector

**File:** `agents/financial_data_collector.md`

```
Report language: {en|zh}
Report calendar year: {Y_cal}
Report date (optional): {YYYY-MM-DD}
Company: {company_name}
Uploaded files: {PDFs or "none"}
Output path: workspace/{Company}_{Date}/financial_data.json
Follow agents/financial_data_collector.md
```

### Agent 2 — Macro Factor Scanner

**File:** `agents/macro_scanner.md`

```
Report language: {en|zh}
Company: {company_name}
Primary operating geography: {US|Greater_China|Eurozone|Japan|UK|Emerging_Asia_ex_China|Global_other}
Sector hint: {infer or ask user}
Reference: references/prediction_factors.md
Output path: workspace/{Company}_{Date}/macro_factors.json
Follow agents/macro_scanner.md
```

### Agent 3 — News & Industry Researcher

**File:** `agents/news_researcher.md`

```
Report language: {en|zh}
Company: {company_name}
Sector: {same as Agent 2}
Output path: workspace/{Company}_{Date}/news_intel.json
Follow agents/news_researcher.md
```

**Wait for all three to finish.**

---

## Phase 2: Financial analysis (orchestrator, inline)

Read `financial_data.json`; compute metrics per `references/financial_metrics.md`.  
**Fiscal year labels (“当年 / 上年”, KPI 财年, `METRICS_YEAR_CUR` / `METRICS_YEAR_PREV`):** Must match **`income_statement.current_year`** and **`prior_year`** as fixed by **Step 0C** (latest **published** full-year pair; default target **`FY(Y_cal − 1)`** vs **`FY(Y_cal − 2)`** when that annual exists). **YoY / 同比** is always those two **consecutive** full fiscal years in the JSON. If only interim (e.g. 9M) exists for the newest year, either keep the table on the last two **full** fiscal years with a **`notes[]`** lag explanation per Step 0C, or add a clearly labeled “最近中期 vs 上年同期” block — do not mix without stating it.
**Geographic revenue (Section II, fourth trend-card):** Fill **`geographic_revenue.analysis`** → **`{{GEO_REVENUE_TEXT}}`** from filings / `financial_data.json` (regional amounts, shares, growth, concentration as disclosed). Rules: **`references/financial_metrics.md`** (Geographic revenue mix) — keep the **card text factual**; do not add meta-lines like “this card does not discuss FX.”  
**Evidence gate for narrative claims:** Any valuation statement in summary / thesis / appendix (e.g. “估值处于历史低位”, target price, upside/downside, cheap/expensive vs history/peers) must be backed by non-null fields in `financial_analysis.json` → `valuation` or by explicitly cited market-data sources in the appendix. If valuation fields are unavailable, remove the valuation claim instead of hand-waving it. Likewise, do not present a live-market conclusion as fact when the underlying market-data fields are `null`.
**HTML narrative (no Markdown):** All strings that fill `{{SUMMARY_PARA_*}}`, `{{TREND*_TEXT}}`, `{{GEO_REVENUE_TEXT}}`, thesis, Sankey note, etc. must be **plain text** — do **not** use `**` / `*` / backticks; the template does not run a Markdown processor. See `references/report_style_guide_cn.md` or `report_style_guide_en.md` and `agents/report_writer_*.md`.  
**If `report_language=en`:** all free-text fields in `financial_analysis.json` must be **English**.  
**If `zh`:** Chinese prose as before.

Save `workspace/{Company}_{Date}/financial_analysis.json`.

---

## Phase 2.5: Revenue prediction (macro factor model)

Same formula as `references/prediction_factors.md`.  
**Macro geography:** Copy factor **labels and ordering** from `macro_factors.json` (which must already follow **Step 0D** + `agents/macro_scanner.md`). Do not reintroduce US-only names if `primary_operating_geography` is **`Greater_China`** or another non-US region.  
**Forecast horizon label:** Set **`predicted_fiscal_year_label`** to **`FY(latest_actual + 1)E`** where **`latest_actual`** is the fiscal year in `financial_data.json` → **`income_statement.current_year`** (e.g. FY2025 actual → **FY2026E**). This must match the Sankey **forecast** tab (Step 0C §4). Only use a later year (e.g. FY2027E) if you deliberately extend the horizon and keep **Sankey + waterfall + appendix** consistent.  
**If `en`:** use English for factor display names in `prediction_waterfall.json` where they are meant for the HTML table; numeric fields unchanged.

Save `prediction_waterfall.json`.

---

## Phase 3: Porter Five Forces

Use `references/porter_framework.md`. Three perspectives (~300 words each).  
**If `en`:** `porter_analysis.json` body text **English**. **If `zh`:** Chinese.

Save `porter_analysis.json`.

---

## Phase 4: Sankey data preparation

Build **`sankeyActualData`** from **`current_year`** P&L in `financial_data.json` and **`sankeyForecastData`** by scaling that structure with **`prediction_waterfall.json` → `predicted_revenue_growth_pct`** for **`FY(latest_actual + 1)E`** (see **Step 0C §4**). Fill **`{{SANKEY_YEAR_ACTUAL}}`** / **`{{SANKEY_YEAR_FORECAST}}`** accordingly.  
**If `en`:** Sankey node `name` strings **English** (Revenue, Cost of revenue, …). **If `zh`:** Chinese labels as in the Chinese template examples.

---

## Phase 5: Report generation (language branch)

### If `report_language = zh`

**File:** `agents/report_writer_cn.md`  
**Style:** `references/report_style_guide_cn.md`  
**Output:** `workspace/{Company}_{Date}/{Company}_Research_CN.html`  

**Reproducible / auditable structure:** Run the extractor **before** filling placeholders (do **not** copy skeleton from another company’s HTML in `workspace/`):

```bash
python3 scripts/extract_report_template.py --lang cn --sha256 \
  -o workspace/{Company}_{Date}/_locked_cn_skeleton.html
```

Then fill **only** `{{PLACEHOLDER}}` markers in the extracted file (or paste into your editor from the same extract) and save as `{Company}_Research_CN.html`. Do not alter the locked HTML/CSS/JS skeleton. **Post-processing caution:** Do **not** delete HTML comment lines that contain `-->` solely because they include illustrative `{{…}}` text — removing the only closing `-->` for a multi-line `<!--` will comment out the Porter/Appendix DOM (see `agents/report_writer_cn.md` 写作规范、`agents/report_validator.md` §5).
After placeholders are filled, you **may** remove **only** single-line, self-contained instructional comments that still contain sample `{{...}}` text **if** you have **positively verified** that the line is not the closing leg of a multi-line `<!-- ... -->` block (e.g. a standalone `<!-- … {{…}} … -->`). **If there is any doubt, do not delete the comment line** — leave it, or rewrite the comment so it no longer contains `{{` / `}}`, instead of removing a line that might be the only `-->` closing an earlier `<!--`. Deliverables must not contain unreplaced real placeholders; optional comment cleanup must never risk breaking the DOM.

### If `report_language = en`

**File:** `agents/report_writer_en.md`  
**Style:** `references/report_style_guide_en.md`  
**Output:** `workspace/{Company}_{Date}/{Company}_Research_EN.html`  

**Reproducible / auditable structure:**

```bash
python3 scripts/extract_report_template.py --lang en --sha256 \
  -o workspace/{Company}_{Date}/_locked_en_skeleton.html
```

Then fill **only** placeholders and save as `{Company}_Research_EN.html`.

**Post-processing:** Same HTML comment rule as Chinese — do **not** strip lines that close a `<!--` block inside the Porter company panel (see `report_writer_en.md`). If you might remove a single-line comment that contains sample `{{...}}` text, apply the same **“only when sure / otherwise leave or reword”** rule as in the Chinese branch above.

- Header: **English legal name** in the first name line; **ticker only** on the second line (see `report_writer_en.md` rules).  
- Use `{{RATING_EN}}`, `{{CONFIDENCE_EN}}` per the English template.  
- Same structural rules as CN: placeholders only, no new classes/ids.

**Wait for Phase 5 to complete before Phase 6.**

---

## Phase 6: Report validation

**File:** `agents/report_validator.md`

**Inputs:**

- HTML: `*_Research_CN.html` **or** `*_Research_EN.html` (whichever Phase 5 produced)  
- `financial_data.json`  
- `financial_analysis.json`
- `macro_factors.json`
- `news_intel.json`
- `prediction_waterfall.json`  

Run all checks; fix CRITICAL issues until zero remain.  
Treat **checklist item 9** in `agents/report_validator.md` (segment/region list must use percentages consistently with `segment_data`, or use amounts only for all items) as a **pre-delivery** fix: do not ship HTML with mixed formats.
Treat the following as **pre-delivery blockers** as well, even if they are classified as WARNING in the validator output: narrative claims unsupported by JSON fields, appendix/source dates later than the report date, “real-time/current/latest” wording when the underlying data is knowledge-cutoff or estimated, and geographic mix text that mixes regions with product/brand labels.

**Why some blockers are WARNING, not CRITICAL:** Items 10–13 (and similar content checks) are labeled **WARNING** because a short validator checklist cannot mechanically prove narrative wrongdoing the way it can detect missing sections or stray `{{…}}`. That lower label does **not** mean they may ship as-is — fix them before delivery like item 9, per `agents/report_validator.md`.

---

## Final output

Deliver the generated file:

- `{Company}_Research_CN.html` if `zh`  
- `{Company}_Research_EN.html` if `en`  

Summarize: data mode, predicted revenue growth and drivers, data confidence caveats, φ and β reference path, validation CRITICAL/WARNING counts.

---

## Data confidence labels

- `"data_source": "10-K upload"` → high confidence  
- `"data_source": "web search"` → medium; mark estimates with `~`  
- `"data_source": "primary filing (web fetched)"` → high confidence when line items were pulled from EDGAR / company IR / exchange filing site during web mode and cross-checked to the filing itself  
- Missing numbers → `null`, note "Data unavailable" **in the report language**

---

## Reference files

| File | When |
|------|------|
| `references/prediction_factors.md` | Phase 2.5 |
| `references/porter_framework.md` | Phase 3 |
| `references/financial_metrics.md` | Phase 2 |
| `references/report_style_guide_cn.md` | Phase 5 if `zh` |
| `references/report_style_guide_en.md` | Phase 5 if `en` |
