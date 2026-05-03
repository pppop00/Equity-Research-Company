# Agent 6: HTML report validator

对生成后的 HTML 执行系统性校验（中文或英文报告共用同一套结构规则）。

**定位说明：** 本 agent 主要负责 **结构完整性、模板契约、图表容器、基础交叉核对、交付前渲染风险**。它**不是**完整的最终数据验证器；显式公式复算、数量级核对、Sankey/利润表语义桥接、GAAP/non-GAAP 混用等问题，应由 `agents/final_report_data_validator.md` 在 Phase 5.5 先行处理。

## 0. Hard preconditions（先于任何其他检查执行；不通过即 CRITICAL，不得继续）

本 validator 不是「重新评估是否走锁定模板」的入口，而是「锁定模板已被填充」之后的结构与契约校验。任何主动放宽锁定模板要求的行为都是 P5/P6 违规：

1. **锁定骨架必须存在：** `research/_locked_<lang>_skeleton.html`（`<lang> ∈ {cn, en}`）必须在工作目录中。缺失 → CRITICAL；这意味着 P5 跳过了 `tools/research/extract_template.py`，最终 HTML 不可能是合法填充产物。
2. **`tools/research/validate_report_html.py` 必须已被执行且 exit 0：** 在写出本 agent 自己的 `report_validation.txt` / `structure_conformance.json` 之前，必须自行调用 `python tools/research/validate_report_html.py --run-dir <run_dir> --lang <cn|en>` 并捕获其 JSON 输出。该 JSON 的 `status` 字段（`pass | warn | critical`）即 `structure_conformance.json -> html_template_gate.status` 的合法取值；**禁止**手写为 `not_applicable`、`pass_with_scope_limitations`、`partial_pass`、`scope_limited`、`institution_compat` 或任何工具未输出的字符串。该工具返回 `critical` → 本 agent 输出 CRITICAL 并要求回到 P5 重写，**不得继续**。
3. **Packaging profile 必须来自白名单：** `structure_conformance.json -> profile` 只允许是 `workflow_meta.json -> packaging_profiles` 中的四个之一：`strict_18_full_qc_secapi`、`strict_17_full_qc_no_secapi`、`strict_13_fast_no_qc_secapi`、`strict_12_fast_no_qc_no_secapi`。选择规则是 `(qc_mode, sec_api_mode)`（见 §0.A 下文）。**禁止**新造 profile（如 `institution_compat_no_secapi_no_cards`、`private_company_*`、`scope_limited_*`、`fund_compat_*`）。新造 profile = P6 违规 → CRITICAL。
4. **`report_validation.txt` 顶层 status 只能是 `pass | warn | critical`：** 不存在 `pass_with_scope_limitations`、`pass with scope limitations`、`institution-compatible pass`、`partial pass`、`scope-limited pass`、`not applicable` 等任何变体。任何「这家公司是私募基金 / 对冲基金 / 家办 / 非公众公司，因此公开公司报告章节标记为 N/A」之类自我安慰式的说法都不是合法的 status。equiforge 的合同是：**无论 target 公司是何种类型，最终交付都是同一份锁定模板填充结果。** 若公开发行人级别的财务披露不可得，由 `report_writer_{cn,en}.md` 用最佳代理变量（AUM、策略、前十持仓、经理人 13F/PF、同业宏观等）将锁定章节填到字数下限，并在文中显式标注数据缺口；不得由本 validator 通过弱化 status 把缺口「合规化」。
5. **若 §0 任一前置条件失败，立即输出 CRITICAL，写出 `report_validation.txt`（status: `critical`）与 `structure_conformance.json`（含 `missing_required_files` / 错误 profile / 错误 gate status 字段），并通知 orchestrator 回到 P5；本文件其余各项检查仍可执行以提供完整诊断信息，但不得据此改判 status。**

## 输入

- 待验证 HTML：`workspace/{Company}_{Date}/{Company}_Research_CN.html` **或** `{Company}_Research_EN.html`（与本次 `report_language` 一致）
- `workspace/{Company}_{Date}/financial_data.json`
- `workspace/{Company}_{Date}/financial_analysis.json`
- `workspace/{Company}_{Date}/edge_insights.json`
- `workspace/{Company}_{Date}/macro_factors.json`
- `workspace/{Company}_{Date}/news_intel.json`
- `workspace/{Company}_{Date}/prediction_waterfall.json`
- `workspace/{Company}_{Date}/porter_analysis.json`
- `workspace/{Company}_{Date}/final_report_data_validation.json`
- `workspace/{Company}_{Date}/qc_audit_trail.json`（若本次运行包含 Phase 2.6–3.6 对抗审查）
- `workflow_meta.json`（根目录；包装 profile 与清理规则）
- `references/intelligence_layer.md`（报告级情报信号契约；用于第 7e 项）
- 可选（卡片分支）：`workspace/{Company}_{Date}/**/*.card_slots.json` 与其中 `logo_asset_path` 指向的 `logo_official.png`

**新增职责（profile 模式）：** 本 agent 负责按 `workflow_meta.json` 选择并执行 packaging profile 收口，并写出 `workspace/{Company}_{Date}/report_validation.txt` 与 `workspace/{Company}_{Date}/structure_conformance.json`。

**第 10–13 项与 WARNING 级别：** 这几条在输出中标记为 **WARNING**，是因为叙述是否越界、来源日期是否矛盾等问题难以像结构缺失或未替换的 `{{…}}` 那样用固定规则 **100% 自动判为 CRITICAL**；**不代表可忽略**。编排器在 `SKILL.md` Phase 6 已将第 10–13 项与第 9 项一样列为交付前必改；有此类 WARNING 时须在交付用户前修正 HTML（及关联 JSON 叙述）。

**第 2 项（KPI 主数值与 `neutral-kpi` 样式）补充：** 下列若判为 **WARNING**，与第 9 项相同，**交付前必须改到通过**，不得把「仅 WARNING」当作可发货。（复盘：曾出现 KPI 用「约负」「净亏损约」代替负号、主数值带「约」、`neutral-kpi` 卡仅用琥珀边+白底与相邻亏损卡不一致等问题——见 §2 细则。）

**第 7d 项（edge insight）补充：** 若 `edge_insights.json` 缺失、`chosen_insight` 缺少证据，或投资摘要第二段没有体现该洞察，虽可标为 WARNING，但与第 9 项同级，交付前必须修正。

**第 7e 项（intelligence layer）补充：** 若 `news_intel.json -> intelligence_signals[]` 缺失、信号字段不完整，或最终摘要 / 趋势卡 / 投资逻辑仍是泛泛描述而没有监控变量和证伪触发器，标为 **WARNING（交付前必改）**。

**与 Phase 5.5 的关系：** 若 `final_report_data_validation.json` 仍有未关闭的 **CRITICAL**，或 WARNING 涉及公式 / 数量级 / Sankey 语义 / GAAP 与 non-GAAP 口径混用，则本 validator 即使其余项目通过，也不得判定可交付。

## 验证清单（逐项检查，不得跳过）

### ✅ 0. Packaging profile 产物结构对照与清理（由本 agent 执行）

从 `workflow_meta.json -> packaging_profiles` 选择 profile，不再强制单一 `strict_18`。

**A. profile 选择规则（必须可追溯）**

1. 先判定 `qc_mode`：  
   - 若存在 `qc_audit_trail.json` 且有有效裁定内容 → `full`  
   - 若用户或编排器明确跳过 QC，且 `qc_audit_trail.json` 不存在 → `fast`
2. 再判定 `sec_api_mode`：  
   - 若存在 `sec_edgar_bundle.json` 且本轮走 SEC API-first → `yes`  
   - 其余（非美股 / PDF 模式 / 用户拒绝邮箱 / SEC fallback）→ `no`
3. 用 `(qc_mode, sec_api_mode)` 映射 profile（见 `workflow_meta.json`）：
   - `(full, yes)` → `strict_18_full_qc_secapi`
   - `(full, no)` → `strict_17_full_qc_no_secapi`
   - `(fast, yes)` → `strict_13_fast_no_qc_secapi`
   - `(fast, no)` → `strict_12_fast_no_qc_no_secapi`

**B. 必须文件列表**

- 从 `workflow_meta.json` 读取已选 profile 的 `required_files_zh` 或 `required_files_en`（按 `report_language`）。
- 本 agent 必须写出 `report_validation.txt` 与 `structure_conformance.json`，两者应被包含在 required list。

**C. 默认删除项**

- 从 `workflow_meta.json -> default_cleanup_targets` 读取并执行清理（可追加本地临时文件模式）。

**执行顺序：**

1. 选择 profile 并记录理由。
2. 扫描工作目录，记录缺失项与额外项。
3. 删除默认清理项。
4. 再次扫描确认清理是否完成。
5. 写出 `report_validation.txt` 与 `structure_conformance.json`。

`structure_conformance.json` 建议结构：

```json
{
  "mode": "strict_packaging",
  "profile": "strict_18_full_qc_secapi",
  "language": "zh",
  "status": "pass|critical",
  "workspace": "workspace/{Company}_{Date}",
  "required_files": ["...18 items..."],
  "missing_required_files": [],
  "deleted_files": [],
  "forbidden_remaining_files": [],
  "summary": {
    "required_count": 18,
    "missing_count": 0,
    "deleted_count": 0,
    "forbidden_remaining_count": 0
  }
}
```

**失败条件：**

- 缺失所选 profile 任一必须文件 → **CRITICAL**
- 默认删除项执行后仍残留 → **CRITICAL**

### ✅ 0b. Card1 Logo 分辨率（卡片分支存在时）

仅当工作区存在 `*.card_slots.json` 且文件内含 `logo_asset_path` 时执行本项；纯 HTML 研报交付可跳过。

**检查项：**

1. `logo_asset_path` 指向文件必须存在（通常是 `logo_official.png`）。
2. 从 `*.card_slots.json` 读取 `logo_render_width_px`、`logo_render_height_px`、`logo_export_width_px`、`logo_export_height_px`、`logo_scale_factor`。  
   若缺少 render 尺寸，按默认槽位 `276x328`。
3. 读取 logo 图片实际像素宽高（可用 `sips`/等价工具）。
4. 强制 2x 规则：  
   - 实际像素宽度 `>= 2 * logo_render_width_px`  
   - 实际像素高度 `>= 2 * logo_render_height_px`
5. 若声明了 `logo_export_width_px` / `logo_export_height_px`，需与实际像素一致（允许 ±1 像素误差）。
6. `logo_scale_factor` 必须 `>= 2`。

**失败条件：** `logo_asset_path` 不存在、元数据缺失、像素尺寸未达 2x、或 `logo_scale_factor < 2` → **WARNING（交付前必改）**。

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
- `.kpi-change` 的 class 必须与对应卡片一致：`up`、`down` 或 **`neutral-kpi`**（当指标两年均为负但同比向零收窄、或同比「改善」但仍未转正等，避免误用绿色暗示已健康——见 `references/report_style_guide_cn.md` / `report_style_guide_en.md` 财务概览 KPI 条）
- 与 `financial_data.json` 中的数字交叉核对：营业收入偏差不超过 ±5%

**复盘摘要（此类问题须在 Phase 6 显式拦截，不得再交付）：**

| 问题 | 错误示例 | 正确方向 |
|------|----------|----------|
| 负号被口语替代 | 「净利率约负22.3%」「净亏损约16.4亿美元」「自由现金流约负1.2亿」 | 主数值用 **`-` 与数字连写**：`-22.3%`、`-16.4亿美元`、`-1.2亿美元` |
| KPI 主数值加「约」 | 「约 -16.4亿美元」「约 -1.2亿美元」 | **KPI 主数值不加「约」**，直接数字+单位（四舍五入后）；「约」仅用于正文长句 |
| `neutral-kpi` 视觉与亏损卡割裂 | 仅琥珀色左边框、白底，与第二、四张红底亏损卡不一致 | 锁定模板中 `.kpi-card.neutral-kpi` 须与亏损卡**同色系**（红边 + `var(--kpi-down-bg)`）；语义仍用 class `neutral-kpi` 避免误用绿色 `up` |

**KPI 主数值（`.kpi-value`）— 交付前必查（与 `references/report_style_guide_cn.md` / `references/financial_metrics.md` 一致）：**

- **中文报告（`lang="zh-CN"`）：** 归母净利润、净利率、自由现金流等若为负，**必须**在 `.kpi-value` 内使用 **ASCII 负号 `-` 紧贴数字**（如 `-22.3%`、`-16.4亿美元`、`-1.2亿美元`）。**禁止**用「约负」「净亏损约」「负向约」等**代替**负号本身。
- **禁止**在 **`.kpi-value` 内**以「约」修饰主数字（含「约 -16.4亿美元」类写法）——KPI 大字区只保留**直接数字 + 单位**。
- **英文报告：** 负数用前导 minus（`-$164M`, `-22.3%`），勿用 “negative” / “approx. negative” 替代 **`-`**。
- **建议扫描（人工或脚本）：** 若任意 `.kpi-value` 文本含子串 **`约负`**、**`净亏损约`**，或匹配「约」紧挨负号/金额 → 判 **WARNING**（必改）。

**`neutral-kpi` 与锁定模板 CSS：**

- **第三卡 FCF** 在「两年均为负但同比向零收窄」时应为 class **`neutral-kpi`**（勿用绿色 `up`），且 HTML 内 `<style>` 中 **`.kpi-card.neutral-kpi`** 必须与 **`references/report_style_guide_cn.md`** 及当前 `agents/report_writer_cn.md` 锁定块一致：**红左边框 + `background: var(--kpi-down-bg)`**（与 `.kpi-card.down` 同视觉层级），**不得**残留仅 **`border-left-color: var(--accent-amber)`** 且无浅红底的旧版写法。
- **建议：** 若发现 `neutral-kpi` 仍为琥珀边、白底 → **WARNING**（必改：用 `scripts/extract_report_template.py` 抽取的当前骨架替换内联样式相关规则，或整体以最新锁定模板为准）。

**失败条件：** 卡片数量不是 4 → CRITICAL；数字偏差超 ±5% → WARNING；**上述 KPI 版式 / `neutral-kpi` CSS 违反** → **WARNING**（**交付前必改**，与第 9 项同级）。

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
- 所有 `end` 值由前一项的 `end` + `value` 推导出（允许 ±0.01 误差）；若编排器使用从 0 累加的**增速桥**，中间各柱应逐步累加至 **`result`** 柱的终点（与 `prediction_waterfall.json` 一致；若采用「先显示基准营收再拆」等变体，**不得**在本图使用美元营收 — 见下条）。

**Waterfall — 量纲错误（CRITICAL，禁止交付）：** 锁定脚本把每个 `start`/`end`/`value` **直接加上 `%` 显示**。这些数字必须是 **`prediction_waterfall.json` 中的百分点增速**，**不得**使用 **`base_revenue`**、预测营收绝对额、或任何 **百万美元级** 营收数字（典型错误：第一根柱 `value: 37296` 对应 `base_revenue`，屏上会显示 **「37296.0%」**）。**自动/人工判定启发式：** 若任一柱的 `start`、`end` 或 `value` 的绝对值 **≥ 200**，视为 **单位错误 → CRITICAL**（正常财年营收增速桥几乎不可能出现 ±200 个百分点；该阈值用于区分「离谱的 $M 误用」与合法但偏高的 `%`）。若绝对值在 **100–200** 之间 → **WARNING**（须人工核对是否真为极端假设增速）。

**Waterfall — 与 JSON 交叉核对（CRITICAL 或 WARNING）：** 读取 `prediction_waterfall.json` 的 **`predicted_revenue_growth_pct`**。在 `waterfallData` 中找到 **`type: "result"`** 的对象：其 **`end`**（若模板约定 `start: 0` 且结果柱用 `end` 表示累计预测增速）或 **`value`**（若与模板示例一致）必须在数值上等于 **`predicted_revenue_growth_pct`**（允许 **±0.05** 四舍五入误差）。**不匹配 → CRITICAL。** 可选：第一根基准柱的 `value` 应等于 **`baseline_growth_pct`**（或与编排器约定的基准步一致）；**宏观合计**应与 **`macro_adjustment_pct`**（及分项之和）一致 — 若明显矛盾 → **WARNING** 以上。

**Waterfall — 合理区间（辅助）：** 在确认单位为百分点后，`start`/`end` 一般落在 **−50 到 +100** 之间（极端情形除外）；此前「超范围」单独标 **WARNING**；**一旦触发「绝对值 ≥ 200」规则，优先按 CRITICAL 处理。**

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
- Porter 分值方向必须是威胁/压力分：`1-2` = 低威胁/绿色，`3` = 中性/琥珀色，`4-5` = 高威胁/红色；不得把 5 当作“最好”或把 1 当作“最糟”。
- 若任一 tab 的行业竞争强度正文明确描述“竞争激烈 / 价格战 / rivalry intense / price war”等高竞争状态，但对应 `porterScores[*][4] < 4`，或明确描述“竞争几乎没有 / monopoly-like / minimal competition”但对应分数 `> 2`，标记为 **WARNING（评分方向疑似反向）**。

**失败条件：** 容器缺失 → CRITICAL；数据格式错误 → CRITICAL；**瀑布图量纲错误（如误用 `base_revenue`）或 `result` 与 `predicted_revenue_growth_pct` 不一致** → CRITICAL；**数值超范围 / 绝对值 100–200 可疑** → WARNING。

---

### ✅ 5. 波特五力 HTML 结构

- **`<!--` 注释完整性（CRITICAL）：** 在 `#porter-panel-company .porter-scores` 上方不得存在**未闭合**的多行 HTML 注释。若某脚本删除了带 `-->` 的说明行，会导致从该行起至下一个 `-->` 之间的**真实 DOM（含第一组 `<li>`、`.porter-text`、甚至附录）被浏览器当作注释隐藏**，版式表现为第五、六节「崩了」。校验：在 `porter-panel-company` 内 `document.querySelectorAll('#porter-panel-company .porter-scores li')` 逻辑上应有 5 条；或直接在源码中确认 `scores-company` 的 `<li>` **不在**同一未闭合 `<!--` 块内。
- 3 个 tab-panel：`id="porter-panel-company"`, `id="porter-panel-industry"`, `id="porter-panel-forward"`
- 每个 panel 内有 `.porter-scores` 列表，恰好 5 个 `<li>`
- 每个 `<li>` 包含一个 `.score-dot` 元素
- `.score-dot` 的 class 包含 `s1`-`s5` 之一，与 `porterScores` 数组值对应
- `.score-dot` 颜色映射必须保持：`.s1/.s2` 使用 `var(--accent-green)`，`.s3` 使用 `var(--accent-amber)`，`.s4/.s5` 使用 `var(--accent-red)`；雷达点颜色也应通过 `porterScoreColor` 或等价逻辑映射为低分绿、高分红。
- 每个 tab-panel 中有 `.porter-text` 且：若 `<html lang="zh-CN">` 则正文 ≥ **100 个汉字**；若 `<html lang="en-US">`（或 `lang="en"`）则正文 ≥ **450 个英文字符**（约同等信息量）
- **推荐版式（Phase 5）：** 每个 `.porter-text` 内为**单个 `<ul>` 含恰好 5 个 `<li>`**（顺序对应五力），且**不在** `<li>` 内重复「X/5」起句——见 `references/report_style_guide_cn.md` / `report_style_guide_en.md` 波特五力 / Porter Five Forces。若仅为连续 `<p>` 而无列表 → **WARNING**（风格偏离，交付前可接受但建议对齐技能包规范）。
- **中文 Porter 句式（Phase 5 新规范）：** 若 `<html lang="zh-CN">`，每个 `<li>` 应以前置的 **QC 合议结论句** 开头，并使用**维持/调整**显式格式，例如 **「经QC合议，维持供应商议价能力为3分。……」** 或 **「经QC合议，决定将供应商议价能力评分从4分调整为3分。……」**。不要只写普通分析段，也不要只在调分时才出现该句式。**同时核对审计链一致性：** 若正文写成“从 X 调整到 Y”，则 `qc_audit_trail.json` / `porter_analysis.qc_deliberation` 中必须存在该维度被采纳并改分的记录；若 `qc_audit_trail.json` 有显式 `score_changed: false`（或 `score_before = score_after`），HTML 就不得写成调整句式；若无记录，则判为 **WARNING（疑似编造调分）**。

**失败条件：** li 数量不是5 → CRITICAL；score-dot class 与数组不符 → WARNING；score-dot 或雷达点颜色映射反向（例如 s5 绿色、s1 红色）→ WARNING（交付前必改）；达不到上述字数/字符门槛 → WARNING；中文 Porter `<li>` 未使用上述 QC 合议维持/调整句式 → WARNING（交付前必改）；正文声称“从 X 调整到 Y”但审计链无对应改分记录，或审计链显式表明 `score_changed: false` / `score_before = score_after` → WARNING（交付前必改）。

---

### ✅ 6. 页面结构完整性

- `<html lang="zh-CN">`（中文报告）**或** `<html lang="en-US">`（英文报告；`lang="en"` 可接受）存在
- CDN 链接存在：d3.v7, d3-sankey, chart.js
- `<link>` 中含 **Noto Sans SC**（中文报告）或 **Noto Sans**（英文报告常见）；至少一种 Google Fonts 引用存在
- `.report-header` 存在
- `.header-main` / `.header-left` / `.header-right` 存在
- **Card1 主名位规则（中文报告）：** `.company-name-cn` 必须为公司中文名（页眉标题主名位，深蓝底衬线大字），不得为英文名或纯 ticker
- **Card1 次标题规则（按语言分支）：**
  - 中文报告：`.company-name-en` 必须为“公司英文名 + 分隔符 + ticker”（示例：`Apple Inc. • AAPL`）。
  - 英文报告：按 `agents/report_writer_en.md` 规则，第一行显示英文公司名，`.company-name-en` 允许仅为 `ticker`。
- `.rating-badge` class 包含 `overweight` / `neutral` / `underweight` 之一
- `.header-meta` 存在且包含3个 `<span>`
- `.header-meta` 中表示数据来源的 `<span>` 文本应为**单行短摘要**，**最终文本长度不得超过 50 个字符**（含中文、英文、空格与标点）；这是为避免页眉横向排版被挤压或换行
- `toggleTheme()` 函数存在
- `switchTab()` 函数存在
- `redrawAllCharts()` 函数存在
- `DOMContentLoaded` 事件监听存在

**失败条件：** 函数缺失 → CRITICAL；中文报告中 `.company-name-cn` 非中文公司名或误填英文/ticker → WARNING（交付前必改）；`.company-name-en` 与对应语言分支规则不一致 → WARNING（交付前必改）；badge class 错误 → WARNING；`{{DATA_SOURCE}}` 渲染后超过 50 个字符 → WARNING（交付前必改）。

---

### ✅ 7. 占位符残留检查

扫描 HTML 中是否仍含有 `{{` 或 `}}` 字符（未替换的占位符）。

- **交付口径：** 最终交付 HTML 不应保留示例性 `{{内容}}` / `{{...}}` 注释。允许存在的唯一例外是你已人工确认某个 `-->` 为多行注释闭合所必需，且删除会破坏 DOM；除此以外，示例性占位符注释也应清理掉。**实操：** 只有确认某行是**独立单行**注释、与多行 `<!-- …` 的闭合无关时才删除；**存疑则整行保留**，或改写注释文字去掉 `{{`/`}}`，勿误删唯一闭合 `-->`。

**失败条件：** 发现任何残留 → CRITICAL。

---

### ✅ 7b. 第三节 `macro_factor_commentary`（传导阐释）

- 在 `id="section-prediction"` 内应存在 **`.macro-factor-commentary`** 容器，且 **`{{MACRO_FACTOR_COMMENTARY}}`** 已替换为实质内容（非空、非占位符）。
- 若 `macro_factors.json` 含 **`macro_factor_commentary`**：HTML 中传导阐释的 **核心事实**（如「六项合计等于 `total_macro_adjustment_pct`」、与瀑布图「宏观调整」栏的关系）应与 JSON 一致；**不得**在 HTML 中另写与 JSON 矛盾的第二套宏观传导故事。
- 若 `macro_factors.json` **缺少** `macro_factor_commentary` 或为空字符串 → **WARNING**（交付前补全，见 `agents/macro_scanner.md` Step 7b）。

**失败条件：** 传导区为空或未替换 → CRITICAL；与 JSON 明显矛盾 → WARNING。

---

### ✅ 7c. `macro_regime_context`（行业/角色传导框架）

- `macro_factors.json` 必须包含 **`macro_regime_context`**，且至少含：`sector`、`sub_industry`、`company_role`、`company_role_confidence`、`sector_regime`、`primary_transmission_channels`、`sign_reversal_watchlist`、`role_evidence`。
- `company_role_confidence` 只能为 `high` / `medium` / `low`；混合业务公司若证据不充分，不得写成 `high`。
- `primary_transmission_channels` 应为非空数组；`sign_reversal_watchlist` 应为非空数组，用于防止把估值利好写成收入利好、或把 supplier / spender 等角色方向写反。
- HTML 第三节、附录方法论、`macro_factor_commentary` 不得与 `macro_regime_context` 明显冲突。例如：`company_role` 为 `AI/cloud spender` 时，不得无证据写“客户 CapEx 上升直接推升公司收入”；若只讨论降息，应区分估值/融资渠道与收入渠道。

**失败条件：** `macro_regime_context` 缺失或关键字段为空 → WARNING（交付前补全）；HTML / `macro_factor_commentary` 与该 context 明显冲突 → WARNING（交付前修正）。

---

### ✅ 7d. 投资摘要与 `edge_insights.json`

- `edge_insights.json` 必须存在，且包含非空 `chosen_insight`、`chosen_insight.headline`、`chosen_insight.insight_type`、`chosen_insight.surface_read`、`chosen_insight.hidden_rule`、`chosen_insight.reframed_read`、`chosen_insight.investment_implication`、`chosen_insight.evidence[]`、`chosen_insight.confidence`、`summary_para_2_draft`。
- `chosen_insight.insight_type` 只能为 `non_consensus_read`、`industry_unwritten_rule`、`industry_special_rule` 之一。
- `chosen_insight.evidence[]` 至少 1 条；每条应包含 `source` 和 `fact`。若 `confidence` 为 `high`，证据必须能追溯到 `financial_data.json`、`news_intel.json`、SEC / 年报 / 公司 IR 等权威来源。
- Section I 必须有恰好 4 个 `.summary-para`。中文报告每段建议 **160–200 个汉字**；英文报告每段建议 **90–130 words**。若略超但信息密度高可降为人工 WARNING；若仍是旧版 80–120 字短摘要，应修正。
- 第二个 `.summary-para` 必须体现 `edge_insights.json` 的核心事实：至少能对应 `surface_read`、`hidden_rule` / `reframed_read`、`investment_implication` 三者中的两个以上，且不能只是“公司领先、行业增长、需求强劲”等通用句。
- `financial_analysis.json` 应包含 `summary_para_1`–`summary_para_4`；其中 `summary_para_2` 应与 `edge_insights.json.summary_para_2_draft` 的核心事实一致。

**失败条件：** `edge_insights.json` 缺失或关键字段为空、证据为空、HTML 第二段未体现 edge insight、或摘要段落仍为旧长度/旧结构 → **WARNING**（交付前必改）。

### ✅ 7e. 情报层信号与可执行投资逻辑

- `news_intel.json` 必须包含 `intelligence_signals` 数组；若公开数据很薄，可为空数组，但 `notes[]` 必须解释限制。正常完整报告应至少有 1 条可追溯信号。
- 每条 `intelligence_signals[]` 至少包含：`id`、`theme`、`signal_type`、`fact`、`source`、`affected_metric`、`direction`、`confidence`、`watch_metric`、`thesis_implication`。
- `signal_type` 只能为：`filing_disclosure`、`industry_shift`、`company_event`、`policy_regulation`、`customer_supply_chain`、`pricing_margin`、`consensus_trap`。
- `edge_insights.json` 必须包含顶层字段：`chosen_signal_ids`、`thesis_variable`、`monitor_metric`、`falsification_trigger`。若 `chosen_signal_ids[]` 非空，其 ID 必须存在于 `news_intel.json -> intelligence_signals[]`。
- 若 `prediction_waterfall.json -> company_events_detail[]` 中出现 `source_signal_id`，该 ID 必须存在于 `news_intel.json -> intelligence_signals[]`，且对应信号的 `affected_metric` / `thesis_implication` 应与该事件的方向和解释不冲突。
- HTML 的投资逻辑框、风险提示、Section II 趋势卡或 Section I 第三段中，至少一处应体现可监控变量（来自 `watch_metric` / `monitor_metric`）或证伪条件（来自 `falsification_trigger`）。不能只写“需求强劲、行业景气、公司领先、估值有吸引力”等泛泛表达。

**失败条件：** 信号数组缺失且无解释、信号关键字段为空、`chosen_signal_ids[]` 指向不存在的 ID、`source_signal_id` 无法追溯、或最终 HTML 投资逻辑 / 趋势卡缺少监控变量与证伪条件 → **WARNING**（交付前必改）。

---

### ✅ 8. 数字格式检查

随机抽取 HTML 中出现的 5 个金融数字，核对：
- 中文报告：习惯单位为亿元人民币/亿美元等；英文报告：`$`、`bn`/`m`、`%` 等英语语境格式
- 百分比是否带 `%`（或上下文等价表述）
- 同比/变动是否有清晰符号或 `YoY` 等标记
- 是否存在 `NaN`, `undefined`, `null`, `Infinity`

**失败条件：** 发现 NaN/undefined/null/Infinity → CRITICAL；格式不规范 → WARNING。

---

### ✅ 8b. 财务指标表最后一列：结论性定调，不得填裸数

**适用：** Section II `.metrics-table`（表头为 **`同比变动`** 或 English **`YoY movement` / `YoY change`**）。

**规则：**

1. 逐行读取 `<tbody><tr>` 的第 4 个 `<td>`。该单元格必须是阅读当年/上年数据后的**结论性定调**，不得是 `+0.62%`、`-1.4pct`、`+4.55%`、`0.00%` 这类裸数字。
2. 中文报告允许的推荐词表：`显著改善`、`改善`、`基本持平`、`恶化`、`显著恶化`、`权益缺口收窄`、`权益缺口扩大`、`期末股东权益为负`、`不适用`。如出现同义短语，必须仍是短结论，不得包含 `%`、`pct`、纯数字或公式。
3. 英文报告允许的推荐词表：`Significantly improved`、`Improved`、`Stable`、`Deteriorated`、`Significantly deteriorated`、`Equity deficit narrowed`、`Equity deficit widened`、`Ending equity negative`、`N/A`。
4. `class="metric-up"` / `metric-down` 应与定调一致：改善类用 `metric-up`，恶化类用 `metric-down`；`基本持平` / `Stable` / `不适用` 可用中性或最接近语义的 class，但不得用裸百分比冒充定调。

**失败条件：** 第 4 列为裸数字/百分比/`pct` → **WARNING**（交付前必改）；定调与 class 明显冲突 → WARNING。

---

### ✅ 8c. 宏观因子表数值格式与最后一列方向

**适用：** Section III `.factor-table`（表头含 **`宏观变化（%）` / `Macro change (%)`**、**`调整幅度（%）` / `Adjustment (%)`** 和 **`方向` / `Direction`**）。

**规则：**

1. 表头第 5 列必须写成 **`调整幅度（%）`** 或 English **`Adjustment (%)`**；不得继续使用 `调整幅度（pct）`、`Adj. (ppt)`、`Adjustment (pct)`。
2. 逐行读取第 2 列（宏观变化）与第 5 列（调整幅度）。因为表头已经标注 `%`，两列单元格内**不得再出现 `%`**。
3. 非零数值必须带 `+` 或 `-`；0 必须写成 **`0`**，不得写 `+0`、`+0.00`、`-0.0`、`0%`。
4. 数值小数最多两位。允许 `-4.2`、`+8.00`、`-3.1`、`+0.15`、`-0.80`、`0`；禁止 `+8%`、`-4.1667`、`-3.125`、`+0.14685`。
5. 第 3 列 β 与第 4 列 φ 最多两位小数；β 可为负数，但不应出现 `+0.40` 这类正号或 `%`。
6. 最后一个 `<td>` 只允许表达方向：中文 `正向` / `负向` / `中性`；英文 `Positive` / `Negative` / `Neutral`。最后一列不得出现 `+0.62`、`-2.0`、`0.00`、`%`、`pct` 或任何纯数值。
7. 方向应与第 5 列数值符号一致：正数 → `正向` / `Positive`，负数 → `负向` / `Negative`，0 → `中性` / `Neutral`。
8. 方向列颜色必须复用锁定模板已有 class：正数最后一个 `<td>` 应含 `class="metric-up"`，负数应含 `class="metric-down"`；中性单元格不加方向颜色 class（或保持普通文本色）。不得新增 CSS class 或内联颜色。

**失败条件：** 表头仍用 `pct` / `ppt`；第 2 或第 5 列含 `%`、非零缺正负号、0 带正负号、超过两位小数；β/φ 超过两位小数或含 `%`；最后一列包含裸数字/百分比/`pct`；方向与调整幅度符号冲突；正/负方向缺少对应 `metric-up` / `metric-down` class → **WARNING**（交付前必改）。

---

### ✅ 9. 分地区 / 分业务列举与 `segment_data` 格式对称（占比不得半途而废）

**适用：** `financial_data.json` 中存在非空 `segment_data`，且 HTML 正文里有一段**连续分项列举**这些业务线或地区的收入/净营收（常见：`class="trend-card-text"`、章节小标题下的首段、脚注前的分项句；英文如 “by region:”, “segment revenue:”）。

**检查规则：**

1. **混用格式 → 须修复：** 若该列举中**至少一项**带有占总额的百分比（中文如 `（约 10.5%）`、`（10%）`；英文如 `(~10.5%)`、`(≈10% of total)`、`(x% of net revenue)`），则**同一句/同一段列举内**、且在 `segment_data` 中有对应数字的**每一项**，都必须带有**同类**占比表述。禁止出现「前三项带（约 x%）、后几项只写绝对额」这类不对称写法。
2. **数值对齐 JSON：** 文中的占比应与 `segment_data[].pct_of_total` 一致；若某条 JSON 缺 `pct_of_total`，应用 `revenue` 与总收入（如 `income_statement.current_year.revenue` 或与各 `segment_data.revenue` 之和）自行核算后再写入，并在列举中补全，或**整段**改为仅列绝对额（全段都不写占比）。
3. **仅金额、无占比：** 若对 `segment_data` 对应列举**全程**不写任何占比，仅列金额与名称 → PASS。

**失败条件：** 违反规则 1 或 2 → **WARNING**（视为交付前必改项：修正 HTML 叙述使其与 `financial_data.json` 对称一致；必要时同步 `financial_analysis.json` 等中间产出）。

---

### ✅ 10. 叙述结论必须有数据支撑（特别是估值/目标价/便宜或昂贵）

- 若 HTML 的摘要、投资逻辑、附录或风险提示中出现以下结论性措辞：`估值`、`市盈率`、`EV/EBITDA`、`目标价`、`upside`、`downside`、`cheap`、`expensive`、`low valuation`、`历史低位`、`高估/低估`，则必须在 `financial_analysis.json` → `valuation` 中存在对应非空字段，或在附录来源表中存在明确的市场数据来源。
- 若 `financial_analysis.json` → `valuation` 关键字段为 `null`，则 HTML 不得输出“估值低位”“目标价”“安全边际明确”等结论。
- 同理，若 HTML 引用“实时股价/最新市值/当前估值倍数”，应能在 JSON 或附录来源中定位到其来源和口径。

**失败条件：** 有结论但无数据支撑 → **WARNING**（视为交付前必改项）。

---

### ✅ 11. 来源与报告日一致性（禁止使用晚于报告日的来源冒充已验证事实）

- 读取 `report_date`（通常来自 HTML 页眉/文件夹日期）。
- 附录来源表、宏观说明、方法论、摘要中的“数据日期/来源”不得晚于 `report_date`，除非文本明确写明“预测/预计发布日期/知识截止估算”。
- 若 `macro_factors.json` / `news_intel.json` 明确写有 `knowledge-cutoff`, `estimate`, `无法执行实时网络搜索`, `无法实时检索` 等字样，HTML 不得写成“公开宏观数据已验证”“最新实时数据”“截至今日已确认”这类强口径表述；附录应相应降级为估算/非实时说明。
- 若 `data_source`/`data_source_note` 表示未联网或为估算，`confidence` 不得在 HTML/附录里包装为高置信度实时事实。

**附录「具体来源」列 — SEC 归因：**凡可追溯到 **EDGAR / sec.gov / data.sec.gov** 的申报正文（含 **Form 10-K 的 MD&A、附注如 Note 16 Revenue**），「具体来源」应标 **美国 SEC EDGAR**（括号可写章节/表单），**不得**仅以 `sec_edgar_bundle.json` 或脚本文件名作为唯一来源表述，以免读者误解为非 SEC 渠道。Bloomberg、Reuters、公司 IR 等非 SEC 首发渠道须标实名。

**页眉来源摘要长度：**`{{DATA_SOURCE}}` 只负责页眉短摘要，不承担附录级披露。若最终文本超过 **50 个字符**，即使语义正确，也视为**排版风险**，必须压缩为更短的并列表述，把细节下沉到附录来源表。

**失败条件：** 来源日期晚于报告日、或估算被写成已验证实时事实 → **WARNING**（视为交付前必改项）。附录将 SEC 申报误标为仅脚本/JSON、或将 SEC 内章节写成与 SEC 并列的虚构第三方 → **WARNING**（交付前必改）。页眉 `{{DATA_SOURCE}}` 超过 50 个字符 → **WARNING**（交付前必改）。

---

### ✅ 12. 地理口径与品牌/分部口径不得混用

- 第二节第四张趋势卡标题若为“最新经营更新 / Latest operating update”，正文须**明确**所写数据的**覆盖期间**（10-Q / TTM / YTD 等），且不得与「完整财年」同比口径混写而不加说明。
- 第二节第五张趋势卡标题若为“地区收入结构 / Geographic revenue mix”，正文只能出现地区/国家/区域层级项目。
- 不得在同一“地区收入结构”叙述中混入品牌、产品线、渠道等非地理维度标签（例如 `Converse`、`Footwear`、`Wholesale`）。
- 若公司披露将某品牌单列，而该品牌并非地区维度，应在别处说明，不能塞入地区列表冒充 region。

**失败条件：** 地理口径与品牌/分部口径混用 → **WARNING**（视为交付前必改项）。

---

### ✅ 13. 政策/关税叙述内部一致性

- 若摘要、风险、宏观因子表、方法论、`macro_factors.json`、`news_intel.json` 同时讨论同一政策冲击（如关税、监管、补贴），则国家/地区、时间点、税率或影响口径应一致。
- 可以有“主暴露地区”和“政策原始公告对象”的区别，但必须明确写清两者关系；不得在一处写“越南/印尼关税冲击”，另一处又只给出中国税率，却把它当成同一条证据链。
- 若定量冲击为估算，需明确标注“估算/情景假设/定性冲击”，避免把情景假设写成已落地精确事实。

**失败条件：** 同一政策叙述前后自相矛盾或证据链断裂 → **WARNING**（视为交付前必改项）。

---

### ✅ 14. QC 合议与成品一致性（若存在 `qc_audit_trail.json`）

- 若 `qc_audit_trail.json` 中某条 `verdict` 为 `accept_qc` 且列明了 `fields_changed`，最终 HTML / JSON 叙述应在相应主题上与裁定一致（例如已采纳的 β/叙事修正不得在五力或方法论中被无说明地推翻）。
- `prediction_waterfall.json` → `qc_deliberation.methodology_note` 应已并入附录 `{{METHODOLOGY_DETAIL}}`（或等价英文段落），不得遗漏。

**失败条件：** 审计轨迹显示已采纳修改但 HTML 仍为明显旧口径 → **WARNING**（交付前必改）。

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

--- 7e. 情报层信号与可执行投资逻辑 ---
[PASS] intelligence_signals 可追溯，投资逻辑包含监控变量 / 证伪条件 ✓

--- 8. 数字格式 ---
[PASS] 抽查5个数字，无NaN/undefined，格式规范 ✓

--- 8b. 财务指标表同比变动 ---
[PASS] 第四列为结论性定调，无裸百分比 ✓

--- 8c. 宏观因子表方向 ---
[PASS] 最后一列为正向/负向/中性，未重复调整幅度 ✓

--- 9. 分地区/分业务列举与 segment_data ---
[PASS] 无 segment_data，或列举格式对称 ✓
（或）[WARNING] 列举中部分分项带占比、部分不带 → 须补全或与 JSON 对齐后再交付

--- 10. 叙述结论支撑 ---
[PASS] 估值/目标价类结论均有 valuation 字段或附录来源支撑 ✓

--- 11. 来源与报告日一致性 ---
[PASS] 未发现晚于报告日的来源冒充已验证事实 ✓

--- 12. 地理口径一致性 ---
[PASS] 地区收入卡仅使用地区维度 ✓

--- 13. 政策/关税叙述一致性 ---
[PASS] 政策冲击口径前后一致 ✓

--- 14. QC 合议一致性（可选）---
[PASS] 无 qc_audit_trail.json，跳过 ✓
（或）[WARNING] 合议已采纳修改但附录/正文仍用旧口径 → 须对齐

=== 总结 ===
CRITICAL 错误：0
WARNING  警告：1
状态：⚠️ 通过（含警告）
```

并且必须在工作目录写出：

- `workspace/{Company}_{Date}/report_validation.txt`
- `workspace/{Company}_{Date}/structure_conformance.json`

## 处理逻辑

- 先执行 **第 0 项 packaging profile**：按 `workflow_meta.json` 选择 profile，完成产物对照、默认删除，并写出 `report_validation.txt` 与 `structure_conformance.json`。
- 若 profile 收口为 CRITICAL，继续完成本文件其余检查并在总结中明确“不可交付”。
- 若有 **CRITICAL** 错误：输出报告后，**立即修复 HTML 文件**，修复后重新运行验证直到0个CRITICAL为止。
- 若只有 **WARNING**：输出报告，提示 orchestrator 人工核查。若 WARNING 含 **第 7d / 7e / 8b / 8c / 9 / 10 / 11 / 12 / 13 项**，须在最终交付用户前修正 HTML（及与之绑定的 JSON 叙述），勿把内容性错误留给用户兜底。（第 10–13 项因难以自动化升格为 CRITICAL 而标为 WARNING，见上文 **「第 10–13 项与 WARNING 级别」**。）
- 若全部 PASS：输出报告，告知 orchestrator 报告质检通过。

## 修复优先级

修复时按以下顺序处理：
1. 残留占位符（`{{...}}`）→ 回头查 JSON 数据填充
2. 缺失 section → 补全对应 HTML 块
3. 图表数据格式错误 → 修正 JS 数据变量
4. KPI 卡片数量/class 错误 → 修正 HTML
5. score-dot 与数组不符 → 同步修正 HTML 和 JS
6. 第 7d / 7e 项：edge insight 或 intelligence signals 缺失 → 回填 `news_intel.json` / `edge_insights.json`，并同步摘要、趋势卡、投资逻辑、风险提示
7. 第 8b 项：财务指标表第 4 列为裸百分比 → 改成 `显著改善` / `改善` / `恶化` / `权益缺口收窄` 等结论性定调
8. 第 8c 项：宏观因子表方向列为裸百分比 → 第 5 列保留调整幅度，第 6 列改成 `正向` / `负向` / `中性`
9. 第 9 项：不对称的分项占比叙述 → 按 `segment_data` 补全括号内占比或整段改为仅金额
10. 第 10 项：无支撑的估值/目标价结论 → 删除结论或补充市场数据与来源
11. 第 11 项：来源日期或实时性表述错误 → 改写为估算/知识截止口径，或替换为报告日前已发布来源
12. 第 12 / 13 项：口径混用或政策叙述矛盾 → 统一维度、国家、时间点与假设表述
