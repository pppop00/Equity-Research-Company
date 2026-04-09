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

All intermediate JSON files and the final HTML go here.

**Detect environment:**

- Claude Code: parallel subagents as below  
- Claude.ai: same phases sequentially  

---

## Phase 1 + 2 (Macro) + 3 (News): Parallel data collection

Spawn or run Agents 1–3. **Each task prompt must include `Report language: {en|zh}`.**

### Agent 1 — Financial Data Collector

**File:** `agents/financial_data_collector.md`

```
Report language: {en|zh}
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
**If `report_language=en`:** all free-text fields in `financial_analysis.json` must be **English**.  
**If `zh`:** Chinese prose as before.

Save `workspace/{Company}_{Date}/financial_analysis.json`.

---

## Phase 2.5: Revenue prediction (macro factor model)

Same formula as `references/prediction_factors.md`.  
**If `en`:** use English for factor display names in `prediction_waterfall.json` where they are meant for the HTML table; numeric fields unchanged.

Save `prediction_waterfall.json`.

---

## Phase 3: Porter Five Forces

Use `references/porter_framework.md`. Three perspectives (~300 words each).  
**If `en`:** `porter_analysis.json` body text **English**. **If `zh`:** Chinese.

Save `porter_analysis.json`.

---

## Phase 4: Sankey data preparation

Build actual and forecast Sankey JS objects from `financial_data.json` and predicted growth.  
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

Then fill **only** `{{PLACEHOLDER}}` markers in the extracted file (or paste into your editor from the same extract) and save as `{Company}_Research_CN.html`. Do not alter the locked HTML/CSS/JS skeleton.

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
- `prediction_waterfall.json`  

Run all checks; fix CRITICAL issues until zero remain.

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
