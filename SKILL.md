---
name: equity-research
description: >
  Full-stack equity research report generator. Trigger when the user wants to analyze a company, generate an equity research report, fundamental analysis, or stock investment research. Works with a company name (web search) or uploaded filings (10-K / 10-Q PDFs, HK/A-share reports). P0 mandatory gates (see SKILL.md Step 0A): (1) explicit report language en/zh before any research; (2) when the SEC API path applies, real email or explicit decline before workspace/Phase 1. Outputs one interactive HTML report (Sankey, macro waterfall, Porter). Never skip Step 0A — it is the key to all downstream procedures.

  TRIGGER on: "equity research", "research report", "analyze [company]", "financial analysis of [company]", "做研报", "研究报告", "分析[公司]", English/Chinese equivalents, or user uploads a 10-K/10-Q and wants full research (not only a revenue-flow diagram).
---

# Equity Research Skill

Generate a professional equity research report for any public company. You are the orchestrator — you coordinate data collection, analysis, and report writing, either via parallel subagents (Claude Code) or sequentially (Claude.ai).

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

## Phase 1 + 2 (Macro) + 3 (News): Parallel data collection

Spawn or run Agents 1–3. **Each task prompt must include `Report language: {en|zh}`.**

### Agent 1 — Financial Data Collector

**File:** `agents/financial_data_collector.md`

```
Report language: {en|zh}
Financial data SEC API: {yes|no}
SEC_EDGAR_USER_AGENT (only if yes): {EquityResearchSkill/1.0 (user@real.domain)}
Report calendar year: {Y_cal}
Report date (optional): {YYYY-MM-DD}
Company: {company_name}
Trading symbol (optional): {e.g. MSFT — helps US SEC API path; else unknown}
SEC CIK (optional): {10-digit CIK if known; else unknown}
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
Sub-industry hint (optional): {from filings/user/news, else infer}
Company role hint (optional): {e.g. AI infrastructure supplier, AI/cloud spender, bank, payment network, else infer}
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

**Post-collection macro regime reconciliation:** After `financial_data.json` and `news_intel.json` exist, re-check `macro_factors.json` → `macro_regime_context` before Phase 2.5. If filings, geographic/segment mix, or news materially contradict Agent 2's initial `sub_industry`, `company_role`, `sector_regime`, or transmission channels, amend `macro_regime_context` and `macro_factor_commentary` (or re-run Agent 2). Do not change β values merely because the role/regime text changed; only adjust β when `beta_source: "adjusted"` is supported and the waterfall is recomputed.

---

## Agent 4 — Edge Insight Writer

Use `agents/edge_insight_writer.md` after Agent 1 and Agent 3 have finished. This agent exists to make every report contain one evidence-backed, non-obvious reading rather than a generic company summary.

```
Report language: {en|zh}
Company: {company_name}
Inputs: workspace/{Company}_{Date}/financial_data.json, workspace/{Company}_{Date}/news_intel.json
Output path: workspace/{Company}_{Date}/edge_insights.json
Follow agents/edge_insight_writer.md
```

**Wait for Agent 4 to finish before Phase 2.** Do not let Phase 2 write `summary_para_2` without reading `edge_insights.json`.

---

## Phase 2: Financial analysis (orchestrator, inline)

Read `financial_data.json`, `news_intel.json`, and `edge_insights.json`; compute metrics per `references/financial_metrics.md`.  
**Fiscal year labels (“当年 / 上年”, KPI 财年, `METRICS_YEAR_CUR` / `METRICS_YEAR_PREV`):** Must match **`income_statement.current_year`** and **`prior_year`** as fixed by **Step 0C** (latest **published** full-year pair; default target **`FY(Y_cal − 1)`** vs **`FY(Y_cal − 2)`** when that annual exists). **YoY / 同比** is always those two **consecutive** full fiscal years in the JSON. If only interim (e.g. 9M) exists for the newest year, either keep the table on the last two **full** fiscal years with a **`notes[]`** lag explanation per Step 0C, or add a clearly labeled “最近中期 vs 上年同期” block — do not mix without stating it.
**Financial metrics table (`{{METRICS_ROWS}}`) — final column is a conclusion label, not a number:** In Section II, the fourth column **`同比变动` / `YoY movement`** must be a qualitative verdict after reading the current/prior values, not a raw delta such as `+0.62%`. Use the controlled vocabulary in `references/financial_metrics.md` (e.g. **显著改善 / 改善 / 恶化 / 权益缺口收窄**; English equivalents for `en`). Put numeric deltas in narrative text or notes when useful, but the table cell itself is the verdict.
**Latest operating update (Section II, fourth trend-card — **最新经营更新** / **Latest operating update**):** Fill **`latest_operating_update`** in `financial_analysis.json` → **`{{LATEST_OPERATING_UPDATE_TEXT}}`** and **`{{TREND_UPDATE_DIRECTION}}`**, using **`financial_data.json` → `latest_interim`** (10-Q / TTM / interim) **as produced by Agent 1**, plus filings and **`news_intel.json`** for guidance. **Lead with the covered period** so readers do not confuse interim momentum with full-year YoY; **headline growth = YoY** unless the user or filing explicitly centers QoQ (then say so). Rules: **`references/financial_metrics.md`** (Latest operating update) and **`references/report_style_guide_{cn|en}.md`** (Latest operating update).  
**Geographic revenue (Section II, fifth trend-card):** Fill **`geographic_revenue.analysis`** → **`{{GEO_REVENUE_TEXT}}`** from filings / `financial_data.json` (regional amounts, shares, growth, concentration as disclosed). Rules: **`references/financial_metrics.md`** (Geographic revenue mix) — keep the **card text factual**; do not add meta-lines like “this card does not discuss FX.”  
**Evidence gate for narrative claims:** Any valuation statement in summary / thesis / appendix (e.g. “估值处于历史低位”, target price, upside/downside, cheap/expensive vs history/peers) must be backed by non-null fields in `financial_analysis.json` → `valuation` or by explicitly cited market-data sources in the appendix. If valuation fields are unavailable, remove the valuation claim instead of hand-waving it. Likewise, do not present a live-market conclusion as fact when the underlying market-data fields are `null`.
**Investment Summary paragraphs (`{{SUMMARY_PARA_1}}`–`{{SUMMARY_PARA_4}}`):** Write all four paragraphs into `financial_analysis.json` as `summary_para_1` through `summary_para_4`; each must be plain text, no Markdown. For `zh`, target **160–200 Chinese characters each**. For `en`, target **90–130 words each**. Structure:
- **`summary_para_1`** = combine the old company/business overview and latest financial performance into one paragraph: business model, revenue scale, YoY growth, margin/cash-flow quality, and listing context when relevant.
- **`summary_para_2`** = use **`edge_insights.json` → `summary_para_2_draft`** as the base. It must include the chosen edge insight's surface read, hidden rule / reframed read, and investment implication. Do not replace it with generic industry commentary.
- **`summary_para_3`** = keep the existing core thesis / catalysts role, expanded to the new length with concrete drivers and constraints.
- **`summary_para_4`** = keep the existing industry position role: use **`news_intel.json` → `industry_position`** (market-share time series, niche definition, reputation, operating vs revenue geography), reconciled with **`financial_data.json`** geographic revenue and segment names. Filings override inconsistent web snippets; if third-party share data is thin, keep the paragraph honest and qualitative rather than fabricating a series.

**HTML narrative (no Markdown):** All strings that fill `{{SUMMARY_PARA_*}}`, `{{TREND*_TEXT}}`, `{{LATEST_OPERATING_UPDATE_TEXT}}`, `{{GEO_REVENUE_TEXT}}`, thesis, Sankey note, etc. must be **plain text** — do **not** use `**` / `*` / backticks; the template does not run a Markdown processor. See `references/report_style_guide_cn.md` or `report_style_guide_en.md` and `agents/report_writer_*.md`.  
**KPI 第三卡（自由现金流）方向：** 若两年 FCF 均为负但同比向零收窄，**勿**填 `{{KPI3_DIRECTION}}` = `up`（易与「已健康」混淆）；用 **`neutral-kpi`**，且 `{{KPI3_CHANGE}}` **须带可核对金额**并标明仍未转正。详见 `references/report_style_guide_cn.md` / `references/financial_metrics.md`（KPI card direction）。  
**If `report_language=en`:** all free-text fields in `financial_analysis.json` must be **English**.  
**If `zh`:** Chinese prose as before.

Save `workspace/{Company}_{Date}/financial_analysis.json`.

---

## Phase 2.5: Revenue prediction (macro factor model)

Same formula as `references/prediction_factors.md`.  
**Macro geography:** Copy factor **labels and ordering** from `macro_factors.json` (which must already follow **Step 0D** + `agents/macro_scanner.md`). Do not reintroduce US-only names if `primary_operating_geography` is **`Greater_China`** or another non-US region.  
**Forecast horizon label:** Set **`predicted_fiscal_year_label`** to **`FY(latest_actual + 1)E`** where **`latest_actual`** is the fiscal year in `financial_data.json` → **`income_statement.current_year`** (e.g. FY2025 actual → **FY2026E**). This must match the Sankey **forecast** tab (Step 0C §4). Only use a later year (e.g. FY2027E) if you deliberately extend the horizon and keep **Sankey + waterfall + appendix** consistent.  
**If `en`:** use English for factor display names in `prediction_waterfall.json` where they are meant for the HTML table; numeric fields unchanged.

**Macro factor commentary (Section III):** `macro_factors.json` must include **`macro_factor_commentary`** (string, HTML-safe) written per **`agents/macro_scanner.md` Step 7b** — analyst-style explanation of **why** the six macro slots affect **this** company’s revenue/margins and how the rows sum to **`total_macro_adjustment_pct`** (bridge to the waterfall “宏观调整 / macro adjustment” bar). Phase 5 copies it into **`{{MACRO_FACTOR_COMMENTARY}}`** verbatim; do not invent a second narrative in HTML.
**Macro regime context:** `macro_factors.json` must include **`macro_regime_context`** from `agents/macro_scanner.md` Step 2b. Treat it as the canonical role/regime explanation for macro transmission (`sub_industry`, `company_role`, `sector_regime`, `primary_transmission_channels`, `sign_reversal_watchlist`). It is **not** a second β table and must not override the six-slot β model unless Agent 2 separately sets `beta_source: "adjusted"` with evidence.
**Macro factor table (`{{FACTOR_ROWS}}`) — final column is direction, not another pct:** The Section III factor table has a separate **`调整幅度（pct）`** column. Its final **`方向` / `Direction`** column must be a qualitative direction label: **正向 / 负向 / 中性** (`zh`) or **Positive / Negative / Neutral** (`en`). Do **not** put `adjustment_pct`, `factor_change_pct`, or any `+/-x%` numeric string in the final direction cell. Color the final direction cell with the existing table classes: positive → `<td class="metric-up">正向</td>` / `<td class="metric-up">Positive</td>`; negative → `<td class="metric-down">负向</td>` / `<td class="metric-down">Negative</td>`; neutral → `<td>中性</td>` / `<td>Neutral</td>` (no extra CSS class).

Save `prediction_waterfall.json`.

**Interim → model bridge (when material):** If **`latest_interim`** (or TTM read from filings) implies a **material** change in revenue run-rate vs. extrapolating from the last **full year** alone, Phase 2.5 may adjust **`company_specific_adjustment_pct`** / **`company_events_detail`** in `prediction_waterfall.json` and add **at most one clarifying sentence** to **`macro_factor_commentary`** (must remain consistent with `macro_factors.json` totals). This **feeds the same** **`predicted_revenue_growth_pct`** used for **Section III** waterfall and **Section IV** Sankey **forecast** tab — keep **`SANKEY_ANALYSIS_TEXT`** and methodology appendix aligned with that choice.

---

## Phase 2.6 — Macro adversarial QC（双审查员，并行）

在初稿 `prediction_waterfall.json` / `macro_factors.json` 定稿前，由两名**独立** QC 审查员挑战「基于数据的宏观与预测叙述」。Spawn 或顺序执行（Claude.ai 则顺序执行）：

### QC Macro — Peer A（模型与表内一致性）

**File:** `agents/qc_macro_peer_a.md`

```
Report language: {en|zh}
Primary operating geography: {同 Step 0D}
Sector / 行业: {与 Agent 2 一致}
Company: {company_name}
Inputs: workspace/{Company}_{Date}/macro_factors.json, prediction_waterfall.json, news_intel.json
Output path: workspace/{Company}_{Date}/qc_macro_peer_a.json
Follow agents/qc_macro_peer_a.md
```

### QC Macro — Peer B（情景与叙事压力）

**File:** `agents/qc_macro_peer_b.md`

```
Report language: {en|zh}
Primary operating geography: {同 Step 0D}
Sector / 行业: {与 Agent 2 一致}
Company: {company_name}
Inputs: 同上
Output path: workspace/{Company}_{Date}/qc_macro_peer_b.json
Follow agents/qc_macro_peer_b.md
```

**Wait for Peer A and Peer B to finish**（宏观 QC 的输出由 Phase 3.6 合并裁定，不在此步单独改 JSON）。

---

## Phase 3: Porter Five Forces

Use `references/porter_framework.md`. Three perspectives (~300 words each).  
**If `en`:** `porter_analysis.json` body text **English**. **If `zh`:** Chinese.

Save `porter_analysis.json`.

---

## Phase 3.5 — Porter adversarial QC（双审查员，并行）

对初稿 `porter_analysis.json` 进行独立挑战（供应商/买方/新进入者/替代品/竞争强度、主要竞争者是否遗漏等）。

### QC Porter — Peer A（分数与证据）

**File:** `agents/qc_porter_peer_a.md`

```
Report language: {en|zh}
Company: {company_name}
Inputs: workspace/{Company}_{Date}/porter_analysis.json, news_intel.json, financial_data.json
Output path: workspace/{Company}_{Date}/qc_porter_peer_a.json
Follow agents/qc_porter_peer_a.md
```

### QC Porter — Peer B（竞争者与市场动态）

**File:** `agents/qc_porter_peer_b.md`

```
Report language: {en|zh}
Company: {company_name}
Inputs: workspace/{Company}_{Date}/porter_analysis.json, news_intel.json
Output path: workspace/{Company}_{Date}/qc_porter_peer_b.json
Follow agents/qc_porter_peer_b.md
```

**Wait for Peer A and Peer B to finish.**

---

## Phase 3.6 — QC resolution merge（合议、更新 JSON）

**File:** `agents/qc_resolution_merge.md`

对 **Phase 2.6** 与 **Phase 3.5** 的全部质疑进行裁定：**质疑成立则修改**初稿对应字段；**不成立则保留**分析师原文。生成审计轨迹并写入合议摘要。

```
Report language: {en|zh}
Company: {company_name}
Inputs:
  - macro_factors.json, prediction_waterfall.json, news_intel.json
  - qc_macro_peer_a.json, qc_macro_peer_b.json
  - porter_analysis.json, financial_data.json (as needed)
  - qc_porter_peer_a.json, qc_porter_peer_b.json
Outputs:
  - workspace/{Company}_{Date}/qc_audit_trail.json
  - 原地更新 prediction_waterfall.json（含 qc_deliberation）
  - 原地更新 porter_analysis.json（含 qc_deliberation）
Follow agents/qc_resolution_merge.md
```

**After Phase 3.6:** `prediction_waterfall.json` 与 `porter_analysis.json` 即为**送审后修订版**；后续 Phase 4–5 必须以此为准。**第三节** HTML 中的免责框（概率性估计、β、φ）保持模板原文；合议补充说明写入 `qc_deliberation.methodology_note`，由 Phase 5 填入 `{{METHODOLOGY_DETAIL}}`（见 `agents/report_writer_*.md`）。

---

## Phase 4: Sankey data preparation

Build **`sankeyActualData`** from **`current_year`** P&L in `financial_data.json` and **`sankeyForecastData`** by scaling that structure with **`prediction_waterfall.json` → `predicted_revenue_growth_pct`** for **`FY(latest_actual + 1)E`** (see **Step 0C §4**). Fill **`{{SANKEY_YEAR_ACTUAL}}`** / **`{{SANKEY_YEAR_FORECAST}}`** accordingly.  
**If `en`:** Sankey node `name` strings **English** (Revenue, Cost of revenue, …). **If `zh`:** Chinese labels as in the Chinese template examples.

---

## Phase 5: Report generation (language branch)

### Phase 5 — `{{WATERFALL_JS_DATA}}` (Section III macro waterfall) — **P0 data contract**

The locked template’s D3 waterfall **appends a `%` sign** to every `start` / `end` / `value` number. Those numbers must be **percentage points** for the **revenue-growth bridge** (e.g. `-3.0` means **−3.0%**), **not** decimals like `0.03`, and **not** dollar amounts.

**Build `waterfallData` only from** `prediction_waterfall.json` growth fields, for example:

- **`baseline_growth_pct`** → first bridge step (after `start: 0`, typically `value`/`end` equal to this)
- **`macro_adjustment_pct`** → one **“宏观调整 / Macro adjustment”** bar (aggregate), **or** per-factor bars **only if** each bar’s `value` is still an **`adjustment_pct`-style percent point** consistent with `macro_factors.json`
- **`company_specific_adjustment_pct`**
- **`predicted_revenue_growth_pct`** → the **`type: "result"`** bar must reconcile so the cumulative growth shown matches this field (within rounding).

**Forbidden in `waterfallData`:** **`base_revenue`**, **`predicted_revenue`** (or any revenue in **millions/billions of currency**), Sankey `links[].value`, or any **dollar-denominated** step. Putting **`base_revenue` (e.g. 37296)** into `start`/`end`/`value` produces nonsense labels like **“37296.0%”** — that is a **unit error**, not a formatting tweak.

**Default shape:** Prefer **4–5 bars** (baseline → macro aggregate → company-specific → result), matching `agents/macro_scanner.md` “bridge table → macro bar” unless the orchestrator explicitly extends the waterfall.

### If `report_language = zh`

**File:** `agents/report_writer_cn.md`  
**Style:** `references/report_style_guide_cn.md`  
**Output:** `workspace/{Company}_{Date}/{Company}_Research_CN.html`  

**Reproducible / auditable structure:** Run the extractor **before** filling placeholders (do **not** copy skeleton from another company’s HTML in `workspace/`):

```bash
python3 scripts/extract_report_template.py --lang cn --sha256 \
  -o workspace/{Company}_{Date}/_locked_cn_skeleton.html
```

Then fill **only** `{{PLACEHOLDER}}` markers in the extracted file (or paste into your editor from the same extract) and save as `{Company}_Research_CN.html`. Do not alter the locked HTML/CSS/JS skeleton. **`{{SUMMARY_PARA_1}}`–`{{SUMMARY_PARA_4}}`** ← `financial_analysis.json` → `summary_para_1` … `summary_para_4`; `{{SUMMARY_PARA_2}}` must reflect `edge_insights.json` → `chosen_insight` / `summary_para_2_draft`. **`{{MACRO_FACTOR_COMMENTARY}}`** ← copy **verbatim** from `macro_factors.json` → `macro_factor_commentary`. **`{{PORTER_COMPANY_TEXT}}` / `{{PORTER_INDUSTRY_TEXT}}` / `{{PORTER_FORWARD_TEXT}}`** — use the **five-`<li>` unordered-list** format; **do not** use a **title-style** opening like **「力名（X/5）：」** (scores stay on radar and the score list). When dual-QC **changes a Porter score**, the matching `<li>` **should** follow the **sentence template** in `references/report_style_guide_cn.md` §波特五力 (**QC合议认为…，并将…评分由 a 调整为 b，原因是…**; then continue analysis). See `references/porter_framework.md` §Phase 5 HTML. **Post-processing caution:** Do **not** delete HTML comment lines that contain `-->` solely because they include illustrative `{{…}}` text — removing the only closing `-->` for a multi-line `<!--` will comment out the Porter/Appendix DOM (see `agents/report_writer_cn.md` 写作规范、`agents/report_validator.md` §5).
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

Then fill **only** placeholders and save as `{Company}_Research_EN.html`. **`{{SUMMARY_PARA_1}}`–`{{SUMMARY_PARA_4}}`** ← `financial_analysis.json` → `summary_para_1` … `summary_para_4`; `{{SUMMARY_PARA_2}}` must reflect `edge_insights.json` → `chosen_insight` / `summary_para_2_draft`. **`{{MACRO_FACTOR_COMMENTARY}}`** ← copy **verbatim** from `macro_factors.json` → `macro_factor_commentary`. Porter placeholders **`{{PORTER_COMPANY_TEXT}}` / `{{PORTER_INDUSTRY_TEXT}}` / `{{PORTER_FORWARD_TEXT}}`**: same **five-`<li>` `<ul>`** rules as Chinese — no **title-style** opening like **"Force (4/5):"**; when QC **changes a score**, use the **template** in `references/report_style_guide_en.md` §Porter Five Forces (**Dual-QC deliberation held that …, and adjusted … from *a* to *b*, because …**).

**Post-processing:** Same HTML comment rule as Chinese — do **not** strip lines that close a `<!--` block inside the Porter company panel (see `report_writer_en.md`). If you might remove a single-line comment that contains sample `{{...}}` text, apply the same **“only when sure / otherwise leave or reword”** rule as in the Chinese branch above.

- Header: **English legal name** in the first name line; **ticker only** on the second line (see `report_writer_en.md` rules).  
- Use `{{RATING_EN}}`, `{{CONFIDENCE_EN}}` per the English template.  
- Same structural rules as CN: placeholders only, no new classes/ids.

**Wait for Phase 5 to complete before Phase 5.5.**

---

## Phase 5.5: Final report data validation

**File:** `agents/final_report_data_validator.md`

This phase is the **final professional data validation** pass, not a layout check. Run it on the finished HTML **before** `report_validator.md`.

**Inputs:**

- HTML: `*_Research_CN.html` **or** `*_Research_EN.html`
- `financial_data.json`
- `financial_analysis.json`
- `macro_factors.json`
- `prediction_waterfall.json`
- `porter_analysis.json`
- `edge_insights.json`
- `news_intel.json`
- `qc_audit_trail.json`（若存在）

**Required behavior:**

- Recompute explicit formulas and quantity claims in the final report.
- Catch unit / magnitude mistakes (`亿` vs `B`, `%` vs `pp`, millions vs billions).
- Reconcile the Section III waterfall totals to `prediction_waterfall.json`.
- Reconcile Sankey labels and values to the actual P&L bridge; do **not** allow a residual `EBIT - net income` number to be mislabeled as only “interest and tax” when other non-operating items are present.
- Distinguish **net company-specific adjustment** from **single event sub-items** (e.g. a `+1.5%` Paramount component vs a `+1.0%` overall company-specific total).
- Detect stale values that survived QC in one place but not another.
- **Fix upstream JSON / wording first**, then sync the final HTML. Do not patch only the final HTML unless the issue is purely display formatting.

**Output:** `workspace/{Company}_{Date}/final_report_data_validation.json`

**Gate:** Do **not** enter Phase 6 until this audit has **0 CRITICAL** findings. Treat warnings about arithmetic, unit consistency, Sankey semantics, or GAAP/non-GAAP mixing as **pre-delivery fixes** as well.

**Wait for Phase 5.5 to complete before Phase 6.**

---

## Phase 6: Report validation

**File:** `agents/report_validator.md`

**Inputs:**

- HTML: `*_Research_CN.html` **or** `*_Research_EN.html` (whichever Phase 5 produced)  
- `financial_data.json`  
- `financial_analysis.json`
- `edge_insights.json`
- `macro_factors.json`
- `news_intel.json`
- `prediction_waterfall.json`  
- `final_report_data_validation.json`
- `qc_audit_trail.json`（若存在：核对合议与 HTML/JSON 无矛盾表述）

Run all checks; fix CRITICAL issues until zero remain. `report_validator.md` is the **delivery / structure / renderability** gate; it is **not** a substitute for the Phase 5.5 final data validation pass.  
Treat **checklist item 2** in `agents/report_validator.md` (KPI **`.kpi-value`**: leading **`-`** for negatives—no 「约负」/「净亏损约」/ **no 「约」 on Chinese KPI headline figures**; **`neutral-kpi`** card CSS must match the locked template—red bar + `kpi-down-bg`, not amber-only + white) as a **pre-delivery** fix: do not ship HTML that fails these even if labeled WARNING.
Treat **checklist item 7c** in `agents/report_validator.md` (`macro_regime_context`) as a **pre-delivery** fix: do not ship if role/regime fields are missing or if Section III / methodology contradicts the role-based transmission context.
Treat **checklist item 7d** in `agents/report_validator.md` (`edge_insights.json` and investment-summary paragraph 2) as a **pre-delivery** fix: do not ship if the edge insight is missing, generic, unsupported, or absent from `{{SUMMARY_PARA_2}}`.
Treat **checklist items 8b and 8c** in `agents/report_validator.md` as **pre-delivery** fixes: Section II metrics-table final column must be a qualitative verdict (e.g. `改善`, `恶化`, `权益缺口收窄`), and Section III factor-table final column must be direction (`正向` / `负向` / `中性`) with the required color class for positive/negative cells, never a repeated `+/-x%` numeric adjustment.
Treat **checklist item 9** in `agents/report_validator.md` (segment/region list must use percentages consistently with `segment_data`, or use amounts only for all items) as a **pre-delivery** fix: do not ship HTML with mixed formats.
Treat **checklist item 4** (Section III waterfall) in `agents/report_validator.md` as a **pre-delivery** fix: do not ship if **`waterfallData` uses revenue units** (see §4 “Waterfall — unit errors”) or if **`predicted_revenue_growth_pct`** does not match the **`result`** bar within tolerance.
Treat any open arithmetic / reconciliation failures from `final_report_data_validation.json` as **hard blockers** for delivery, even if the HTML still passes structural checks.
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
