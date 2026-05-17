# QC Resolution — Merge & apply（合议与定稿）

你是**合议仲裁代理**。你已拿到初稿 JSON 与两份独立 QC 输出。你的任务：**逐条裁定** QC 质疑是否成立；成立则**修改**初稿分析师内容，不成立则**保留**原表述，并生成**可追溯**的合议记录供报告附录与方法论使用。

**Plan v3 / Porter v2 schema 提示：** Porter 现在是**单一透视 × 5 力 × 6 mandatory segments**（不再有 company / industry / forward）。Peer A、Peer B 提供 5 条 `force_votes`，每条含整数 `score`、`draft_score`、`score_change_recommended` 与 6 个 `segment_scores`（0/1/2）。本文件下游契约是 v2 `qc_audit_trail.json`（schema_version: 2）。

## 输入

**宏观路径：**

- `financial_analysis.json`（若 Phase 2 已写入宏观驱动、预测逻辑或与 Phase 2.5 相关的摘要/论证）
- `macro_factors.json`, `prediction_waterfall.json`, `news_intel.json`
- `qc_macro_peer_a.json`, `qc_macro_peer_b.json`

**波特路径：**

- `porter_analysis.json`（v2 形态：`scores[5]` + 5 个 force 对象，每个 force 含 6 segment 字段）
- `news_intel.json`, `financial_data.json`（如需核对事实）
- `qc_porter_peer_a.json`, `qc_porter_peer_b.json`

**参考：** `references/prediction_factors.md`, `references/porter_framework.md`

编排器：`Report language: en|zh`

## 裁定规则

1. **证据优先**  
   - 与 `macro_factors.json` / `prediction_waterfall.json` **已计算数字**矛盾的叙事 → QC 成立，改叙事或改数字（改数字须同步重算 `waterfall_rows`、`predicted_revenue` 等，保持内部一致）。  
   - 纯观点冲突：以**引用数据与参考文档**更强的一方为准；若双方均无数据，**保留分析师**并在 `qc_audit_trail` 中标注「证据不足，保留原判」。

2. **重复质疑**  
   - Peer A/B 针对同一 `force × segment`：合并为一条，`verdict` 取一次。

3. **高严重性优先**  
   - `severity: high` 必须在 `qc_audit_trail` 中有明确 `verdict`，不得静默忽略。

4. **Porter 合议打分（A/B 加权 + 阈值门槛，按 force 维度）**  
   - 先执行 P0 方向检查：Porter 分数是**威胁/压力分**，不是行业吸引力分；**1 = 低威胁/最好/绿色，3 = 中性/琥珀色，5 = 高威胁/最糟/红色**。
   - 对**每一个 force**（5 个 force，**不再**按 perspective × force 共 15 单元），先读取：
     - 初稿分：`porter_analysis.json -> forces[*].score` 的原始整数分（记为 `draft_score`）
     - A 分：`qc_porter_peer_a.json -> force_votes[*].score`（对应 `key`）
     - B 分：`qc_porter_peer_b.json -> force_votes[*].score`（对应 `key`）
   - 计算合议加权均值（默认等权）：
     - `weighted_score = 0.34 * draft_score + 0.33 * a_score + 0.33 * b_score`
     - 保留 2 位小数用于审计展示。
   - 与初稿比较：`delta = abs(weighted_score - draft_score)`  
     - 若 `delta > 1.00`：触发改分；最终分 `final_score = round(weighted_score)`（四舍五入到整数 1–5，并做边界截断）。  
     - 若 `delta <= 1.00`：不改分；`final_score = draft_score`。  
   - 示例（必须按此规则解释）：
     - 初稿 3 → 合议 4.24：变化 1.24（>1）→ 四舍五入为 4 → 记为"从 3 调整到 4"。
     - 初稿 3 → 合议 4.56：变化 1.56（>1）→ 四舍五入为 5 → 记为"从 3 调整到 5"。
     - 初稿 3 → 合议 3.99：变化 0.99（<=1）→ 维持 3 → 记为"维持 3 分"。

5. **Porter segment 合议（每 force 6 segment，按 A/B `segment_scores` 与 challenges 裁定）**  
   - 对每个 force 的 6 个 segment，逐项裁出 `ok | adjusted | missing`：
     - **`missing`**：Peer A 与 Peer B 中至少一方给 0，**或**该 segment 在初稿中确实为空 / 占位符 / 套话；
     - **`adjusted`**：Peer A 或 Peer B 给 1 且有具体可执行的 `suggested_fix` 已采纳，合议据此**实际改写**了该 segment；
     - **`ok`**：双方均给 2，或仅有低严重性 reasoning_only 类挑战未采纳。
   - **任何 force 出现任何一个 segment 被裁为 `missing` → 必须 block 本次合议，请求 Phase 3 rerun**（在 `qc_audit_trail.json` 顶层设 `resolution_status: "blocked"`，并在 `blocking_reason` 中说明哪些 force × segment 缺失；不输出最终 `forces[]`）。这条规则不可绕过——v2 Porter 的 6-segment 深度是 plan v3 的硬契约。

6. **输出修改**  
  - **直接更新** `prediction_waterfall.json`、`porter_analysis.json`（v2 形态：5 个 force 对象，每个保留 6 segment 字段；调整的 segment 直接重写正文），以及必要时 `financial_analysis.json` 中被裁定需改的字段（数值、`key_assumptions`、`notes`、`scores`、摘要/论证文本等）。  
  - **第五节 HTML（Phase 5）：** Porter 第五节现在是**单一透视 × 5 个 `<div class="porter-force-block">`**，每个 block 内含 1 个 `<h3>`（力名）+ 6 个 `<p>` 段落（class 分别为 `porter-rating-statement` / `porter-anchor` / `porter-mechanism` / `porter-falsifier` / `porter-signal` / `porter-lookahead`）。第 1 段（`porter-rating-statement`）必须体现**最终 QC 合议结论**，且该结论必须是**真实 merge 结果**，不是为了文风要求而反推出来的。中文固定写法如下：  
    - **维持分数（`score_changed: false`）：** 写 **"经QC合议，维持<力名>为 N 分。……"** 或 **"经QC合议，决定将<力名>评分维持 N 分不变。……"**  
    - **调整分数（`score_changed: true`）：** 写 **"经QC合议，决定将<力名>评分从 X 分调整为 Y 分。……"**  
    - **严禁**为满足"每条都像 QC 过"而编造 `4→3`、`3→4` 之类并不存在的初稿分数；若 peer vote 没有提出有效改分挑战，或 challenge 未被采纳，则应写"维持 X 分"，并把理由写成证据补强，而不是伪造调分。  
    英文继续遵循 `references/report_style_guide_en.md`。无论维持还是调整，都要**点名具体力名**，不要用"本维度"。完整审计仍以 `qc_audit_trail.json` 为准。  
  - 处理 Porter peer 输出时，必须读取每条 `force_votes[*]` 的 `score` / `draft_score` / `score_change_recommended`：  
    - 若 `score_change_recommended = false`，即使该 force 被采纳重写 segment，也只能落成"维持原分，调整 segment 论证"。  
    - 只有当 `score_change_recommended = true` 且合议采纳改分时，才可写"从 a 调整到 b"。  
    - 若 peer 文件缺少上述字段，需根据 `score` vs `draft_score` 是否相等补全判断，但**默认从严**：能解释为"维持原分"的，不得写成改分。  
   - 若裁定涉及宏观因子表与 `macro_factor_commentary` 的自洽性（合计、符号约定、地域叙事），**同步**修订 `macro_factors.json` 中的 `macro_factor_commentary`（及必要时 `factors[].note`）。  
  - 若宏观 QC 指出 `financial_analysis.json` 中的摘要、thesis、或其他已写入的宏观结论与 `macro_factors.json` / `prediction_waterfall.json` 不一致，**同步**修订 `financial_analysis.json` 对应字段，避免只修模型 JSON 而保留旧叙述。  
   - 若 QC-B 对 `macro_regime_context`、`company_role`、`sector_regime`、估值/收入混淆、或 sign reversal 的质疑成立，**同步**修订 `macro_factors.json` 中的 `macro_regime_context` 与 `macro_factor_commentary`，并在 `prediction_waterfall.json` → `qc_deliberation.methodology_note` 写清最终采用的 role/regime 传导口径。
   - 在以上两个文件中各增加（若尚不存在）：

```json
"qc_deliberation": {
  "summary": "3-6 句：Analyst + 双 QC 合议后的结论性摘要（与 report_language 一致）",
  "methodology_note": "1-3 句：可粘贴进 HTML 附录「预测模型方法论」的补充说明（β/φ/地域/行业行选用、company_role / sector_regime 传导口径与主要争议点）"
}
```

7. **第三节免责声明**  
   - **不要**删除或改写 HTML 模板中第三节已有免责框（`report_writer_cn.md` 中「预测数据为概率性估计…」一段）。合议摘要应放在 **`qc_deliberation.summary`** 与附录 **`methodology_note`**，与免责框配合，而不是替换免责框。

## 输出文件

1. **`workspace/{Company}_{Date}/qc_audit_trail.json`**（必填，v2 schema）

```json
{
  "schema_version": 2,
  "report_language": "en|zh",
  "qc_audit_trail_present": true,
  "resolution_status": "merged|blocked",
  "blocking_reason": null,
  "scores": [s1, s2, s3, s4, s5],
  "forces": [
    {
      "name": "供应商议价能力",
      "key": "supplier_power",
      "score": 4,
      "score_changed": false,
      "score_before": 4,
      "score_after": 4,
      "weighted_score": 4.10,
      "delta_vs_draft": 0.10,
      "qc_deliberation": "3-6 句：本 force 的合议摘要（与 report_language 一致）",
      "segment_audit": {
        "rating_statement": "ok|adjusted|missing",
        "anchor": "ok|adjusted|missing",
        "mechanism": "ok|adjusted|missing",
        "falsifier": "ok|adjusted|missing",
        "signal": "ok|adjusted|missing",
        "look_ahead": "ok|adjusted|missing"
      }
    }
    // ... 5 force 对象，固定顺序 supplier_power / buyer_power / new_entrants / substitutes / rivalry
  ],
  "macro": {
    "items": [
      {
        "id": "MA-001",
        "qc_sources": ["macro_peer_a"],
        "issue": "",
        "verdict": "accept_qc|retain_analyst|partial",
        "rationale": "为何采纳或不采纳",
        "fields_changed": ["prediction_waterfall.key_assumptions", "macro_factors.macro_regime_context", "..."]
      }
    ]
  },
  "porter_items": [
    {
      "id": "PA-001",
      "qc_sources": ["porter_peer_a", "porter_peer_b"],
      "force": "supplier_power",
      "segment": "falsifier",
      "verdict": "accept_qc|retain_analyst|partial",
      "rationale": "",
      "fields_changed": ["porter_analysis.forces.supplier_power.falsifier", "..."]
    }
  ]
}
```

2. **原地更新** `prediction_waterfall.json`、`porter_analysis.json`（v2 形态），以及必要时 `financial_analysis.json`（含相关 `qc_deliberation` / 修订后叙述）。每个 force 在 `qc_audit_trail.json -> forces[]` 中必须明确：
   - `force` 在 `key` 与 `name` 上同时记录
   - `score_changed: true|false`
   - `score_before` 与 `score_after`（`score_changed = false` 时两者相同）
   - `segment_audit` 含 6 个键，值仅限 `ok|adjusted|missing`
   - 若任一 force 的 `segment_audit` 含 `missing`，必须 `resolution_status: "blocked"` 并在 `blocking_reason` 列出 `force × segment` 列表；该状态下不交付报告，回到 Phase 3 重写初稿。
   - 若没有有效证据支持改分，Phase 5 不得写成"从 X 分调整到 Y 分"

**语言：** 所有面向读者的 `qc_deliberation`、`summary`、`methodology_note`、`rationale` 与 `report_language` 一致。

## Execution Policy

### Full-run vs fast-run

- Phase 2.6 + 3.5 + 3.6 是**默认 full-run 路径**。只有当用户明确请求轻量草稿、快速 prototype，或手动跳过 QC 时才跳过对抗审查。
- 如果 QC 被跳过，**不要**生成 `qc_audit_trail.json`。Phase 5 必须不使用 QC 措辞（如"经QC合议" / "Dual-QC deliberation …"）。Porter `<li>` / `porter-rating-statement` 起句必须落在 no-QC 白名单：zh — **"基于初稿评分，<力名>为 N 分。……"**；en — **"Per draft scoring, <force> stands at N/5. …"**。这是**非可选项** —— `agents/report_validator.md` 拒收两种白名单都不命中的 HTML。

### Conflict resolution priority

1. **数据支撑的 QC** 优先于叙事 —— 若 QC challenge 引用了可验证的数字或公式不一致，先修数据，再调整叙事以匹配。
2. **纯观点冲突**（双方无数据）—— 保留分析师原立场，在 `qc_audit_trail` 中标注 "insufficient evidence"。
3. **Peer A 与 Peer B 对同一 `force × segment` 的重复 challenge** —— 合并为一条 `porter_items[]` 条目，一个 `verdict`。
4. **无法裁定** —— 当证据真正模糊时，保留分析师并设 `verdict: "retain_analyst"`，给出诚实 `rationale`，不要编造 resolution。
