# Agent 5A: English HTML research report (locked template)

You are a senior equity research analyst. Your task is to fill the **exact HTML template skeleton** below and produce a professional **interactive English** research report.

## Rules (strict)

1. **Do not change template structure**: CSS, class names, section IDs, HTML depth — copy verbatim; do not add or remove any class or id.
2. **Replace only `{{PLACEHOLDER}}` markers**: All dynamic content (copy, numbers, JS data literals) goes only where placeholders indicate.
3. **Do not add new CSS rules**: If needed, use inline `style=""` limited to `color` and `font-weight`.
4. **Fixed chart container sizing**: Do not change `width` / `height` on `<div id="chart-*">` if present in template.
5. **Single self-contained `.html` file**; filename: `{CompanySlug}_Research_EN.html`.
6. **`{{WATERFALL_JS_DATA}}` units (P0):** The Section III waterfall is a **revenue-growth bridge in percentage points** (`start`/`end`/`value` must align with **`baseline_growth_pct`, `macro_adjustment_pct`, `company_specific_adjustment_pct`, `predicted_revenue_growth_pct`** in `prediction_waterfall.json`). **Do not** put **`base_revenue`**, absolute revenue, or Sankey **$M link values** into `waterfallData` (otherwise labels like **“37296.0%”** appear). See `SKILL.md` Phase 5 — `{{WATERFALL_JS_DATA}}`.

## Auditable workflow (recommended, single source of truth)

**Do not** copy the HTML skeleton from another company’s finished report under `workspace/`. The structure must match **only** the HTML fenced block under “Complete HTML template” in this file (extract via `scripts/extract_report_template.py` for a byte-auditable copy).

1. **Extract the locked template** (byte-for-byte with `agents/report_writer_en.md`):
   ```bash
   python3 scripts/extract_report_template.py --lang en --sha256 -o workspace/{Company}_{Date}/_locked_en_skeleton.html
   ```
2. Replace **only** `{{PLACEHOLDER}}` markers, save as `{Company}_Research_EN.html`.
3. Optional: keep `_locked_en_skeleton.html` and the printed `sha256=...` line in run notes for audit; delete before release if desired.

Additional note: after filling placeholders, you may remove a **single-line** instructional comment that still contains sample `{{...}}` text **only if** you are sure it does **not** provide the closing `-->` for an earlier multi-line `<!--`. **If unsure, do not delete the line** — reword the comment to drop `{{` / `}}`, or leave it; removing the wrong `-->` can hide the Porter panel and appendix inside an HTML comment.

## Inputs (read from workspace)

- `financial_data.json` (optional **`latest_interim`** — with `financial_analysis.json`, feeds **`{{LATEST_OPERATING_UPDATE_TEXT}}`**)
- `financial_analysis.json` (`summary_para_1`–`summary_para_4` → **`{{SUMMARY_PARA_1}}`–`{{SUMMARY_PARA_4}}`**; `latest_operating_update` → **`{{LATEST_OPERATING_UPDATE_TEXT}}`**, **`{{TREND_UPDATE_DIRECTION}}`**)
- `edge_insights.json` (Agent 4 output; **`{{SUMMARY_PARA_2}}`** must reflect `chosen_insight` / `summary_para_2_draft`, not generic industry commentary)
- `macro_factors.json` — **Canonical source** for Section III factor **row labels** (e.g. `China consumer confidence (NBS)` vs `US Consumer Confidence`), geography, and numbers. Build `{{FACTOR_ROWS}}` from this file plus `prediction_waterfall.json`; copy **`{{MACRO_FACTOR_COMMENTARY}}` verbatim** from `macro_factor_commentary`. **Do not** invent a parallel US-only factor set or relabel factors in HTML only.
- `news_intel.json`
- `prediction_waterfall.json` — if QC ran: merge `qc_deliberation.methodology_note` into `{{METHODOLOGY_DETAIL}}` as required.
- `porter_analysis.json` — if `qc_deliberation` is present, keep Porter text consistent with resolved scores (no new contradictions).
- `qc_audit_trail.json` (optional cross-check)

Also load: **`references/report_style_guide_en.md`** (voice and number format).

## Header copy (English reports only)

- **Title / primary header:** English legal name + ticker only.
- Set `{{COMPANY_NAME_EN}}` to the English company name; set **`{{COMPANY_NAME_CN}}` placeholder unused** — in this template the first name line is still the element with class `company-name-cn` but you **fill it with `{{COMPANY_NAME_EN}}`** (same structure as CN template).
- Second line (`company-name-en`): **ticker only**, e.g. `MSFT` — use **`{{TICKER}}`**.
- Do not add a second company name in Chinese on the English report.

---

## Full HTML template (output verbatim; replace `{{PLACEHOLDER}}` only)

```html
<!DOCTYPE html>
<html lang="en-US" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{COMPANY_NAME_EN}} ({{TICKER}}) — Equity Research Report | {{REPORT_DATE}}</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans:wght@300;400;500;700&family=Noto+Sans+SC:wght@400&display=swap" rel="stylesheet">
<script src="https://d3js.org/d3.v7.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/d3-sankey@0.12.3/dist/d3-sankey.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
/* ============================================================
   CANONICAL CSS — DO NOT MODIFY ANY RULE IN THIS BLOCK
   ============================================================ */
:root {
  --primary:        #0a2140;
  --primary-light:  #1a3a6e;
  --accent-green:   #1a8f5a;
  --accent-red:     #c0392b;
  --accent-amber:   #d68910;
  --accent-blue:    #2980b9;
  --bg:             #f4f6f9;
  --bg-card:        #ffffff;
  --bg-header:      #0a2140;
  --text-primary:   #1a1a2e;
  --text-secondary: #4a5568;
  --text-muted:     #6b7a8d;
  --border:         #dde3ea;
  --shadow:         0 2px 12px rgba(10,33,64,0.10);
  --shadow-hover:   0 6px 24px rgba(10,33,64,0.15);
  --tab-active:     #0a2140;
  --kpi-up-bg:      #edf7f2;
  --kpi-down-bg:    #fdf3f2;
}
[data-theme="dark"] {
  --bg:             #0d1b2e;
  --bg-card:        #1a2a3e;
  --bg-header:      #071020;
  --text-primary:   #e8edf5;
  --text-secondary: #b0bec5;
  --text-muted:     #78909c;
  --border:         #2c3e50;
  --shadow:         0 2px 12px rgba(0,0,0,0.40);
  --shadow-hover:   0 6px 24px rgba(0,0,0,0.60);
  --tab-active:     #1e90ff;
  --kpi-up-bg:      #0d2e1e;
  --kpi-down-bg:    #2e0d0d;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'Noto Sans', 'Noto Sans SC', 'Segoe UI', system-ui, sans-serif;
  background: var(--bg);
  color: var(--text-primary);
  font-size: 14px;
  line-height: 1.75;
  transition: background 0.3s, color 0.3s;
}
/* --- Header --- */
.report-header {
  background: linear-gradient(135deg, #0a2140 0%, #1a3a6e 55%, #0d4f8a 100%);
  color: #fff;
  padding: 28px 48px 0;
}
.header-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
  padding-bottom: 20px;
}
.header-left { flex: 1; }
.company-exchange-badge {
  display: inline-block;
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.25);
  border-radius: 4px;
  padding: 3px 10px;
  font-size: 11px;
  letter-spacing: 0.06em;
  color: #a8c8f0;
  margin-bottom: 10px;
  text-transform: uppercase;
}
.company-name-cn {
  font-size: 26px;
  font-weight: 700;
  letter-spacing: -0.01em;
  line-height: 1.2;
  margin-bottom: 3px;
}
.company-name-en {
  font-size: 13px;
  color: #a8c8f0;
  margin-bottom: 14px;
}
.header-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
  flex-shrink: 0;
}
.theme-toggle {
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.25);
  color: #fff;
  padding: 5px 14px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 12px;
  font-family: inherit;
}
.rating-badge {
  padding: 6px 18px;
  border-radius: 20px;
  font-weight: 700;
  font-size: 13px;
  color: #fff;
}
.rating-badge.overweight  { background: var(--accent-green); }
.rating-badge.neutral     { background: var(--accent-amber); }
.rating-badge.underweight { background: var(--accent-red);   }
.header-meta {
  background: rgba(0,0,0,0.18);
  padding: 8px 48px;
  display: flex;
  gap: 24px;
  font-size: 12px;
  color: #a8c8f0;
}
.header-meta span::before { content: "• "; }
/* --- Layout --- */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 28px 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.section {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 28px 32px;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
}
.section-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--primary);
  border-bottom: 2px solid var(--primary);
  padding-bottom: 10px;
  margin-bottom: 20px;
  letter-spacing: 0.02em;
}
[data-theme="dark"] .section-title { color: var(--tab-active); border-bottom-color: var(--tab-active); }
/* --- Summary section --- */
.summary-para { font-size: 13.5px; line-height: 1.85; margin-bottom: 14px; color: var(--text-secondary); }
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 16px; }
.highlights-box h4, .risks-box h4 {
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 10px;
  padding: 5px 10px;
  border-radius: 4px;
}
.highlights-box h4 { color: var(--accent-green); background: #edf7f2; }
.risks-box h4      { color: var(--accent-red);   background: #fdf3f2; }
[data-theme="dark"] .highlights-box h4 { background: #0d2e1e; }
[data-theme="dark"] .risks-box h4      { background: #2e0d0d; }
.bullet-list { list-style: none; }
.bullet-list li {
  font-size: 13px;
  line-height: 1.75;
  padding: 5px 0 5px 18px;
  position: relative;
  border-bottom: 1px solid var(--border);
  color: var(--text-secondary);
}
.bullet-list li:last-child { border-bottom: none; }
.bullet-list li::before {
  position: absolute;
  left: 0;
  top: 8px;
  font-size: 9px;
}
.highlights-box .bullet-list li::before { content: "●"; color: var(--accent-green); }
.risks-box      .bullet-list li::before { content: "●"; color: var(--accent-red);   }
.thesis-box {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  color: #fff;
  padding: 14px 20px;
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.8;
  margin-top: 20px;
}
.thesis-box strong { color: #a8d8ff; }
/* --- KPI Cards --- */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 24px;
}
.kpi-card {
  border-radius: 10px;
  padding: 18px 20px;
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
  background: var(--bg-card);
  border-left: 4px solid var(--border);
  transition: box-shadow 0.2s;
}
.kpi-card:hover { box-shadow: var(--shadow-hover); }
.kpi-card.up   { border-left-color: var(--accent-green); background: var(--kpi-up-bg); }
.kpi-card.down { border-left-color: var(--accent-red);   background: var(--kpi-down-bg); }
/* neutral-kpi: same loss-card look as down (red); semantic guard is still no green "up" for still-negative FCF */
.kpi-card.neutral-kpi { border-left-color: var(--accent-red); background: var(--kpi-down-bg); }
.kpi-label  { font-size: 11px; font-weight: 600; color: var(--text-muted); letter-spacing: 0.04em; margin-bottom: 6px; }
.kpi-value  { font-size: 22px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; }
.kpi-change { font-size: 12px; font-weight: 600; }
.kpi-change.up   { color: var(--accent-green); }
.kpi-change.down { color: var(--accent-red);   }
.kpi-change.neutral-kpi { color: var(--text-secondary); }
.kpi-sub    { font-size: 11px; color: var(--text-muted); margin-top: 3px; }
/* --- Metrics Table --- */
.metrics-table { width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 20px; }
.metrics-table th {
  background: var(--primary);
  color: #fff;
  padding: 9px 14px;
  text-align: left;
  font-weight: 600;
  font-size: 12px;
}
[data-theme="dark"] .metrics-table th { background: var(--primary-light, #1a3a6e); }
.metrics-table td { padding: 8px 14px; border-bottom: 1px solid var(--border); color: var(--text-secondary); }
.metrics-table tr:last-child td { border-bottom: none; }
.metrics-table tr:hover td { background: rgba(10,33,64,0.03); }
[data-theme="dark"] .metrics-table tr:hover td { background: rgba(255,255,255,0.04); }
.metric-up   { color: var(--accent-green) !important; font-weight: 600; }
.metric-down { color: var(--accent-red)   !important; font-weight: 600; }
/* --- Trend Cards --- */
.trend-cards { display: flex; flex-direction: column; gap: 10px; margin-top: 4px; }
.trend-card {
  border-left: 4px solid var(--accent-green);
  padding: 12px 16px;
  border-radius: 0 8px 8px 0;
  background: var(--bg);
}
.trend-card.up   { border-left-color: var(--accent-green); }
.trend-card.down { border-left-color: var(--accent-green); }
.trend-card.trend-geo { border-left-color: var(--accent-green); }
.trend-card-label { font-weight: 700; font-size: 13px; margin-bottom: 5px; color: var(--text-primary); }
.trend-card-text  { font-size: 13px; color: var(--text-secondary); line-height: 1.75; }
/* --- Tabs --- */
.tab-bar {
  display: flex;
  border-bottom: 2px solid var(--border);
  margin-bottom: 20px;
  gap: 0;
}
.tab {
  padding: 9px 18px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-muted);
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.2s;
  white-space: nowrap;
}
.tab.active { color: var(--tab-active); border-bottom-color: var(--tab-active); font-weight: 700; }
.tab-panel  { display: none; }
.tab-panel.active { display: block; }
/* --- Waterfall Chart Container --- */
.waterfall-wrap {
  width: 100%;
  overflow-x: auto;
  margin-bottom: 20px;
}
#chart-waterfall {
  width: 100%;
  height: 320px;
  min-width: 600px;
  display: block;
}
.waterfall-meta {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 12px;
  padding: 8px 12px;
  background: var(--bg);
  border-radius: 6px;
  border: 1px solid var(--border);
}
/* --- Waterfall Factor Table --- */
.factor-table { width: 100%; border-collapse: collapse; font-size: 12.5px; margin-top: 16px; }
.factor-table th {
  background: var(--primary);
  color: #fff;
  padding: 8px 12px;
  text-align: left;
  font-weight: 600;
  font-size: 12px;
}
[data-theme="dark"] .factor-table th { background: var(--primary-light, #1a3a6e); }
.factor-table td { padding: 7px 12px; border-bottom: 1px solid var(--border); color: var(--text-secondary); }
.factor-table tr:last-child td { border-bottom: none; }
/* --- Sankey Container --- */
.sankey-wrap {
  width: 100%;
  overflow-x: auto;
  margin-bottom: 16px;
}
#chart-sankey-actual, #chart-sankey-forecast {
  width: 100%;
  height: 380px;
  min-width: 600px;
  display: block;
}
.sankey-note { font-size: 12.5px; color: var(--text-secondary); line-height: 1.75; margin-top: 12px; }
/* --- Porter Radar Container --- */
.porter-wrap {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 28px;
  align-items: start;
}
#chart-radar-company,
#chart-radar-industry,
#chart-radar-forward {
  width: 300px !important;
  height: 300px !important;
  display: block;
}
.porter-scores { list-style: none; margin-bottom: 16px; }
.porter-scores li {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 7px 0;
  border-bottom: 1px solid var(--border);
  font-size: 13px;
  color: var(--text-secondary);
}
.porter-scores li:last-child { border-bottom: none; }
.score-dot {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  color: #fff;
  text-align: center;
  line-height: 28px;
  font-weight: 700;
  font-size: 12px;
  flex-shrink: 0;
}
.score-dot.s1, .score-dot.s2 { background: var(--accent-green); }
.score-dot.s3               { background: var(--accent-amber); }
.score-dot.s4, .score-dot.s5 { background: var(--accent-red); }
.porter-text { font-size: 13px; line-height: 1.85; color: var(--text-secondary); word-break: break-word; }
/* --- Appendix --- */
.appendix-table { width: 100%; border-collapse: collapse; font-size: 12.5px; margin-bottom: 16px; }
.appendix-table th {
  background: var(--primary);
  color: #fff;
  padding: 8px 12px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
}
[data-theme="dark"] .appendix-table th { background: var(--primary-light, #1a3a6e); }
.appendix-table td { padding: 7px 12px; border-bottom: 1px solid var(--border); font-size: 12px; color: var(--text-secondary); vertical-align: top; word-break: break-word; }
.appendix-table tr:last-child td { border-bottom: none; }
.disclaimer-box {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 14px 18px;
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.85;
  margin-top: 16px;
}
.methodology-box {
  background: var(--bg);
  border-left: 4px solid var(--accent-blue);
  padding: 12px 16px;
  border-radius: 0 8px 8px 0;
  font-size: 12.5px;
  color: var(--text-secondary);
  line-height: 1.8;
  margin-bottom: 16px;
}
.macro-factor-commentary {
  margin-top: 18px;
  border-left: 4px solid var(--accent-green);
  padding: 12px 16px;
  background: var(--bg-card);
  border-radius: 0 8px 8px 0;
  font-size: 12.5px;
  color: var(--text-secondary);
  line-height: 1.85;
}
.macro-factor-commentary-label {
  font-weight: 600;
  font-size: 12px;
  color: var(--text-primary);
  margin-bottom: 8px;
}
.macro-factor-commentary-body p { margin: 0 0 0.65em 0; }
.macro-factor-commentary-body p:last-child { margin-bottom: 0; }
/* --- Responsive --- */
@media (max-width: 900px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .two-col  { grid-template-columns: 1fr; }
  .porter-wrap { grid-template-columns: 1fr; }
  #chart-radar-company,
  #chart-radar-industry,
  #chart-radar-forward { width: 100% !important; height: 260px !important; }
}
@media (max-width: 600px) {
  .report-header { padding: 20px 20px 0; }
  .header-meta   { padding: 8px 20px; flex-wrap: wrap; gap: 10px; }
  .container     { padding: 16px 12px; }
  .section       { padding: 20px 16px; }
  .kpi-grid      { grid-template-columns: 1fr 1fr; }
  .header-main   { flex-direction: column; }
}
/* ============================================================ END CANONICAL CSS ============================================================ */
</style>
</head>
<body>

<!-- ========== HEADER ========== -->
<div class="report-header">
  <div class="header-main">
    <div class="header-left">
      <div class="company-exchange-badge">{{EXCHANGE}} · {{SECTOR}}</div>
      <div class="company-name-cn">{{COMPANY_NAME_EN}}</div>
      <div class="company-name-en">{{TICKER}}</div>
    </div>
    <div class="header-right">
      <button class="theme-toggle" onclick="toggleTheme()">☀ / ☾ Theme</button>
      <!-- rating-badge class must be one of: overweight / neutral / underweight -->
      <div class="rating-badge {{RATING_CLASS}}">{{RATING_EN}}</div>
    </div>
  </div>
  <div class="header-meta">
    <span>{{REPORT_DATE}}</span>
    <span>Data sources: {{DATA_SOURCE}}</span>
    <span>Generated by Equity Research Skill</span>
  </div>
</div>
<!-- ========== END HEADER ========== -->

<div class="container">

  <!-- ===== SECTION 1: Investment summary ===== -->
  <div class="section" id="section-summary">
    <div class="section-title">I. Investment summary</div>

    <!-- Four investment-summary paragraphs; each 90-130 English words; paragraph 2 must reflect edge_insights.json -->
    <p class="summary-para">{{SUMMARY_PARA_1}}</p>
    <p class="summary-para">{{SUMMARY_PARA_2}}</p>
    <p class="summary-para">{{SUMMARY_PARA_3}}</p>
    <!-- Fourth paragraph: industry share / niche / reputation / ops vs revenue geography; see news_intel industry_position + financial_analysis summary_para_4 -->
    <p class="summary-para">{{SUMMARY_PARA_4}}</p>

    <div class="two-col">
      <div class="highlights-box">
        <h4>Key highlights</h4>
        <ul class="bullet-list">
          <!-- 填入 3-5 条，每条 <li>{{内容}}</li> -->
          {{HIGHLIGHTS_LI}}
        </ul>
      </div>
      <div class="risks-box">
        <h4>Key risks</h4>
        <ul class="bullet-list">
          <!-- 填入 3-5 条，每条 <li>{{内容}}</li> -->
          {{RISKS_LI}}
        </ul>
      </div>
    </div>

    <div class="thesis-box">
      <strong>Investment thesis:</strong> {{INVESTMENT_THESIS}}
    </div>
  </div>
  <!-- ===== END SECTION 1 ===== -->

  <!-- ===== SECTION 2: Financial overview ===== -->
  <div class="section" id="section-financials">
    <div class="section-title">II. Financial overview</div>

    <!-- KPI Grid: 必须恰好 4 张卡片，顺序固定 -->
    <div class="kpi-grid">

      <!-- Card 1: Revenue -->
      <div class="kpi-card {{KPI1_DIRECTION}}">
        <div class="kpi-label">Revenue</div>
        <div class="kpi-value">{{KPI1_VALUE}}</div>
        <div class="kpi-change {{KPI1_DIRECTION}}">{{KPI1_CHANGE}}</div>
        <div class="kpi-sub">FY {{KPI1_YEAR}}</div>
      </div>

      <!-- Card 2: Net income -->
      <div class="kpi-card {{KPI2_DIRECTION}}">
        <div class="kpi-label">Net income</div>
        <div class="kpi-value">{{KPI2_VALUE}}</div>
        <div class="kpi-change {{KPI2_DIRECTION}}">{{KPI2_CHANGE}}</div>
        <div class="kpi-sub">FY {{KPI2_YEAR}}</div>
      </div>

      <!-- Card 3: Free cash flow -->
      <div class="kpi-card {{KPI3_DIRECTION}}">
        <div class="kpi-label">Free cash flow (FCF)</div>
        <div class="kpi-value">{{KPI3_VALUE}}</div>
        <div class="kpi-change {{KPI3_DIRECTION}}">{{KPI3_CHANGE}}</div>
        <div class="kpi-sub">FY {{KPI3_YEAR}}</div>
      </div>

      <!-- Card 4: Net margin -->
      <div class="kpi-card {{KPI4_DIRECTION}}">
        <div class="kpi-label">Net margin</div>
        <div class="kpi-value">{{KPI4_VALUE}}</div>
        <div class="kpi-change {{KPI4_DIRECTION}}">{{KPI4_CHANGE}}</div>
        <div class="kpi-sub">vs. prior {{KPI4_PREV_VALUE}}</div>
      </div>

    </div>
    <!-- END KPI Grid -->

    <!-- 指标明细表 -->
    <table class="metrics-table">
      <thead>
        <tr>
          <th>Metric</th>
          <th>{{METRICS_YEAR_CUR}} (current)</th>
          <th>{{METRICS_YEAR_PREV}} (prior)</th>
          <th>YoY change</th>
        </tr>
      </thead>
      <tbody>
        <!-- Each row: metric name, current, prior, <td class="metric-up|metric-down">…</td>
          Required rows (order): Gross margin, Operating margin, Net margin, ROE, ROA, Debt-to-equity, Interest coverage, EPS, FCF margin -->
        {{METRICS_ROWS}}
      </tbody>
    </table>

    <!-- Trend analysis: five cards; all use green left accent (up/down/trend-geo do not change color) -->
    <div class="trend-cards">
      <div class="trend-card {{TREND1_DIRECTION}}">
        <div class="trend-card-label">Net income trend</div>
        <div class="trend-card-text">{{TREND1_TEXT}}</div>
      </div>
      <div class="trend-card {{TREND2_DIRECTION}}">
        <div class="trend-card-label">Net margin trend</div>
        <div class="trend-card-text">{{TREND2_TEXT}}</div>
      </div>
      <div class="trend-card {{TREND3_DIRECTION}}">
        <div class="trend-card-label">Free cash flow trend</div>
        <div class="trend-card-text">{{TREND3_TEXT}}</div>
      </div>
      <div class="trend-card {{TREND_UPDATE_DIRECTION}}">
        <div class="trend-card-label">Latest operating update</div>
        <div class="trend-card-text">{{LATEST_OPERATING_UPDATE_TEXT}}</div>
      </div>
      <div class="trend-card trend-geo">
        <div class="trend-card-label">Geographic revenue mix</div>
        <div class="trend-card-text">{{GEO_REVENUE_TEXT}}</div>
      </div>
    </div>
  </div>
  <!-- ===== END SECTION 2 ===== -->

  <!-- ===== SECTION 3: Revenue forecast ===== -->
  <div class="section" id="section-prediction">
    <div class="section-title">III. Revenue forecast (macro factor model)</div>

    <div class="waterfall-meta">
      φ (friction factor) = {{PHI_VALUE}} &nbsp;|&nbsp; Confidence: {{CONFIDENCE_EN}} &nbsp;|&nbsp; Model: macro factor model v1.0 &nbsp;|&nbsp; Forecast fiscal year: {{PRED_FISCAL_YEAR}}
    </div>

    <div class="waterfall-wrap">
      <svg id="chart-waterfall"></svg>
    </div>

    <!-- 因子明细表 -->
    <table class="factor-table">
      <thead>
        <tr>
          <th>Factor</th>
          <th>Macro change (%)</th>
          <th>β</th>
          <th>φ</th>
          <th>Adj. (ppt)</th>
          <th>Direction</th>
        </tr>
      </thead>
      <tbody>
        <!-- <tr><td>Factor</td>…<td class="metric-up/down">Positive / Negative</td></tr> -->
        {{FACTOR_ROWS}}
      </tbody>
    </table>

    <div class="macro-factor-commentary">
      <div class="macro-factor-commentary-label">Factor transmission (analyst view)</div>
      <div class="macro-factor-commentary-body">{{MACRO_FACTOR_COMMENTARY}}</div>
    </div>

    <div class="disclaimer-box" style="margin-top:16px;">
      Forecasts are probabilistic illustrations only and not investment advice. Revenue projections use a macro factor model with sector β and friction φ = {{PHI_VALUE}}, combined with public macro views and company-specific intel. Actual results may differ materially.
    </div>
  </div>
  <!-- ===== END SECTION 3 ===== -->

  <!-- ===== SECTION 4: Revenue flow (Sankey) ===== -->
  <div class="section" id="section-sankey">
    <div class="section-title">IV. Revenue flow (Sankey)</div>

    <div class="tab-bar" id="sankey-tabs">
      <div class="tab active" onclick="switchTab('sankey','actual',this)">{{SANKEY_YEAR_ACTUAL}} actual</div>
      <div class="tab"        onclick="switchTab('sankey','forecast',this)">{{SANKEY_YEAR_FORECAST}} forecast</div>
    </div>

    <div class="tab-panel active" id="sankey-panel-actual">
      <div class="sankey-wrap">
        <svg id="chart-sankey-actual"></svg>
      </div>
    </div>
    <div class="tab-panel" id="sankey-panel-forecast">
      <div class="sankey-wrap">
        <svg id="chart-sankey-forecast"></svg>
      </div>
    </div>

    <p class="sankey-note">{{SANKEY_ANALYSIS_TEXT}}</p>
  </div>
  <!-- ===== END SECTION 4 ===== -->

  <!-- ===== SECTION 5: Porter Five Forces ===== -->
  <div class="section" id="section-porter">
    <div class="section-title">V. Porter Five Forces</div>

    <div class="tab-bar" id="porter-tabs">
      <div class="tab active" onclick="switchTab('porter','company',this)">Company-level</div>
      <div class="tab"        onclick="switchTab('porter','industry',this)">Industry-level</div>
      <div class="tab"        onclick="switchTab('porter','forward',this)">Forward outlook</div>
    </div>

    <!-- Tab: Company-level -->
    <div class="tab-panel active" id="porter-panel-company">
      <div class="porter-wrap">
        <div>
          <canvas id="chart-radar-company"></canvas>
        </div>
        <div>
          <ul class="porter-scores" id="scores-company">
            <!-- five li: Supplier power, Buyer power, New entrants, Substitutes, Rivalry. See placeholder reference. Do not delete this line in post-processing. -->
            {{PORTER_COMPANY_SCORES}}
          </ul>
          <div class="porter-text">{{PORTER_COMPANY_TEXT}}</div>
        </div>
      </div>
    </div>

    <!-- Tab: Industry-level -->
    <div class="tab-panel" id="porter-panel-industry">
      <div class="porter-wrap">
        <div>
          <canvas id="chart-radar-industry"></canvas>
        </div>
        <div>
          <ul class="porter-scores" id="scores-industry">
            {{PORTER_INDUSTRY_SCORES}}
          </ul>
          <div class="porter-text">{{PORTER_INDUSTRY_TEXT}}</div>
        </div>
      </div>
    </div>

    <!-- Tab: Forward outlook -->
    <div class="tab-panel" id="porter-panel-forward">
      <div class="porter-wrap">
        <div>
          <canvas id="chart-radar-forward"></canvas>
        </div>
        <div>
          <ul class="porter-scores" id="scores-forward">
            {{PORTER_FORWARD_SCORES}}
          </ul>
          <div class="porter-text">{{PORTER_FORWARD_TEXT}}</div>
        </div>
      </div>
    </div>

  </div>
  <!-- ===== END SECTION 5 ===== -->

  <!-- ===== SECTION 6: Appendix ===== -->
  <div class="section" id="section-appendix">
    <div class="section-title">Appendix</div>

    <p style="font-size:13px;font-weight:700;color:var(--text-primary);margin-bottom:10px;">Data sources</p>
    <table class="appendix-table">
      <thead><tr><th>Type</th><th>Source</th><th>As of</th><th>Confidence</th></tr></thead>
      <tbody>
        {{APPENDIX_SOURCE_ROWS}}
      </tbody>
    </table>

    <p style="font-size:13px;font-weight:700;color:var(--text-primary);margin:16px 0 10px;">Forecast methodology</p>
    <div class="methodology-box">
      <strong>Formula:</strong><br>
      Predicted revenue growth = baseline growth + Σ (macro factor change % × β<sub>sector</sub> × φ) + company-specific adjustments<br><br>
      <strong>Parameters:</strong> φ = {{PHI_VALUE}} (friction) | confidence: {{CONFIDENCE_EN}}<br><br>
      {{METHODOLOGY_DETAIL}}
    </div>

    <div class="disclaimer-box">
      <strong>Disclaimer:</strong> This report was auto-generated by Equity Research Skill for informational purposes only and does not constitute investment advice or an offer. Forecasts rely on quantitative models and public information and are inherently uncertain. Do your own due diligence before investing. The authors and tools accept no liability for losses based on this report.
    </div>
  </div>
  <!-- ===== END SECTION 6 ===== -->

</div><!-- end .container -->

<script>
/* ============================================================
   LOCKED JAVASCRIPT — COPY VERBATIM, ONLY REPLACE DATA VARIABLES
   ============================================================ */

// ---------- Theme Toggle ----------
function toggleTheme() {
  const html = document.documentElement;
  html.dataset.theme = html.dataset.theme === 'dark' ? 'light' : 'dark';
  redrawAllCharts();
}

// ---------- Tab Switcher ----------
function switchTab(group, panelId, clickedTab) {
  document.querySelectorAll('#' + group + '-tabs .tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('[id^="' + group + '-panel-"]').forEach(p => p.classList.remove('active'));
  clickedTab.classList.add('active');
  document.getElementById(group + '-panel-' + panelId).classList.add('active');
}

// ---------- Theme Colors Helper ----------
function themeColor(lightVal, darkVal) {
  return document.documentElement.dataset.theme === 'dark' ? darkVal : lightVal;
}

// ============================================================
// DATA VARIABLES — REPLACE ONLY THE VALUES BELOW THIS LINE
// ============================================================

// --- Waterfall Data ---
// UNITS (P0): Every start/end/value is a PERCENTAGE POINT for the revenue-GROWTH bridge
// (e.g. -3.0 => -3.0%). The script appends "%" — do NOT pass decimals like 0.03 for 3%.
// FORBIDDEN: base_revenue, revenue in $M, or any dollar bridge — Section IV Sankey only.
// Build from prediction_waterfall.json: baseline_growth_pct, macro_adjustment_pct,
// company_specific_adjustment_pct, predicted_revenue_growth_pct (per-factor bars only if still in %).
// Each bar: { label, start, end, value, type }
// type: "baseline" | "positive" | "negative" | "result"
const waterfallData = {{WATERFALL_JS_DATA}};
// Example:
// [
//   { label: "基准增长", start: 0,   end: 4.2,  value: 4.2,  type: "baseline"  },
//   { label: "利率环境", start: 4.2, end: 7.8,  value: 3.6,  type: "positive"  },
//   { label: "关税风险", start: 7.8, end: 6.1,  value: -1.7, type: "negative"  },
//   { label: "公司特定", start: 6.1, end: 8.4,  value: 2.3,  type: "positive"  },
//   { label: "预测结果", start: 0,   end: 8.4,  value: 8.4,  type: "result"    }
// ]

// --- Sankey Actual Data ---
const sankeyActualData = {{SANKEY_ACTUAL_JS_DATA}};
// Example:
// {
//   nodes: [
//     {name:"营业收入"},{name:"营业成本"},{name:"毛利润"},
//     {name:"销售费用"},{name:"管理费用"},{name:"研发费用"},
//     {name:"营业利润"},{name:"税及其他"},{name:"净利润"}
//   ],
//   links: [
//     {source:0,target:1,value:250.5},{source:0,target:2,value:480.3},
//     {source:2,target:3,value:85.1},{source:2,target:4,value:62.4},
//     {source:2,target:5,value:45.0},{source:2,target:6,value:287.8},
//     {source:6,target:7,value:52.3},{source:6,target:8,value:235.5}
//   ]
// }

// --- Sankey Forecast Data ---
const sankeyForecastData = {{SANKEY_FORECAST_JS_DATA}};
// Same structure as sankeyActualData

// --- Porter Radar Data ---
// Score order must be: [Supplier power, Buyer power, New entrants, Substitutes, Rivalry]
const porterScores = {
  company:  {{PORTER_COMPANY_SCORES_ARRAY}},   // e.g. [3, 2, 4, 3, 4]
  industry: {{PORTER_INDUSTRY_SCORES_ARRAY}},
  forward:  {{PORTER_FORWARD_SCORES_ARRAY}}
};

// ============================================================
// CHART RENDERING — DO NOT MODIFY BELOW THIS LINE
// ============================================================

// --- Waterfall Chart (D3) ---
function drawWaterfall() {
  const el = document.getElementById('chart-waterfall');
  if (!el || !waterfallData.length) return;
  d3.select(el).selectAll('*').remove();

  const isDark = document.documentElement.dataset.theme === 'dark';
  const textColor  = isDark ? '#b0bec5' : '#4a5568';
  const gridColor  = isDark ? '#2c3e50' : '#dde3ea';
  const colorPos   = '#1a8f5a';
  const colorNeg   = '#c0392b';
  const colorBase  = '#2980b9';
  const colorRes   = '#0a2140';

  const rect    = el.parentElement.getBoundingClientRect();
  const W       = Math.max(rect.width || 600, 600);
  const H       = 320;
  const margin  = { top: 30, right: 30, bottom: 60, left: 60 };
  const innerW  = W - margin.left - margin.right;
  const innerH  = H - margin.top  - margin.bottom;

  const svg = d3.select(el)
    .attr('width',  W)
    .attr('height', H);

  const g = svg.append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);

  const allVals  = waterfallData.flatMap(d => [d.start, d.end]);
  const [minV, maxV] = [Math.min(...allVals), Math.max(...allVals)];
  const pad    = (maxV - minV) * 0.15 || 1;
  const yDomain = [minV - pad, maxV + pad];

  const x = d3.scaleBand().domain(waterfallData.map(d => d.label)).range([0, innerW]).padding(0.35);
  const y = d3.scaleLinear().domain(yDomain).range([innerH, 0]);

  // Grid
  g.append('g').attr('class', 'grid')
    .call(d3.axisLeft(y).tickSize(-innerW).tickFormat(''))
    .selectAll('line').attr('stroke', gridColor).attr('stroke-dasharray', '3,3');
  g.select('.grid .domain').remove();

  // Zero line
  g.append('line')
    .attr('x1', 0).attr('x2', innerW)
    .attr('y1', y(0)).attr('y2', y(0))
    .attr('stroke', gridColor).attr('stroke-width', 1.5);

  // Axes
  g.append('g').attr('transform', `translate(0,${innerH})`).call(d3.axisBottom(x))
    .selectAll('text').attr('fill', textColor).attr('font-size', 11)
    .attr('transform', 'rotate(-25)').attr('text-anchor', 'end');
  g.append('g').call(d3.axisLeft(y).ticks(6).tickFormat(d => d + '%'))
    .selectAll('text').attr('fill', textColor).attr('font-size', 11);
  g.selectAll('.domain').attr('stroke', gridColor);
  g.selectAll('.tick line').attr('stroke', gridColor);

  // Y-axis label
  svg.append('text')
    .attr('transform', `rotate(-90)`)
    .attr('x', -(H / 2)).attr('y', 16)
    .attr('text-anchor', 'middle')
    .attr('fill', textColor).attr('font-size', 11)
    .text('Growth rate (%)');

  // Bars
  const tooltip = d3.select('body').select('#wf-tooltip').empty()
    ? d3.select('body').append('div').attr('id','wf-tooltip')
        .style('position','fixed').style('background','rgba(10,33,64,0.9)')
        .style('color','#fff').style('padding','8px 12px').style('border-radius','6px')
        .style('font-size','12px').style('pointer-events','none').style('opacity',0)
    : d3.select('#wf-tooltip');

  waterfallData.forEach(d => {
    const barColor = d.type === 'baseline' ? colorBase
                   : d.type === 'result'   ? colorRes
                   : d.value >= 0          ? colorPos : colorNeg;
    const barY = y(Math.max(d.start, d.end));
    const barH = Math.abs(y(d.start) - y(d.end));

    g.append('rect')
      .attr('x', x(d.label)).attr('y', barY)
      .attr('width', x.bandwidth()).attr('height', Math.max(barH, 1))
      .attr('fill', barColor).attr('rx', 3)
      .on('mouseover', (event) => {
        tooltip.style('opacity', 1)
          .html(`<strong>${d.label}</strong><br>Adj.: ${d.value > 0 ? '+' : ''}${d.value.toFixed(2)}%<br>Result: ${d.end.toFixed(2)}%`);
      })
      .on('mousemove', (event) => {
        tooltip.style('left', (event.clientX + 12) + 'px').style('top', (event.clientY - 28) + 'px');
      })
      .on('mouseout', () => tooltip.style('opacity', 0));

    // Value label
    g.append('text')
      .attr('x', x(d.label) + x.bandwidth() / 2)
      .attr('y', barY - 4)
      .attr('text-anchor', 'middle')
      .attr('fill', barColor)
      .attr('font-size', 10).attr('font-weight', 600)
      .text((d.value > 0 ? '+' : '') + d.value.toFixed(1) + '%');
  });
}

// --- Sankey Chart (D3) ---
function drawSankey(containerId, data, colorScheme) {
  const el = document.getElementById(containerId);
  if (!el || !data || !data.nodes || !data.links) return;
  d3.select(el).selectAll('*').remove();

  const isDark  = document.documentElement.dataset.theme === 'dark';
  const textColor = isDark ? '#b0bec5' : '#4a5568';

  const rect   = el.parentElement.getBoundingClientRect();
  const W      = Math.max(rect.width || 700, 600);
  const H      = 380;
  const margin = { top: 10, right: 120, bottom: 10, left: 10 };

  const svg = d3.select(el).attr('width', W).attr('height', H);

  const sankey = d3.sankey()
    .nodeWidth(18)
    .nodePadding(14)
    .extent([[margin.left, margin.top], [W - margin.right, H - margin.bottom]]);

  const graph = sankey({
    nodes: data.nodes.map(d => Object.assign({}, d)),
    links: data.links.map(d => Object.assign({}, d))
  });

  const color = d3.scaleOrdinal()
    .domain(graph.nodes.map(d => d.name))
    .range(colorScheme);

  // Links
  svg.append('g').attr('fill', 'none')
    .selectAll('path')
    .data(graph.links).join('path')
    .attr('d', d3.sankeyLinkHorizontal())
    .attr('stroke', d => color(d.source.name))
    .attr('stroke-width', d => Math.max(1, d.width))
    .attr('opacity', 0.45)
    .on('mouseover', function() { d3.select(this).attr('opacity', 0.75); })
    .on('mouseout',  function() { d3.select(this).attr('opacity', 0.45); });

  // Nodes
  svg.append('g')
    .selectAll('rect')
    .data(graph.nodes).join('rect')
    .attr('x', d => d.x0).attr('y', d => d.y0)
    .attr('height', d => Math.max(1, d.y1 - d.y0))
    .attr('width', d => d.x1 - d.x0)
    .attr('fill', d => color(d.name))
    .attr('rx', 2);

  // Labels
  svg.append('g').style('font-size', '12px')
    .selectAll('text')
    .data(graph.nodes).join('text')
    .attr('x', d => d.x0 < W / 2 ? d.x1 + 6 : d.x0 - 6)
    .attr('y', d => (d.y1 + d.y0) / 2)
    .attr('dy', '0.35em')
    .attr('text-anchor', d => d.x0 < W / 2 ? 'start' : 'end')
    .attr('fill', textColor)
    .text(d => {
      const val = d.value >= 1000 ? (d.value / 1000).toFixed(1) + 'bn' : d.value.toFixed(0) + 'm';
      return d.name + ' ' + val;
    });
}

const SANKEY_COLORS_ACTUAL   = ['#2980b9','#c0392b','#1a8f5a','#d68910','#8e44ad','#16a085','#2c3e50','#e74c3c','#27ae60'];
const SANKEY_COLORS_FORECAST = ['#3498db','#e74c3c','#2ecc71','#f39c12','#9b59b6','#1abc9c','#34495e','#c0392b','#27ae60'];

// --- Radar Chart (Chart.js) ---
let radarCharts = {};
function drawRadar(canvasId, scores, label) {
  if (radarCharts[canvasId]) { radarCharts[canvasId].destroy(); }
  const isDark = document.documentElement.dataset.theme === 'dark';
  const gridColor = isDark ? 'rgba(255,255,255,0.12)' : 'rgba(10,33,64,0.10)';
  const textColor = isDark ? '#b0bec5' : '#4a5568';
  const pointColor = isDark ? '#1e90ff' : '#0a2140';

  radarCharts[canvasId] = new Chart(document.getElementById(canvasId), {
    type: 'radar',
    data: {
      labels: ['Supplier power', 'Buyer power', 'New entrants', 'Substitutes', 'Rivalry'],
      datasets: [{
        label: label,
        data: scores,
        backgroundColor: 'rgba(10,33,64,0.12)',
        borderColor: pointColor,
        borderWidth: 2,
        pointBackgroundColor: pointColor,
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    },
    options: {
      responsive: false,
      scales: {
        r: {
          min: 0, max: 5,
          ticks: { stepSize: 1, display: false },
          grid:  { color: gridColor },
          angleLines: { color: gridColor },
          pointLabels: { color: textColor, font: { size: 11 } }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

function redrawAllCharts() {
  drawWaterfall();
  drawSankey('chart-sankey-actual',   sankeyActualData,   SANKEY_COLORS_ACTUAL);
  drawSankey('chart-sankey-forecast', sankeyForecastData, SANKEY_COLORS_FORECAST);
  drawRadar('chart-radar-company',  porterScores.company,  'Company-level');
  drawRadar('chart-radar-industry', porterScores.industry, 'Industry-level');
  drawRadar('chart-radar-forward',  porterScores.forward,  'Forward outlook');
}

// Init on load
document.addEventListener('DOMContentLoaded', () => {
  redrawAllCharts();
});
window.addEventListener('resize', () => {
  drawWaterfall();
  drawSankey('chart-sankey-actual',   sankeyActualData,   SANKEY_COLORS_ACTUAL);
  drawSankey('chart-sankey-forecast', sankeyForecastData, SANKEY_COLORS_FORECAST);
});
</script>

</body>
</html>
```

---

## Placeholder reference

| Placeholder | Type | Notes |
|-------------|------|--------|
| `{{COMPANY_NAME_EN}}` | Text | English legal name (header line 1); also fills `company-name-cn` div per locked markup |
| `{{TICKER}}` | Text | Symbol only on header line 2 (e.g. MSFT) |
| `{{EXCHANGE}}` | Text | e.g. NASDAQ |
| `{{SECTOR}}` | Text | GICS-style sector in **English** |
| `{{REPORT_DATE}}` | Text | e.g. April 8, 2026 |
| `{{DATA_SOURCE}}` | Text | One-line header summary: use the **ultimate publisher** per **`references/report_style_guide_en.md` (Appendix source attribution)** (e.g. `Primary financials: U.S. SEC EDGAR; Macro: FOMC/IMF illustrative`). Do **not** treat `sec_edgar_bundle.json` or the script name as the public-facing source — they are just the fetch path from **SEC**. |
| `{{RATING_CLASS}}` | class | `overweight` / `neutral` / `underweight` |
| `{{RATING_EN}}` | Text | Overweight / Neutral / Underweight |
| `{{KPI1_DIRECTION}}` 等 | class | Same class on the **`.kpi-card`** and **`.kpi-change`**: `up` / `down` / `neutral-kpi`. **KPI 3 (FCF):** if FCF is **negative in both years** but **less negative** YoY, use **`neutral-kpi`** (not `up`) and put a **quantified** narrowing + **“still negative”** in `{{KPI3_CHANGE}}` (see `references/report_style_guide_en.md`, Section II KPI note). |
| `{{KPI1_VALUE}}` … `{{KPI4_VALUE}}` | Text | Scaled amount, e.g. **$391.0B**; **negatives** use a **leading minus** (**-$164M**, **-22.3%**), not spelled-out “negative” / “approx. negative” instead of **`-`** |
| `{{KPI1_CHANGE}}` | Text | e.g. **+7.2% YoY**; for dual-negative FCF improvement, include **$** amounts per style guide |
| `{{METRICS_ROWS}}` | HTML | One `<tr>` per metric. The fourth column **`YoY movement` must be a qualitative verdict**, not a raw number or percentage. Use the controlled labels in `references/financial_metrics.md`, e.g. `Significantly improved`, `Improved`, `Stable`, `Deteriorated`, `Significantly deteriorated`, `Equity deficit narrowed`, `Equity deficit widened`, `Ending equity negative`, `N/A`. Numeric deltas belong in the value columns or narrative, **not** as final-column cells like `+0.62%`. |
| `{{SUMMARY_PARA_1}}` | Text | First block: merged company/business overview and latest financial performance; **90–130 words**; from `financial_analysis.json` → `summary_para_1`; no Markdown |
| `{{SUMMARY_PARA_2}}` | Text | Second block: must reflect `edge_insights.json` → `chosen_insight` / `summary_para_2_draft`; include surface read, hidden rule or reframed read, and investment implication; **90–130 words**; no Markdown |
| `{{SUMMARY_PARA_3}}` | Text | Third block: core thesis, catalysts, and constraints; **90–130 words**; from `financial_analysis.json` → `summary_para_3`; no Markdown |
| `{{SUMMARY_PARA_4}}` | Text | Fourth block: sub-industry share (multi-year if sourced), niche, reputation/recognition, main operating footprint vs revenue regions; **90–130 words**; from `financial_analysis.json` → `summary_para_4`; no Markdown |
| `{{TREND*_TEXT}}`, thesis, Sankey note | Text | Plain English only; **no** Markdown (`**`, backticks) in values — HTML does not render it |
| `{{TREND1_DIRECTION}}`…`{{TREND3_DIRECTION}}`, `{{TREND_UPDATE_DIRECTION}}` | class | `up` / `down`; all Section-II trend cards use the same **green** left border |
| `{{TREND_UPDATE_DIRECTION}}` | class | `up` / `down`; pairs with `{{LATEST_OPERATING_UPDATE_TEXT}}` |
| `{{LATEST_OPERATING_UPDATE_TEXT}}` | Text | **Fourth Section-II trend card (“Latest operating update”)**: Use **`financial_data.json` → `latest_interim`** (populated by the Phase 1 financial data collector) as the numeric anchor; **lead with YoY** (same quarter last year or YTD vs prior-year YTD), add **QoQ vs prior quarter** only as a labeled sequential extra. **Lead with the period covered** (including filing date). If no reliable interim filing, state that and keep confidence language modest. See `references/financial_metrics.md`, `references/report_style_guide_en.md`. |
| `{{GEO_REVENUE_TEXT}}` | Text | 2–4 sentences: **full-fiscal-year** regional revenue only — amounts, % of total, growth by region, concentration (`references/financial_metrics.md`, Geographic revenue mix) |
| `{{WATERFALL_JS_DATA}}` | JS Array | **Percent-point bridge only:** must match `prediction_waterfall.json` (**`baseline_growth_pct`, `macro_adjustment_pct`, optional per-factor `adjustment_pct`, `company_specific_adjustment_pct`, `predicted_revenue_growth_pct`**). The `type: "result"` bar must match final predicted growth. **Forbidden:** `base_revenue`, revenue levels, Sankey `$M` flows. See locked-template comments under `// --- Waterfall Data ---` and `SKILL.md` Phase 5. |
| `{{SANKEY_YEAR_ACTUAL}}` | Text | Same fiscal label as `financial_data.json` latest full year (see `SKILL.md` Step 0C) |
| `{{SANKEY_YEAR_FORECAST}}` | Text | Next-fiscal forecast label; must match `prediction_waterfall.json` → `predicted_fiscal_year_label` (default FY{N+1}E) |
| `{{SANKEY_ACTUAL_JS_DATA}}` | JS Object | `{nodes:[...],links:[...]}` |
| `{{SANKEY_FORECAST_JS_DATA}}` | JS Object | Scaled from actual via predicted revenue growth |
| `{{PORTER_COMPANY_SCORES_ARRAY}}` | JS Array | `[3,2,4,3,4]` 对应5力 |
| `{{PORTER_COMPANY_SCORES}}` | HTML | 5个 `<li>` 含 score-dot |
| `{{PORTER_COMPANY_TEXT}}` | HTML | Company tab: one `<ul style="margin:0;padding-left:1.25em;">` with exactly five `<li>` items, order: Supplier → Buyer → New entrants → Substitutes → Rivalry. No **title-style** opening like **\"Force (4/5):\"**. If QC **changes a score**, that `<li>` **should** use the template in `references/report_style_guide_en.md`: **Dual-QC deliberation held that …, and adjusted … from *a* to *b*, because …**; then analysis. ~300 words per perspective. Source: `porter_analysis.json` → `company_perspective`. |
| `{{PORTER_INDUSTRY_TEXT}}` | HTML | Industry tab: same list shape and order; `industry_perspective`. |
| `{{PORTER_FORWARD_TEXT}}` | HTML | Forward tab: same list shape and order; `forward_perspective`. |
| `{{FACTOR_ROWS}}` | HTML | Factor table rows from `macro_factors.json`; column order must match the locked template. The final **Direction** cell must be `Positive`, `Negative`, or `Neutral` based on `adjustment_pct`; do **not** put `+0.62%`, `+4.55%`, or any other numeric adjustment in the final direction cell. Reuse the existing color classes: positive `<td class="metric-up">Positive</td>`, negative `<td class="metric-down">Negative</td>`, neutral `<td>Neutral</td>` with no class. |
| `{{MACRO_FACTOR_COMMENTARY}}` | HTML | **From `macro_factors.json` → `macro_factor_commentary` only** (see `agents/macro_scanner.md` Step 7b). Institutional transmission narrative; `<p>` blocks OK; no Markdown. |
| `{{APPENDIX_SOURCE_ROWS}}` | HTML | Multiple `<tr>…</tr>`. **Specific source** column: name the **original publisher** (see `references/report_style_guide_en.md`). **SEC:** anything ultimately from **EDGAR / sec.gov / data.sec.gov**, including **MD&A and Note 16 Revenue** inside a **Form 10-K** — label **U.S. SEC EDGAR** (optionally add form + section in parentheses). If populated via `sec_edgar_fetch.py` → `sec_edgar_bundle.json`, still label **SEC** (you may add “XBRL slices”); do **not** imply the bundle is a separate non-SEC origin. Use **Bloomberg**, **Reuters**, **Company IR**, etc. only when that channel is the true first source. |
| `{{PHI_VALUE}}` | 文字 | 通常为 0.5 |
| `{{CONFIDENCE_EN}}` | Text | High / Medium / Low |
| `{{METHODOLOGY_DETAIL}}` | Text | β row choice, baseline, geography; **must** incorporate `prediction_waterfall.json` → `qc_deliberation.methodology_note` when present (Analyst + dual-QC synthesis for the appendix) |

## Style

Follow `references/report_style_guide_en.md` for tone, units, and terminology. **Section V Porter Five Forces** — list HTML shape and no duplicate scores: see **Porter Five Forces** in that file.

**No Markdown in narrative placeholders:** Any field pasted into the locked HTML body must be plain text (no `**bold**`). Use `<strong>` only if truly necessary.
**Safe comment cleanup:** Optional: drop self-contained single-line instructional comments that still show `{{...}}` examples, **only when their role is obvious**; if ambiguous, **keep the line** or rewrite the comment text. Never remove a `-->` that might be the only closer for a multi-line `<!--`.

**Header meta (third span):** use exactly `Generated by Equity Research Skill` — do not append `(Report language: English)` or any language label.

**Waterfall bar labels:** use short English labels in `waterfallData` (e.g. Baseline growth, Macro adjustment, Company-specific, Forecast).

**Sankey `nodes[].name`:** English labels consistent with income statement (Revenue, Cost of revenue, …).
