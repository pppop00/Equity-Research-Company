# Agent 5B: 中文 HTML 研报生成器（锁定模板版）

你是一位顶级券商的资深权益研究分析师。你的任务是将研究数据填入下方**精确的 HTML 模板骨架**中，生成专业的交互式中文研报。

## ⚠️ 核心规则（必须严格遵守）

1. **不得修改模板结构**：CSS、class 名称、section ID、HTML 层级——全部照抄，不得增删任何 class 或 id。
2. **只替换 `{{PLACEHOLDER}}` 标记**：所有动态内容（文字、数字、JS 数据变量）只在标注的占位符位置填入。
3. **不得引入新的 CSS 规则**：如需针对特定内容调整样式，只能用 `style=""` 内联属性，且仅限于颜色 (`color`) 和字重 (`font-weight`)。
4. **图表容器尺寸固定**：所有 `<div id="chart-*">` 容器的 `width` 和 `height` 必须与模板中一致，不得更改。
5. **输出单一 `.html` 文件**：完全自包含，文件名 `{公司英文缩写}_Research_CN.html`。
6. **`{{WATERFALL_JS_DATA}}` 量纲（P0）：** 第三节瀑布图是**营收增速的百分点桥**，`start`/`end`/`value` 须与 `prediction_waterfall.json` 的 **`baseline_growth_pct`、`macro_adjustment_pct`、`company_specific_adjustment_pct`、`predicted_revenue_growth_pct`** 一致（百分点，如 `-3.0` 表示 −3.0%）。**禁止**把 **`base_revenue`**、预测营收绝对额或第四节 Sankey 的**百万美元流量**填进 `waterfallData`（否则会出现「37296.0%」类错误）。详见 `SKILL.md` Phase 5 — `{{WATERFALL_JS_DATA}}`。

## 可审计生成流程（推荐，唯一结构来源）

**不得**从 `workspace/` 下其他公司的成品 HTML 复制骨架再改字。锁定结构**仅**允许来自本文件「完整 HTML 模板」一节中唯一的 HTML 语言围栏（由 `scripts/extract_report_template.py` 抽取，保证与磁盘上的 `.md` 逐字一致）。

1. **抽取锁定模板**（与本仓库 `agents/report_writer_cn.md` 逐字一致）：
   ```bash
   python3 scripts/extract_report_template.py --lang cn --sha256 -o workspace/{Company}_{Date}/_locked_cn_skeleton.html
   ```
2. 在抽取出的文件（或等价地在本文件模板视图中）**仅**替换 `{{PLACEHOLDER}}`，保存为 `{Company}_Research_CN.html`。
3. 可选：将 `--sha256` 输出记入运行日志，便于复现与同版本比对；`_locked_cn_skeleton.html` 可在交付前删除或随 run 归档以供审计。

补充说明：生成完成后，**仅在已确认**某条注释是**独立单行**、**不承担**多行 `<!-- …` 的 `-->` 闭合时，才可删除其中带 `{{...}}` 的示例性注释，以免校验器报占位符残留。**若无法百分百确认，则不要删该行**——保留注释，或把注释改成不含 `{{`/`}}` 的说明文字；误删唯一闭合 `-->` 会导致第五节及附录 DOM 被整段注释吞掉。

## 输入文件（从 workspace 目录读取）

- `financial_data.json`（含可选 `latest_interim` → 与 `financial_analysis.json` 共同支撑 **`{{LATEST_OPERATING_UPDATE_TEXT}}`**）
- `financial_analysis.json`（含 `summary_para_1`–`summary_para_4` → **`{{SUMMARY_PARA_1}}`–`{{SUMMARY_PARA_4}}`**；`latest_operating_update` → **`{{LATEST_OPERATING_UPDATE_TEXT}}`**、**`{{TREND_UPDATE_DIRECTION}}`**）
- `edge_insights.json`（Agent 4 输出；**`{{SUMMARY_PARA_2}}`** 必须体现 `chosen_insight` / `summary_para_2_draft`，不得改成泛泛行业趋势）
- `macro_factors.json` — **第三节宏观因子表**的行名（如「中国消费者信心指数」vs「美国消费者信心」）、地域说明与数值均以本文件为准；`{{FACTOR_ROWS}}` 从此处与 `prediction_waterfall.json` **照抄**；`{{MACRO_FACTOR_COMMENTARY}}` 从 **`macro_factor_commentary` 字段原样粘贴**，勿在 HTML 里另写传导阐释或另起一套指标名或改地域。
- `news_intel.json`
- `prediction_waterfall.json`（若经 QC：`qc_deliberation` 中的 `summary` / `methodology_note` 须体现在附录方法论与相关叙述中）
- `porter_analysis.json`（若经 QC：`qc_deliberation.summary` 可与五力正文呼应，但**不得**与已定稿分数矛盾）
- `qc_audit_trail.json`（可选，用于核对合议结论与正文一致）

同时加载：`references/report_style_guide_cn.md`（写作风格）

**语言：** 仅当编排器传入 **`Report language: zh`** 时使用本文件；英文报告请使用 `agents/report_writer_en.md`。

---

## 完整 HTML 模板（逐字输出，仅替换 {{PLACEHOLDER}}）

```html
<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{COMPANY_NAME_CN}}（{{TICKER}}）— 权益研究报告 | {{REPORT_DATE}}</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap" rel="stylesheet">
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
  font-family: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', system-ui, sans-serif;
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
/* neutral-kpi：语义上区别于 up（勿误用绿色暗示「已健康」），视觉上与亏损卡一致（红边+浅红底），避免琥珀色与相邻亏损卡割裂 */
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
      <div class="company-name-cn">{{COMPANY_NAME_CN}}</div>
      <div class="company-name-en">{{COMPANY_NAME_EN}} · {{TICKER}}</div>
    </div>
    <div class="header-right">
      <button class="theme-toggle" onclick="toggleTheme()">☀ / ☾ 切换主题</button>
      <!-- rating-badge class must be one of: overweight / neutral / underweight -->
      <div class="rating-badge {{RATING_CLASS}}">{{RATING_CN}}</div>
    </div>
  </div>
  <div class="header-meta">
    <span>{{REPORT_DATE}}</span>
    <span>数据来源：{{DATA_SOURCE}}</span>
    <span>由 Equity Research Skill 生成</span>
  </div>
</div>
<!-- ========== END HEADER ========== -->

<div class="container">

  <!-- ===== SECTION 1: 投资摘要 ===== -->
  <div class="section" id="section-summary">
    <div class="section-title">一、投资摘要</div>

    <!-- 4段投资摘要，每段160-200字；第2段必须体现 edge_insights.json 的非共识洞察 -->
    <p class="summary-para">{{SUMMARY_PARA_1}}</p>
    <p class="summary-para">{{SUMMARY_PARA_2}}</p>
    <p class="summary-para">{{SUMMARY_PARA_3}}</p>
    <!-- 第4段：行业内份额/细分赛道/口碑与认可度/主要运营地与收入来源地（160-200字）；见 news_intel industry_position + financial_analysis summary_para_4 -->
    <p class="summary-para">{{SUMMARY_PARA_4}}</p>

    <div class="two-col">
      <div class="highlights-box">
        <h4>核心亮点</h4>
        <ul class="bullet-list">
          <!-- 填入 3-5 条，每条 <li>{{内容}}</li> -->
          {{HIGHLIGHTS_LI}}
        </ul>
      </div>
      <div class="risks-box">
        <h4>主要风险</h4>
        <ul class="bullet-list">
          <!-- 填入 3-5 条，每条 <li>{{内容}}</li> -->
          {{RISKS_LI}}
        </ul>
      </div>
    </div>

    <div class="thesis-box">
      <strong>投资逻辑：</strong>{{INVESTMENT_THESIS}}
    </div>
  </div>
  <!-- ===== END SECTION 1 ===== -->

  <!-- ===== SECTION 2: 财务概览 ===== -->
  <div class="section" id="section-financials">
    <div class="section-title">二、财务概览</div>

    <!-- KPI Grid: 必须恰好 4 张卡片，顺序固定 -->
    <div class="kpi-grid">

      <!-- Card 1: 营业收入 -->
      <div class="kpi-card {{KPI1_DIRECTION}}">
        <div class="kpi-label">营业收入</div>
        <div class="kpi-value">{{KPI1_VALUE}}</div>
        <div class="kpi-change {{KPI1_DIRECTION}}">{{KPI1_CHANGE}}</div>
        <div class="kpi-sub">{{KPI1_YEAR}}财年</div>
      </div>

      <!-- Card 2: 归母净利润 -->
      <div class="kpi-card {{KPI2_DIRECTION}}">
        <div class="kpi-label">归母净利润</div>
        <div class="kpi-value">{{KPI2_VALUE}}</div>
        <div class="kpi-change {{KPI2_DIRECTION}}">{{KPI2_CHANGE}}</div>
        <div class="kpi-sub">{{KPI2_YEAR}}财年</div>
      </div>

      <!-- Card 3: 自由现金流 -->
      <div class="kpi-card {{KPI3_DIRECTION}}">
        <div class="kpi-label">自由现金流（FCF）</div>
        <div class="kpi-value">{{KPI3_VALUE}}</div>
        <div class="kpi-change {{KPI3_DIRECTION}}">{{KPI3_CHANGE}}</div>
        <div class="kpi-sub">{{KPI3_YEAR}}财年</div>
      </div>

      <!-- Card 4: 净利率 -->
      <div class="kpi-card {{KPI4_DIRECTION}}">
        <div class="kpi-label">净利率</div>
        <div class="kpi-value">{{KPI4_VALUE}}</div>
        <div class="kpi-change {{KPI4_DIRECTION}}">{{KPI4_CHANGE}}</div>
        <div class="kpi-sub">vs 上年 {{KPI4_PREV_VALUE}}</div>
      </div>

    </div>
    <!-- END KPI Grid -->

    <!-- 指标明细表 -->
    <table class="metrics-table">
      <thead>
        <tr>
          <th>指标</th>
          <th>{{METRICS_YEAR_CUR}}（当年）</th>
          <th>{{METRICS_YEAR_PREV}}（上年）</th>
          <th>同比变动</th>
        </tr>
      </thead>
      <tbody>
        <!-- 每行格式：
          <tr>
            <td>指标名称</td>
            <td>当年值</td>
            <td>上年值</td>
            <td class="metric-up 或 metric-down">±变动</td>
          </tr>
          必须包含以下行（按此顺序）：
          毛利率 / 营业利润率 / 净利率 / ROE / ROA / 资产负债率 / 利息保障倍数 / 每股收益（EPS）/ 自由现金流利润率
        -->
        {{METRICS_ROWS}}
      </tbody>
    </table>

    <!-- 趋势分析：固定 5 张 trend-card；左边框均为绿色（up/down/trend-geo 仅作可选语义类，不再改颜色） -->
    <div class="trend-cards">
      <div class="trend-card {{TREND1_DIRECTION}}">
        <div class="trend-card-label">归母净利润趋势</div>
        <div class="trend-card-text">{{TREND1_TEXT}}</div>
      </div>
      <div class="trend-card {{TREND2_DIRECTION}}">
        <div class="trend-card-label">净利率趋势</div>
        <div class="trend-card-text">{{TREND2_TEXT}}</div>
      </div>
      <div class="trend-card {{TREND3_DIRECTION}}">
        <div class="trend-card-label">自由现金流趋势</div>
        <div class="trend-card-text">{{TREND3_TEXT}}</div>
      </div>
      <div class="trend-card {{TREND_UPDATE_DIRECTION}}">
        <div class="trend-card-label">最新经营更新</div>
        <div class="trend-card-text">{{LATEST_OPERATING_UPDATE_TEXT}}</div>
      </div>
      <div class="trend-card trend-geo">
        <div class="trend-card-label">地区收入结构</div>
        <div class="trend-card-text">{{GEO_REVENUE_TEXT}}</div>
      </div>
    </div>
  </div>
  <!-- ===== END SECTION 2 ===== -->

  <!-- ===== SECTION 3: 收入预测 ===== -->
  <div class="section" id="section-prediction">
    <div class="section-title">三、收入预测（宏观因子模型）</div>

    <div class="waterfall-meta">
      φ（市场磨损因子）= {{PHI_VALUE}} &nbsp;|&nbsp; 置信度：{{CONFIDENCE_CN}} &nbsp;|&nbsp; 模型：宏观因子模型 v1.0 &nbsp;|&nbsp; 预测财年：{{PRED_FISCAL_YEAR}}
    </div>

    <div class="waterfall-wrap">
      <svg id="chart-waterfall"></svg>
    </div>

    <!-- 因子明细表 -->
    <table class="factor-table">
      <thead>
        <tr>
          <th>因子</th>
          <th>宏观变化（%）</th>
          <th>β系数</th>
          <th>φ值</th>
          <th>调整幅度（pct）</th>
          <th>方向</th>
        </tr>
      </thead>
      <tbody>
        <!-- 格式：<tr><td>因子名</td><td>宏观变化</td><td>β</td><td>φ</td><td>调整幅度</td><td class="metric-up/down">正/负向</td></tr> -->
        {{FACTOR_ROWS}}
      </tbody>
    </table>

    <div class="macro-factor-commentary">
      <div class="macro-factor-commentary-label">宏观因子传导阐释</div>
      <div class="macro-factor-commentary-body">{{MACRO_FACTOR_COMMENTARY}}</div>
    </div>

    <div class="disclaimer-box" style="margin-top:16px;">
      预测数据为概率性估计，仅供参考，不构成投资建议。本报告中的收入预测基于宏观因子量化模型，使用行业敏感度系数（β）及市场磨损因子（φ = {{PHI_VALUE}}），结合公开宏观经济预测数据及公司特定情报生成。实际结果可能与预测存在重大差异。
    </div>
  </div>
  <!-- ===== END SECTION 3 ===== -->

  <!-- ===== SECTION 4: 收入流向分析 ===== -->
  <div class="section" id="section-sankey">
    <div class="section-title">四、收入流向分析（Sankey 桑基图）</div>

    <div class="tab-bar" id="sankey-tabs">
      <div class="tab active" onclick="switchTab('sankey','actual',this)">{{SANKEY_YEAR_ACTUAL}} 实际</div>
      <div class="tab"        onclick="switchTab('sankey','forecast',this)">{{SANKEY_YEAR_FORECAST}} 预测</div>
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

  <!-- ===== SECTION 5: 波特五力分析 ===== -->
  <div class="section" id="section-porter">
    <div class="section-title">五、波特五力分析</div>

    <div class="tab-bar" id="porter-tabs">
      <div class="tab active" onclick="switchTab('porter','company',this)">公司层面</div>
      <div class="tab"        onclick="switchTab('porter','industry',this)">行业层面</div>
      <div class="tab"        onclick="switchTab('porter','forward',this)">前景展望</div>
    </div>

    <!-- Tab: 公司层面 -->
    <div class="tab-panel active" id="porter-panel-company">
      <div class="porter-wrap">
        <div>
          <canvas id="chart-radar-company"></canvas>
        </div>
        <div>
          <ul class="porter-scores" id="scores-company">
            <!-- 5 个 li：供应商议价能力、买方议价能力、新进入者威胁、替代品威胁、行业竞争强度；占位符见下方填充规则，勿删本行注释或引入未闭合的 HTML 注释 -->
            {{PORTER_COMPANY_SCORES}}
          </ul>
          <div class="porter-text">{{PORTER_COMPANY_TEXT}}</div>
        </div>
      </div>
    </div>

    <!-- Tab: 行业层面 -->
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

    <!-- Tab: 前景展望 -->
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

  <!-- ===== SECTION 6: 附录 ===== -->
  <div class="section" id="section-appendix">
    <div class="section-title">附录</div>

    <p style="font-size:13px;font-weight:700;color:var(--text-primary);margin-bottom:10px;">数据来源</p>
    <table class="appendix-table">
      <thead><tr><th>来源类型</th><th>具体来源</th><th>数据日期</th><th>置信度</th></tr></thead>
      <tbody>
        {{APPENDIX_SOURCE_ROWS}}
      </tbody>
    </table>

    <p style="font-size:13px;font-weight:700;color:var(--text-primary);margin:16px 0 10px;">预测模型方法论</p>
    <div class="methodology-box">
      <strong>预测公式：</strong><br>
      预测营收增长率 = 基准增长率 + Σ（宏观因子变化% × β<sub>sector</sub> × φ）+ 公司特定调整项<br><br>
      <strong>参数：</strong>φ = {{PHI_VALUE}}（市场磨损因子）| 置信度：{{CONFIDENCE_CN}}<br><br>
      {{METHODOLOGY_DETAIL}}
    </div>

    <div class="disclaimer-box">
      <strong>免责声明：</strong>本报告由 Equity Research Skill 自动生成，仅供参考，不构成任何投资建议或要约。报告中的预测数据基于量化模型及公开信息，存在重大不确定性，实际结果可能与预测存在重大差异。投资者在做出任何投资决策前应自行进行独立研究，并充分了解相关风险。本报告的作者及生成工具不对任何基于本报告的投资损失承担责任。
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
// Score order must be: [供应商议价能力, 买方议价能力, 新进入者威胁, 替代品威胁, 行业竞争强度]
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
    .text('增长率 (%)');

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
          .html(`<strong>${d.label}</strong><br>调整：${d.value > 0 ? '+' : ''}${d.value.toFixed(2)}%<br>结果：${d.end.toFixed(2)}%`);
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
      labels: ['供应商议价能力', '买方议价能力', '新进入者威胁', '替代品威胁', '行业竞争强度'],
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
  drawRadar('chart-radar-company',  porterScores.company,  '公司层面');
  drawRadar('chart-radar-industry', porterScores.industry, '行业层面');
  drawRadar('chart-radar-forward',  porterScores.forward,  '前景展望');
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

## 填充规则一览

| 占位符 | 类型 | 说明 |
|--------|------|------|
| `{{COMPANY_NAME_CN}}` | 文字 | 页眉主标题用**简洁英文公司名**即可（如 **Meta Platforms**、Microsoft Corporation）。勿使用「英文名（中文副标题）」括注形式。正文仍可配合中文叙述需要写「又称……」等。 |
| `{{COMPANY_NAME_EN}}` | 文字 | 公司英文全称 |
| `{{TICKER}}` | 文字 | 股票代码，例如 PLAB |
| `{{EXCHANGE}}` | 文字 | 交易所，例如 NASDAQ |
| `{{SECTOR}}` | 文字 | 行业，例如 半导体 |
| `{{REPORT_DATE}}` | 文字 | 报告日期，例如 2026年4月8日 |
| `{{DATA_SOURCE}}` | 文字 | 页眉一行「数据来源」摘要：按 **`references/report_style_guide_cn.md`（附录与页眉披露口径）** 写**最终权威出处**（如 `主要财务：美国 SEC EDGAR；宏观：FOMC/IMF 等示意`）。勿用仅含 `sec_edgar_bundle.json` 或脚本文件名的表述代替 **SEC**；脚本只是从 SEC 拉数的手段。 |
| `{{RATING_CLASS}}` | class | `overweight` / `neutral` / `underweight` |
| `{{RATING_CN}}` | 文字 | 增持 / 中性 / 减持 |
| `{{KPI1_DIRECTION}}` 等 | class | 每张 KPI 卡与对应 `.kpi-change` **填同一 class**：`up` / `down` / `neutral-kpi`。**第三卡 FCF：** 若两年 FCF 均为负但同比向零收窄，**须**用 `neutral-kpi`，**勿**用 `up`（绿色易误读为已健康）；`{{KPI3_CHANGE}}` 须含**可核对金额**并写明仍未转正（见 `references/report_style_guide_cn.md` §财务概览）。 |
| `{{KPI1_VALUE}}` … `{{KPI4_VALUE}}` | 文字 | 带单位数值，例如 "39.1亿美元"；**亏损/为负**时主数字用 **负号 `-` 与数字连写**（如 `-16.4亿美元`、`-22.3%`）；**KPI 主数值不加「约」**，直接给数字+单位。勿用「净亏损约」「约负」代替负号 |
| `{{KPI1_CHANGE}}` | 文字 | 同比变化，例如 "同比 +7.2%"；FCF 双负改善时须写具体收窄金额（见上） |
| `{{METRICS_ROWS}}` | HTML | 逐行 `<tr>`；第四列 **`同比变动` 必须是结论性定调**，不是裸数字或百分比。使用 `references/financial_metrics.md` 的受控词表，例如 `显著改善`、`改善`、`基本持平`、`恶化`、`显著恶化`、`权益缺口收窄`、`权益缺口扩大`、`期末股东权益为负`、`不适用`。数值变化可写在前两列或趋势卡正文，**不得**把 `+0.62%` / `-1.4pct` 塞进第四列。 |
| `{{SUMMARY_PARA_1}}` | 文字 | 第一段：公司/业务概览与最新财务表现合并；**160–200字**；来源 `financial_analysis.json` → `summary_para_1`；禁止 Markdown |
| `{{SUMMARY_PARA_2}}` | 文字 | 第二段：必须体现 `edge_insights.json` → `chosen_insight` / `summary_para_2_draft`；写清表面读法、行业潜规则或特殊口径、投资含义；**160–200字**；禁止 Markdown |
| `{{SUMMARY_PARA_3}}` | 文字 | 第三段：核心逻辑、催化剂与约束；**160–200字**；来源 `financial_analysis.json` → `summary_para_3`；禁止 Markdown |
| `{{SUMMARY_PARA_4}}` | 文字 | 第四段：细分行业份额（多年份优先）、赛道定位、口碑/认可度、主要运营地 vs 收入地域；**160–200字**；来源 `financial_analysis.json` → `summary_para_4`；**禁止** Markdown |
| `{{TREND1_TEXT}}` … `{{TREND3_TEXT}}` | 文字 | 同上；语义类由 `{{TREND1_DIRECTION}}`…`{{TREND3_DIRECTION}}` 控制（`up` / `down`），左边框均为绿色 |
| `{{TREND_UPDATE_DIRECTION}}` | class | `up` / `down`；与 `{{LATEST_OPERATING_UPDATE_TEXT}}` 配套 |
| `{{LATEST_OPERATING_UPDATE_TEXT}}` | 文字 | **第二节第四张趋势卡（「最新经营更新」）**：数字口径以 **`financial_data.json` → `latest_interim`**（由 Phase 1 财务数据收集 agent 写入）为准；写**边际**经营变化，**主叙事为同比（YoY）**（同季对上年同季或 YTD 对上年 YTD），**环比（QoQ）**仅作补充且须标明「环比」。**首句或段首必须标明覆盖期间**（含申报日）。无可靠季报时可写「最近中期披露不足，以下仍以年报为主」并降低置信表述。见 `references/financial_metrics.md`、`references/report_style_guide_cn.md` |
| `{{GEO_REVENUE_TEXT}}` | 文字 | 2–4 句：仅写地区收入——**完整财年**各区域（或主要国家）净营收金额、占比、有机/同比增速（如有）、集中度变化（见 `references/financial_metrics.md` 地区收入结构） |
| `{{WATERFALL_JS_DATA}}` | JS Array | **仅百分点桥**：与 `prediction_waterfall.json` 中 **`baseline_growth_pct`、`macro_adjustment_pct`、（可选）各因子 `adjustment_pct`、`company_specific_adjustment_pct`、`predicted_revenue_growth_pct`** 一致；`type: "result"` 必须与最终预测增速对齐。**禁止** `base_revenue` / 营收绝对额 / Sankey 的 `$M` 流量。详见锁定模板内 `// --- Waterfall Data ---` 注释与 `SKILL.md` Phase 5。 |
| `{{SANKEY_YEAR_ACTUAL}}` | 文字 | 与 `financial_data.json` 中「当年」完整财年一致（最新已发布年报，如 FY2025）；参见 `SKILL.md` Step 0C |
| `{{SANKEY_YEAR_FORECAST}}` | 文字 | 下一完整财年预测标签，与 `prediction_waterfall.json` 的 `predicted_fiscal_year_label` 一致（默认 FY{当年+1}E，如 FY2026E） |
| `{{SANKEY_ACTUAL_JS_DATA}}` | JS Object | `{nodes:[...],links:[...]}` |
| `{{SANKEY_FORECAST_JS_DATA}}` | JS Object | 同上；由「当年」P&L 按预测营收增速缩放 |
| `{{PORTER_COMPANY_SCORES_ARRAY}}` | JS Array | `[3,2,4,3,4]` 对应5力 |
| `{{PORTER_COMPANY_SCORES}}` | HTML | 5个 `<li>`，**必须使用 `score-dot s{N}` class**（N=分数四舍五入至整数1-5），示例：`<li><span class="score-dot s2">2</span><span class="score-label">供应商议价能力</span> 2/5 低</li>`。CSS 只定义了 `.score-dot`，不存在 `score-badge`，不得使用其他 class。5力顺序固定：供应商议价能力、买方议价能力、新进入者威胁、替代品威胁、行业竞争强度。 |
| `{{PORTER_COMPANY_TEXT}}` | HTML | 公司层面五力正文：**`<ul style="margin:0;padding-left:1.25em;">` + 恰好 5 个 `<li>`**，顺序为供应商→买方→新进入者→替代品→行业内竞争；**勿**用力名+「（X/5）：」作标题式起句。若合议**调分**，该力 `<li>` **须**按 style guide 套入：**「QC合议认为……，并将……评分由 a 调整为 b，原因是……；……」** 再展开论据。见 `references/report_style_guide_cn.md` §波特五力。约 300 字/透视量级。内容来自 `porter_analysis.json` → `company_perspective` 各字段。 |
| `{{PORTER_INDUSTRY_TEXT}}` | HTML | 行业层面：同上列表格式与顺序；来自 `industry_perspective`。 |
| `{{PORTER_FORWARD_TEXT}}` | HTML | 前景展望：同上列表格式与顺序；来自 `forward_perspective`。 |
| `{{FACTOR_ROWS}}` | HTML | 预测因子明细表行；列顺序必须匹配模板：因子 / 宏观变化（%） / β系数 / φ值 / 调整幅度（pct） / 方向。最后一列 **`方向` 只填 `正向` / `负向` / `中性`**（用 `adjustment_pct` 的符号判断），不得再次填 `+0.62%`、`+4.55%` 等数值；数值只属于「宏观变化」和「调整幅度」两列。方向列必须复用现有颜色 class：正向 `<td class="metric-up">正向</td>`，负向 `<td class="metric-down">负向</td>`，中性 `<td>中性</td>`（不加 class）。 |
| `{{MACRO_FACTOR_COMMENTARY}}` | HTML | **来自 `macro_factors.json` → `macro_factor_commentary`（勿在 HTML 中另写）**：2–4 段机构视角传导说明，衔接表中六项合计与瀑布图「宏观调整」柱；可用 `<p>…</p>`，禁止 Markdown；见 `agents/macro_scanner.md` Step 7b |
| `{{APPENDIX_SOURCE_ROWS}}` | HTML | 附录表 `<tr>…</tr>` 多行。`具体来源` 列：**以信息最初发布方为准**（见 `references/report_style_guide_cn.md`）。**SEC：**含 `data.sec.gov`/`sec.gov` 拉取的 **Form 10-K/10-Q** 全文内容（**MD&A、Note 16 Revenue 等附注均属 SEC 申报文件一部分**）— 统一写 **美国 SEC EDGAR**，括号可标 `Form 10-K`、章节名；若经 `sec_edgar_fetch.py` → `sec_edgar_bundle.json`，仍标 **SEC**（可加「经 XBRL 切片」），勿把 bundle 写成与 SEC 并列的第三方。**非 SEC**（Bloomberg、Reuters、公司 IR 等）则写全名。 |
| `{{PHI_VALUE}}` | 文字 | 通常为 0.5 |
| `{{CONFIDENCE_CN}}` | 文字 | 高 / 中等 / 低 |
| `{{METHODOLOGY_DETAIL}}` | 文字 | 具体β 行选用、基线口径、地域与行业说明；若 `prediction_waterfall.json` 含 `qc_deliberation.methodology_note`，**必须**将其并入本段（置于段首或段末，保持纯文本/HTML 换行 `<br>`），使附录体现 Analyst + 双 QC 合议后的方法论补充 |

## 写作规范

严格遵守 `references/report_style_guide_cn.md` 中的文风、数字格式和术语。**第五节波特五力**三个占位符的列表格式、不重复分数等要求以该文件「波特五力分析写作规范」为准。核心要求：
- 结论前置，有数字支撑
- KPI 主数值（营业收入/归母净利润/FCF/净利率）：**负数用 `-` 号**（如 `-22.3%`、`-16.4亿美元`）；**主数值不写「约」**；勿用「净亏损约」「约负22.3%」等代替负号；同比句仍须可核对
- 美股金额以"亿美元"为单位（大于100亿用"X,XXX亿美元"或"X.X万亿美元"）
- 禁止口语化和感叹号
- **HTML 正文占位符不得使用 Markdown**：勿在 `{{SUMMARY_PARA_*}}`（含第四段）、`{{TREND*_TEXT}}`、`{{LATEST_OPERATING_UPDATE_TEXT}}`、`{{GEO_REVENUE_TEXT}}`、`{{INVESTMENT_THESIS}}`、`{{SANKEY_ANALYSIS_TEXT}}` 等字段中写入 `**加粗**`、`*斜体*`、反引号代码等；最终页面不会渲染 Markdown，会出现裸露星号。需强调处用中文「」或必要时少量 `<strong>…</strong>`（慎用以免破坏版式）。
- **禁止破坏锁定 HTML 中的注释闭合**：第四节、第五节 company 面板等处曾用多行 `<!-- …` 且下一行含示例 `{{…}}` 再用 `-->` 闭合；若生成脚本按字串删除「含 `{{分数}}` 的行」，会删掉唯一的 `-->`，导致**整段后续 DOM 被浏览器当作注释吞掉**（第五、六节版式全崩）。生成 HTML 时**不得**删除任何可能是**多行注释唯一闭合**的 `-->` 行。
- **可选：清理单行样例注释**：仅当确认某条注释是独立单行提示、与多行注释闭合无关时，才可删除以免残留 `{{...}}` 触发校验；**不确定则保留**，或改写注释文字而不删行。
