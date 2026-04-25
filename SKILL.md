---
name: equity-research
description: >
  Full-stack equity research report generator. Trigger when the user wants to analyze a company, generate an equity research report, fundamental analysis, or stock investment research. Works with a company name (web search) or uploaded filings (10-K / 10-Q PDFs, HK/A-share reports). P0 mandatory gates (see SKILL.md Step 0A): (1) explicit report language en/zh before any research; (2) when the SEC API path applies, real email or explicit decline before workspace/Phase 1. Outputs one interactive HTML report (Sankey, macro waterfall, Porter). Never skip Step 0A — it is the key to all downstream procedures.

  TRIGGER on: "equity research", "research report", "analyze [company]", "financial analysis of [company]", "做研报", "研究报告", "分析[公司]", English/Chinese equivalents, or user uploads a 10-K/10-Q and wants full research (not only a revenue-flow diagram).
---

# Equity Research Skill

Generate a professional equity research report for any public company. You are the orchestrator — you coordinate data collection, analysis, and report writing, either via parallel subagents (Claude Code) or sequentially (Claude.ai).

---

## Step 0M: Load machine-readable workflow contract (mandatory)

Before Step 0A, load `workflow_meta.json` as the machine-readable contract for this run.

- Treat `workflow_meta.json` as the source of truth for:
  - gate IDs and preconditions
  - phase order
  - packaging profiles in Phase 6 (`strict_18_full_qc_secapi`, `strict_17_full_qc_no_secapi`, `strict_13_fast_no_qc_secapi`, `strict_12_fast_no_qc_no_secapi`)
- `SKILL.md` and `agents/*.md` remain the narrative execution guide; if there is a conflict on artifact presence or packaging strictness, follow `workflow_meta.json`.
- Persist run mode flags early (at least in working notes):  
  `qc_mode = full|fast` and `sec_api_mode = yes|no`  
  so Phase 6 can select the correct packaging profile instead of forcing unavailable artifacts.

---

## Step 0A: Mandatory gates — **language + SEC contact (before workspace & Phase 1)**

### 0A.0 — **P0 硬门禁（不可跳过、不可推断）**

These two gates are **P0**: they are the **key** to every later step. **If they are not satisfied, nothing else in this skill may run.**

| Gate | What must be true before Step 0B / Phase 1 |
|------|--------------------------------------------|
| **§0A.1 报告语言** | `report_language` is **`en`** or **`zh`**, resolved **only** as allowed in §0A.1 (explicit table **or** user answer to the language question). |
| **§0A.2 SEC 邮箱** | Either **(a)** §0A.2 **does not apply** (see below), **or (b)** it applies and the user has supplied a **real email** or an **explicit decline** (`no email` / `不提供邮箱` / unmistakable refusal). |

**Strictly forbidden until both rows above are satisfied for this run** (non-exhaustive):

- Creating **`workspace/`**, writing any **`financial_data.json`** / intermediate JSON, or starting **Phase 1–6**
- Spawning or simulating **Agents 1–5**, `web_search` / `web_fetch` for **company financials, filings, or industry research** (other than the **single** listing-resolution search allowed in §0A.2 when the primary listing is unclear — and that search is **only** after §0A.1 is complete)
- Announcing progress such as “正在生成完整研报…”, “Starting Phase 1…”, “collecting 10-K…”, or otherwise behaving as if research has begun
- **Inferring** `report_language` from the user’s conversational language (e.g. Chinese vs English messages), UI locale, or company country — **not allowed** unless a cue appears in the **explicit table** in §0A.1
- **Inferring** `financial_data_sec_api = no` when §0A.2 applies — **not allowed** without the user’s **explicit decline** of the SEC API path (or a valid email for `yes`)

**Do not create `workspace/`** and **do not start Phase 1** (no agents, no JSON generation) until **both** §0A.1 and §0A.2 are satisfied **for this run** as defined in the table above.

---

### 0A.1 Report language

Resolve `report_language` to exactly one of: **`en`** | **`zh`**. This is the **first** gate; resolve it **before** evaluating §0A.2 or performing any allowed `web_search`.

#### When language is already explicit

Treat any of the following as explicit (map and proceed **without** asking):

| Maps to `report_language = en` | Maps to `report_language = zh` |
|--------------------------------|----------------------------------|
| `English`, `EN`, `英文`, `英语`, `in English`, `English report`, `英文研报`, `generate English` | `Chinese`, `ZH`, `中文`, `简体`, `Chinese report`, `中文研报`, `生成中文` |

**Strict rule:** The user **writing in Chinese** or **English** in chat, or asking for a “report” / “研报” **without** one of the phrases above, is **not** sufficient to set `report_language`. Phrases like “做研报”, “analyze Apple”, “equity research” **alone** do **not** set language — you **must** ask the single question below and **stop**.

If the user states both or contradictory cues, ask one short clarification (still **no** workspace / Phase 1).

#### When language is **not** explicit

Reply **only** with this prompt and **stop** until the user answers:

> **What language should the final HTML report use — English or Chinese (中文)?**  
> Reply with **English** or **Chinese**.

After the user answers, map **English** → `en`, **Chinese** / **中文** → `zh`. If the reply is ambiguous, ask again.

#### Persist `report_language`

- Store `report_language` for all subsequent phases.
- Every agent task prompt (Phase 1+) **must** include:  
  `Report language: en` **or** `Report language: zh`  
  When `en`: **all narrative text in intermediate JSON and the final HTML must be English** (numbers and tickers as usual).  
  When `zh`: use Chinese for narrative as today; final HTML from `report_writer_cn.md`.

---

### 0A.2 US SEC EDGAR API — **real contact email gate (P0; same priority as 0A.1)**

This is the **second** gate. Evaluate it **only after** `report_language` is fixed in §0A.1.

SEC fair-access rules require a **truthful, contactable** identifier in the HTTP `User-Agent` when calling `data.sec.gov` (see `scripts/sec_edgar_fetch.py`). The orchestrator **must not** invent, placeholder, or guess an email.

#### When this sub-step applies

Evaluate **after** §0A.1 is done. **All** must be true:

1. **No uploaded SEC PDFs** for this run as the primary financial input — i.e. **Mode A** (company name / ticker only). If the user attached **10-K / 10-Q** PDFs (**Mode B/C**), set **`financial_data_sec_api = no`** and **skip** the rest of 0A.2 (Agent 1 uses file extraction per `agents/financial_data_collector.md`).
2. The research target is **intended as a US-listed SEC periodic filer** (NYSE / Nasdaq / other US exchange; **10-K / 10-Q** on EDGAR). **Treat as US** when the user says e.g. **美股**, **US listing**, **NASDAQ / NYSE**, gives a **bare US ticker** (`MSFT`), or clearly names a **known US-only** listing context. **Treat as non-US** when the user says e.g. **港股 / A股 / 伦敦**, primary listing is clearly non-US, or the company is private / not an SEC periodic filer.
3. **If listing is unclear**, you may use **at most one** `web_search` whose **sole purpose** is to determine whether the **primary listing** is US SEC — still **no** workspace until 0A.2 is resolved. **Do not** run this search until §0A.1 is complete. If the answer is not US SEC, set **`financial_data_sec_api = no`** and skip the email ask.

#### When 0A.2 does **not** apply

Set **`financial_data_sec_api = no`** and proceed to Step 0B **only if** §0A.1 is already satisfied. (Examples: Mode B/C with PDFs; clearly non-US listing; private company.)

#### When 0A.2 **does** apply — ask for email (or explicit decline)

**Stop** — do **not** run Step 0B yet — until the user either supplies a **real email** or **explicitly declines** the SEC API path.

You **must** send the email prompt (or the `zh` equivalent) to the user in this case. **Do not** skip the question, **do not** assume decline, and **do not** set `financial_data_sec_api = no` without one of the outcomes in the **Resolve replies** table below.

Use wording that matches **`report_language`**:

**If `report_language = en`**, ask (adapt politely):

> To use the **SEC EDGAR API** (`data.sec.gov`) for faster, structured US filings, SEC policy requires a **real contact email** in the request User-Agent.  
> **Please reply with one email address** (we will use it only as `EquityResearchSkill/1.0 (you@domain.com)` for this run).  
> If you **do not want to provide an email**, reply **`no email`** — we will use **web search + primary filing fetches** instead (no SEC API-first script).

**If `report_language = zh`**, ask (adapt politely):

> 若本轮走 **SEC 官方 EDGAR 数据接口**（`data.sec.gov`），按 SEC 要求必须在请求头 User-Agent 中包含**真实、可联系的邮箱**。  
> 请直接回复**一个您本人可收信的邮箱**（仅用于本轮标识字符串，例如 `EquityResearchSkill/1.0 (您@域名)`）。  
> 若**不愿提供邮箱**，请回复 **`不提供邮箱`** 或 **`no email`** — 则本轮财务数据改为 **网络检索 + 源站抓取**，**不**调用 `sec_edgar_fetch.py` 的 API 优先路径。

#### Resolve replies

| Outcome | Set |
|--------|-----|
| User sends a **plausible single email address** | **`financial_data_sec_api = yes`**, **`SEC_EDGAR_USER_AGENT = EquityResearchSkill/1.0 (email@normalized)`** — strip surrounding spaces; **reject** obvious placeholders (`example.com`, `test@test`, `user@localhost`) by asking once more for a **real** mailbox. |
| User declines: **`no email`**, **`不提供邮箱`**, or unmistakable refusal | **`financial_data_sec_api = no`** |
| Ambiguous | Ask once more; **still no Step 0B** until resolved. |

If the user **already** supplied one plausible email **and** confirmed a US SEC / **美股** context **before** you send the template ask (e.g. same message after language is clear), you may set **`financial_data_sec_api = yes`** **without** repeating the question — still apply the **placeholder rejection** rule.

**Never** fabricate or assume an email. If the user never supplies one and never declines, keep clarifying — same discipline as 0A.1.

#### Persist for Agent 1

- Every Agent 1 task prompt **must** include exactly one line: **`Financial data SEC API: yes`** or **`Financial data SEC API: no`**.
- If **`yes`**, also include: **`SEC_EDGAR_USER_AGENT: EquityResearchSkill/1.0 (user@domain.com)`** (the same string Agent 1 passes to `scripts/sec_edgar_fetch.py` as **`--user-agent`**).

---

## Step 0B: Parse input & setup workspace

**Input mode:**

- **Mode A** — Company name only → Web Search mode  
- **Mode B** — Company name + 10-K PDF → File-based mode  
- **Mode C** — Company name + 10-K + 10-Q PDF → Full File mode  

**Only after Step 0A is fully satisfied** (§0A.0 P0 table: language resolved **and** §0A.2 either N/A or email/decline resolved), create:

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
   - **`latest_interim`** (optional but **required to attempt**): most recent **10-Q / 季报 / 半年报** on or before the report date — **Agent 1 alone** structures this from primary filings per `agents/financial_data_collector.md`; downstream agents **summarize or declare a gap**, they do not invent quarterly tables. Use **`null`** only if no filing exists, with **`notes[]`** explanation. Feeds Section II **「最新经营更新」** and may inform **`prediction_waterfall.json`** company-specific lines when material. **Comparison convention:** card prose **leads with YoY** (same quarter prior year or YTD vs prior-year YTD); **QoQ vs prior quarter** only as a labeled secondary beat when material (see `references/financial_metrics.md` — Latest operating update).  
   - **If `FY(Y_cal − 1)` annual is not yet published** on the report date, use the **latest two consecutive full fiscal years that *are* published** (e.g. FY2024 vs FY2023) and add a **`notes[]`** line stating that **`FY(Y_cal − 1)` was unavailable** so readers know why the table lags.

4. **Section IV — Sankey (two tabs)**  
   - **Actual tab (`{{SANKEY_YEAR_ACTUAL}}`, `sankeyActualData`):** Built from the **same** P&L basis as **`current_year`** in `financial_data.json` (the latest **full-year** actual in the file). **Do not** label or scale “actual” two years behind `Y_cal` without the note in §3.  
   - **Forecast tab (`{{SANKEY_YEAR_FORECAST}}`, `sankeyForecastData`):** **P&L structure scaled** to the **next fiscal year** after `current_year` using the model’s predicted revenue growth — label **`FY{current_FY + 1}E`** (e.g. actual FY2025 → **FY2026E**). This is the default “次财年 / 相对最新年报的下一完整财年” forecast, not a jump to **FY2027E** unless the model and narrative **explicitly** target that later year and the HTML label matches `prediction_waterfall.json`.

5. **Phase 2.5 — `prediction_waterfall.json`**  
   - **`predicted_fiscal_year_label`** **must match** the Sankey **forecast** tab (default **`FY(latest_actual + 1)E`**). The waterfall “预测财年” line should use the **same** label.

Pass **`Report calendar year: {Y_cal}`** (and **`Report date: {YYYY-MM-DD}`** if known) into **every** Agent 1 task prompt so searches target the correct 10-K / 年报. When the company is US-listed and the symbol is known, also pass **`Trading symbol:`** and, if available, **`SEC CIK:`** so Agent 1 can run **`scripts/sec_edgar_fetch.py`** without an extra ticker-resolution step.

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

## Phase 1: Parallel data collection via Agents 1–3

**Inputs:** `company_name`, `report_language`, Step 0A/0C/0D outputs (`financial_data_sec_api`, `SEC_EDGAR_USER_AGENT` when applicable, `Y_cal`, `primary_operating_geography`), uploaded files.

**Agent calls:**

- Agent 1: `agents/financial_data_collector.md` → `workspace/{Company}_{Date}/financial_data.json`
- Agent 2: `agents/macro_scanner.md` → `workspace/{Company}_{Date}/macro_factors.json`
- Agent 3: `agents/news_researcher.md` → `workspace/{Company}_{Date}/news_intel.json`

**Output:** three base JSON files above.

**Gate:** do not leave Phase 1 until Agent 1/2/3 all complete successfully.

**Detailed execution rules, exceptions, and formatting constraints:** `references/phase_execution_rules.md` (Phase 1 section).

---

## Phase 1.5: Agent 4 — Edge Insight Writer

**Inputs:** `financial_data.json`, `news_intel.json`, `report_language`, `company_name`.

**Agent call:** `agents/edge_insight_writer.md` → `workspace/{Company}_{Date}/edge_insights.json`.

**Output:** `edge_insights.json`.

**Gate:** must finish before Phase 2; Phase 2 must consume `summary_para_2_draft`.

**Detailed execution rules:** `agents/edge_insight_writer.md` (Downstream Contract section).

---

## Phase 2: Financial analysis (orchestrator, inline)

**Inputs:** `financial_data.json`, `news_intel.json`, `edge_insights.json`, `report_language`, `Y_cal`.

**Execution:** orchestrator computes metrics and narrative per `references/financial_metrics.md` and style guide.

**Output:** `workspace/{Company}_{Date}/financial_analysis.json`.

**Gate:** `financial_analysis.json` must be complete and internally consistent before Phase 2.5.

**Detailed execution rules, exceptions, and format contracts:** `references/phase_execution_rules.md` (Phase 2 section).

---

## Phase 2.5: Revenue prediction (macro factor model)

**Inputs:** `macro_factors.json`, `news_intel.json`, `financial_data.json`, `financial_analysis.json` (if needed for reconciliation), `report_language`, `primary_operating_geography`.

**Execution:** compute macro + company-specific bridge using `references/prediction_factors.md`.

**Output:** `workspace/{Company}_{Date}/prediction_waterfall.json`.

**Gate:** forecast label, geography mapping, and bridge reconciliation must pass before QC (Phase 2.6).

**Detailed execution rules, event-normalization methodology, and table-format constraints:** `references/phase_execution_rules.md` (Phase 2.5 section).

---

## Phase 2.6: Macro adversarial QC

**Inputs:** `macro_factors.json`, `prediction_waterfall.json`, `financial_analysis.json`, `news_intel.json`, context from Step 0D.

**Agent calls:**

- `agents/qc_macro_peer_a.md` → `workspace/{Company}_{Date}/qc_macro_peer_a.json`
- `agents/qc_macro_peer_b.md` → `workspace/{Company}_{Date}/qc_macro_peer_b.json`

**Output:** two macro QC files.

**Gate:** both peer outputs required before Phase 3.6 merge.

**Detailed execution rules:** `agents/qc_macro_peer_a.md` and `agents/qc_macro_peer_b.md` (each includes Downstream Contract).

---

## Phase 3: Porter Five Forces

**Inputs:** `news_intel.json`, `financial_data.json` (as needed), `report_language`.

**Execution:** produce Porter base analysis using `references/porter_framework.md`.

**P0 scoring orientation:** Porter scores are **threat / pressure scores**, not attractiveness scores: **1 = lowest threat / best / green**, **3 = mixed / amber**, **5 = highest threat / worst / red**. For `rivalry`, intense industry competition or price wars must score high (4-5), while near-monopoly or minimal competition must score low (1-2).

**Output:** `workspace/{Company}_{Date}/porter_analysis.json`.

**Gate:** base Porter analysis complete before Phase 3.5 QC.

**Detailed execution rules:** `references/porter_framework.md`.

---

## Phase 3.5: Porter adversarial QC

**Inputs:** `porter_analysis.json`, `news_intel.json`, `financial_data.json` (for peer A), `report_language`.

**Agent calls:**

- `agents/qc_porter_peer_a.md` → `workspace/{Company}_{Date}/qc_porter_peer_a.json`
- `agents/qc_porter_peer_b.md` → `workspace/{Company}_{Date}/qc_porter_peer_b.json`

**Output:** two Porter QC files.

**Gate:** both peer outputs required before Phase 3.6.

**Detailed score-change vs maintain semantics:** `agents/qc_porter_peer_a.md` and `agents/qc_porter_peer_b.md` (each includes Downstream Contract).

---

## Phase 3.6: QC resolution merge

**Inputs:** macro QC outputs, Porter QC outputs, `prediction_waterfall.json`, `porter_analysis.json`, and dependent JSON files.

**Agent call:** `agents/qc_resolution_merge.md`.

**Output:**

- `workspace/{Company}_{Date}/qc_audit_trail.json`
- in-place updates where needed to `prediction_waterfall.json`, `porter_analysis.json`, and optionally `financial_analysis.json`

**Gate:** merged outputs become the only authoritative version for Phases 4-6.

**Detailed merge policy and full-run/fast-run exceptions:** `agents/qc_resolution_merge.md` (Execution Policy section).

---

## Phase 4: Sankey data preparation

**Inputs:** `financial_data.json` (`current_year` basis), `prediction_waterfall.json` (`predicted_revenue_growth_pct` and forecast fiscal label), `report_language`.

**Execution:** build actual + forecast Sankey datasets for the locked template.

**Output:** Sankey placeholder payloads consumed in Phase 5.

**Gate:** Sankey year labels and forecast assumptions must reconcile with Phase 2.5 outputs.

**Detailed execution rules:** `references/phase_execution_rules.md` (Phase 4 section).

---

## Phase 5: Report generation (language branch)

**Inputs:** all validated upstream JSON, Sankey payloads, `report_language`, locked template extractor script.

**Agent calls:**

- `agents/report_writer_cn.md` for `zh`
- `agents/report_writer_en.md` for `en`

**Output:**

- `workspace/{Company}_{Date}/{Company}_Research_CN.html` (zh)
- `workspace/{Company}_{Date}/{Company}_Research_EN.html` (en)

**Gate:** only placeholder substitution on extracted locked skeleton; no structural HTML/CSS/JS edits.

**Detailed waterfall contract, placeholder rules, and language-specific formatting constraints:** `references/phase_execution_rules.md` (Phase 5 section), `agents/report_writer_*.md`, and `references/report_style_guide_{cn|en}.md`.

---

## Phase 5.2: Card logo production (when card workflow is enabled)

If this run includes card artifacts (`*.card_slots.json`, `01_cover.png`, etc.), run **logo-production-agent first** before any card rendering:

- **Agent call:** `agents/logo_production_agent.md`
- **Core requirement (P0):** Card1 logo export resolution must be at least **2x** the render slot on both width and height.
- **Required metadata in `*.card_slots.json`:** `logo_render_width_px`, `logo_render_height_px`, `logo_export_width_px`, `logo_export_height_px`, `logo_scale_factor`
- **Fallback when render size not provided:** treat legacy slot as `276x328`, so export must be at least `552x656`.

This phase is optional for report-only runs and mandatory for card-output runs.

---

## Phase 5.5: Final report data validation

**Inputs:** final HTML + all upstream JSON + `qc_audit_trail.json` when present.

**Agent call:** `agents/final_report_data_validator.md`.

**Output:** `workspace/{Company}_{Date}/final_report_data_validation.json`.

**Gate:** must reach zero CRITICAL before Phase 6.

**Detailed validation expectations and pre-delivery warnings policy:** `agents/final_report_data_validator.md`.

---

## Phase 6: Report validation

**Inputs:** final HTML, all production JSON, `final_report_data_validation.json`, optional `qc_audit_trail.json`.

**Agent call:** `agents/report_validator.md`.

**Output:** final delivery-ready HTML package + `workspace/{Company}_{Date}/report_validation.txt` + `workspace/{Company}_{Date}/structure_conformance.json`.

**Gate:** resolve CRITICAL plus designated pre-delivery WARNING blockers before delivery.

**Detailed blocker policy:** `agents/report_validator.md`.

### Phase 6 packaging profiles (owned by report validator)

`report_validator` must select one packaging profile from `workflow_meta.json` and write the chosen profile into `structure_conformance.json`.

Selection rule:

1. `qc_mode = full` and `sec_api_mode = yes` → `strict_18_full_qc_secapi`
2. `qc_mode = full` and `sec_api_mode = no` → `strict_17_full_qc_no_secapi`
3. `qc_mode = fast` and `sec_api_mode = yes` → `strict_13_fast_no_qc_secapi`
4. `qc_mode = fast` and `sec_api_mode = no` → `strict_12_fast_no_qc_no_secapi`

Notes:

- `qc_mode = fast` is allowed only when the user explicitly requests a shortened run (same policy as Phase 3.6).
- `sec_api_mode = no` is valid for non-US, PDF-first runs, or explicit SEC email decline cases; do not force `sec_edgar_bundle.json` in those runs.
- Cleanup targets remain defined by `workflow_meta.json` + `agents/report_validator.md`.

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
| `references/phase_execution_rules.md` | Detailed constraints for Phases 1-6 |
| `references/intelligence_layer.md` | Agent 3, Agent 4, Phase 2, Phase 2.5, Phase 6 |
| `references/prediction_factors.md` | Phase 2.5 |
| `references/porter_framework.md` | Phase 3 |
| `references/financial_metrics.md` | Phase 2 |
| `references/report_style_guide_cn.md` | Phase 5 if `zh` |
| `references/report_style_guide_en.md` | Phase 5 if `en` |
| `agents/logo_production_agent.md` | Phase 5.2 when card workflow is enabled |
