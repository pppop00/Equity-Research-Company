# Agent 5: HTML report validator

对生成后的 HTML 执行系统性校验（中文或英文报告共用同一套结构规则）。

## 输入

- 待验证 HTML：`workspace/{Company}_{Date}/{Company}_Research_CN.html` **或** `{Company}_Research_EN.html`（与本次 `report_language` 一致）
- `workspace/{Company}_{Date}/financial_data.json`
- `workspace/{Company}_{Date}/prediction_waterfall.json`

## 验证清单（逐项检查，不得跳过）

### ✅ 1. Section 完整性（结构检查）

必须存在以下 6 个 section（通过 id 定位）：
- `id="section-summary"`
- `id="section-financials"`
- `id="section-prediction"`
- `id="section-sankey"`
- `id="section-porter"`
- `id="section-appendix"`

**失败条件：** 任何一个 id 不存在 → 报告 CRITICAL 错误。

---

### ✅ 2. KPI 卡片（财务数据）

- `class="kpi-grid"` 下恰好 4 个 `class="kpi-card"`
- 每张卡片包含：`.kpi-label`, `.kpi-value`, `.kpi-change`, `.kpi-sub`
- `.kpi-card` 的 class 必须含 `up` 或 `down` 或 `neutral-kpi`（三选一）
- `.kpi-change` 的 class 必须含 `up` 或 `down`（二选一）
- 与 `financial_data.json` 中的数字交叉核对：营业收入偏差不超过 ±5%

**失败条件：** 卡片数量不是 4 → CRITICAL；数字偏差超 ±5% → WARNING。

---

### ✅ 3. CSS 变量完整性

HTML 中的 `<style>` 块必须包含以下所有变量定义（在 `:root` 或 `[data-theme="dark"]` 中）：
- `:root` 中：`--primary`, `--primary-light`, `--accent-green`, `--accent-red`, `--accent-amber`, `--bg`, `--bg-card`, `--text-primary`, `--text-secondary`, `--text-muted`, `--border`, `--shadow`
- `[data-theme="dark"]` 中：`--bg`, `--bg-card`, `--text-primary`, `--border`, `--shadow`

扫描 HTML 正文中是否有 `var(--` 引用了未在上述列表内的变量（可能是拼写错误）。

**失败条件：** 缺少任何必须变量 → WARNING；引用了未定义变量 → WARNING。

---

### ✅ 4. 图表容器与数据

**Waterfall 图：**
- `<svg id="chart-waterfall">` 存在
- JS 中 `const waterfallData = [...]` 存在且为非空数组
- 数组最后一项的 `type` 必须是 `"result"`
- 第一项的 `type` 必须是 `"baseline"`
- 所有 `end` 值由前一项的 `end` + `value` 推导出（允许 ±0.01 误差）
- `start` 和 `end` 数值范围合理：增长率应在 -50% 到 +100% 之间

**Sankey 图：**
- `<svg id="chart-sankey-actual">` 和 `<svg id="chart-sankey-forecast">` 均存在
- `const sankeyActualData` 和 `const sankeyForecastData` 均存在
- 每个 Sankey 对象有 `nodes` 数组（≥3个节点）和 `links` 数组（≥2条链接）
- `links` 中的 `source` 和 `target` 索引不超出 `nodes` 数组范围
- 所有 `value` > 0

**Radar 图：**
- `<canvas id="chart-radar-company">`, `<canvas id="chart-radar-industry">`, `<canvas id="chart-radar-forward">` 均存在
- `const porterScores` 存在，包含 `company`, `industry`, `forward` 三个 key
- 每个数组长度恰好为 5
- 每个分值在 1-5 之间（整数）

**失败条件：** 容器缺失 → CRITICAL；数据格式错误 → CRITICAL；数值超范围 → WARNING。

---

### ✅ 5. 波特五力 HTML 结构

- **`<!--` 注释完整性（CRITICAL）：** 在 `#porter-panel-company .porter-scores` 上方不得存在**未闭合**的多行 HTML 注释。若某脚本删除了带 `-->` 的说明行，会导致从该行起至下一个 `-->` 之间的**真实 DOM（含第一组 `<li>`、`.porter-text`、甚至附录）被浏览器当作注释隐藏**，版式表现为第五、六节「崩了」。校验：在 `porter-panel-company` 内 `document.querySelectorAll('#porter-panel-company .porter-scores li')` 逻辑上应有 5 条；或直接在源码中确认 `scores-company` 的 `<li>` **不在**同一未闭合 `<!--` 块内。
- 3 个 tab-panel：`id="porter-panel-company"`, `id="porter-panel-industry"`, `id="porter-panel-forward"`
- 每个 panel 内有 `.porter-scores` 列表，恰好 5 个 `<li>`
- 每个 `<li>` 包含一个 `.score-dot` 元素
- `.score-dot` 的 class 包含 `s1`-`s5` 之一，与 `porterScores` 数组值对应
- 每个 tab-panel 中有 `.porter-text` 且：若 `<html lang="zh-CN">` 则正文 ≥ **100 个汉字**；若 `<html lang="en-US">`（或 `lang="en"`）则正文 ≥ **450 个英文字符**（约同等信息量）

**失败条件：** li 数量不是5 → CRITICAL；score-dot class 与数组不符 → WARNING；达不到上述字数/字符门槛 → WARNING。

---

### ✅ 6. 页面结构完整性

- `<html lang="zh-CN">`（中文报告）**或** `<html lang="en-US">`（英文报告；`lang="en"` 可接受）存在
- CDN 链接存在：d3.v7, d3-sankey, chart.js
- `<link>` 中含 **Noto Sans SC**（中文报告）或 **Noto Sans**（英文报告常见）；至少一种 Google Fonts 引用存在
- `.report-header` 存在
- `.header-main` / `.header-left` / `.header-right` 存在
- `.rating-badge` class 包含 `overweight` / `neutral` / `underweight` 之一
- `.header-meta` 存在且包含3个 `<span>`
- `toggleTheme()` 函数存在
- `switchTab()` 函数存在
- `redrawAllCharts()` 函数存在
- `DOMContentLoaded` 事件监听存在

**失败条件：** 函数缺失 → CRITICAL；badge class 错误 → WARNING。

---

### ✅ 7. 占位符残留检查

扫描 HTML 中是否仍含有 `{{` 或 `}}` 字符（未替换的占位符）。

**失败条件：** 发现任何残留 → CRITICAL。

---

### ✅ 8. 数字格式检查

随机抽取 HTML 中出现的 5 个金融数字，核对：
- 中文报告：习惯单位为亿元人民币/亿美元等；英文报告：`$`、`bn`/`m`、`%` 等英语语境格式
- 百分比是否带 `%`（或上下文等价表述）
- 同比/变动是否有清晰符号或 `YoY` 等标记
- 是否存在 `NaN`, `undefined`, `null`, `Infinity`

**失败条件：** 发现 NaN/undefined/null/Infinity → CRITICAL；格式不规范 → WARNING。

---

### ✅ 9. 分地区 / 分业务列举与 `segment_data` 格式对称（占比不得半途而废）

**适用：** `financial_data.json` 中存在非空 `segment_data`，且 HTML 正文里有一段**连续分项列举**这些业务线或地区的收入/净营收（常见：`class="trend-card-text"`、章节小标题下的首段、脚注前的分项句；英文如 “by region:”, “segment revenue:”）。

**检查规则：**

1. **混用格式 → 须修复：** 若该列举中**至少一项**带有占总额的百分比（中文如 `（约 10.5%）`、`（10%）`；英文如 `(~10.5%)`、`(≈10% of total)`、`(x% of net revenue)`），则**同一句/同一段列举内**、且在 `segment_data` 中有对应数字的**每一项**，都必须带有**同类**占比表述。禁止出现「前三项带（约 x%）、后几项只写绝对额」这类不对称写法。
2. **数值对齐 JSON：** 文中的占比应与 `segment_data[].pct_of_total` 一致；若某条 JSON 缺 `pct_of_total`，应用 `revenue` 与总收入（如 `income_statement.current_year.revenue` 或与各 `segment_data.revenue` 之和）自行核算后再写入，并在列举中补全，或**整段**改为仅列绝对额（全段都不写占比）。
3. **仅金额、无占比：** 若对 `segment_data` 对应列举**全程**不写任何占比，仅列金额与名称 → PASS。

**失败条件：** 违反规则 1 或 2 → **WARNING**（视为交付前必改项：修正 HTML 叙述使其与 `financial_data.json` 对称一致；必要时同步 `financial_analysis.json` 等中间产出）。

---

## 输出格式

输出结构化校验报告，格式如下：

```
=== HTML 报告验证报告 ===
文件：{Company}_Research_CN.html 或 {Company}_Research_EN.html
验证时间：{时间}

[CRITICAL] 或 [WARNING] 或 [PASS]

--- 1. Section 完整性 ---
[PASS] 6个section均存在 ✓

--- 2. KPI 卡片 ---
[PASS] 4张卡片，方向class正确 ✓
[WARNING] 营业收入：HTML显示 39.1亿 vs JSON 38.7亿（偏差 1.0%，在容差内）

--- 3. CSS 变量 ---
[PASS] 所有必须变量存在 ✓

--- 4. 图表容器与数据 ---
[PASS] Waterfall: 6个bar，首尾类型正确 ✓
[PASS] Sankey: 9节点/8链接(实际), 9节点/8链接(预测) ✓
[PASS] Radar: 3组，每组5分值，范围1-5 ✓

--- 5. 波特五力 ---
[PASS] 3个panel，各5个li，score-dot与数组吻合 ✓

--- 6. 页面结构 ---
[PASS] 所有必须元素和函数存在 ✓

--- 7. 占位符残留 ---
[PASS] 无残留占位符 ✓

--- 8. 数字格式 ---
[PASS] 抽查5个数字，无NaN/undefined，格式规范 ✓

--- 9. 分地区/分业务列举与 segment_data ---
[PASS] 无 segment_data，或列举格式对称 ✓
（或）[WARNING] 列举中部分分项带占比、部分不带 → 须补全或与 JSON 对齐后再交付

=== 总结 ===
CRITICAL 错误：0
WARNING  警告：1
状态：⚠️ 通过（含警告）
```

## 处理逻辑

- 若有 **CRITICAL** 错误：输出报告后，**立即修复 HTML 文件**，修复后重新运行验证直到0个CRITICAL为止。
- 若只有 **WARNING**：输出报告，提示 orchestrator 人工核查。若 WARNING 含 **第 9 项（分地区/分业务格式对称）**，须在最终交付用户前修正 HTML（及与之绑定的 JSON 叙述），勿留「部分有占比、部分无」的半成品句。
- 若全部 PASS：输出报告，告知 orchestrator 报告质检通过。

## 修复优先级

修复时按以下顺序处理：
1. 残留占位符（`{{...}}`）→ 回头查 JSON 数据填充
2. 缺失 section → 补全对应 HTML 块
3. 图表数据格式错误 → 修正 JS 数据变量
4. KPI 卡片数量/class 错误 → 修正 HTML
5. score-dot 与数组不符 → 同步修正 HTML 和 JS
6. 第 9 项：不对称的分项占比叙述 → 按 `segment_data` 补全括号内占比或整段改为仅金额
