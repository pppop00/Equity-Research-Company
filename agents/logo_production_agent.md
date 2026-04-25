# Agent: logo-production-agent

负责 Card1 公司 Logo 的高质量产出与元数据登记，供后续卡片渲染与 validator 校验使用。

## 触发时机（必须先于卡片渲染）

当本轮需要生成卡片素材（如 `*.card_slots.json`、`01_cover.png` 等）时，**先执行本 agent**，再做任何 Card1 绘制。

## 输入

- `workspace/{Company}_{Date}/.../*.card_slots.json`（至少包含 `logo_asset_path`）
- 公司名 / ticker（用于检索官方 logo）
- 可选：`logo_render_width_px`、`logo_render_height_px`（Card1 中 logo 最终显示尺寸）

## 输出

1. `logo_asset_path` 指向的高分辨率 `logo_official.png`（透明背景）
2. 在 `*.card_slots.json` 中写入或更新以下字段（供 validator 使用）：
   - `logo_render_width_px`
   - `logo_render_height_px`
   - `logo_export_width_px`
   - `logo_export_height_px`
   - `logo_scale_factor`

## 强制规则（P0）

1. **分辨率提升 2 倍（硬约束）**  
   `logo_export_width_px >= 2 * logo_render_width_px` 且  
   `logo_export_height_px >= 2 * logo_render_height_px`。  
   `logo_scale_factor` 必须写为 `2`（或更高）。

2. **默认槽位回退（无 render 尺寸时）**  
   若 `*.card_slots.json` 未提供 render 尺寸，使用默认槽位 `276x328`，则导出至少 `552x656`。

3. **禁止低质放大**  
   不得把明显低分辨率位图直接硬拉伸到目标尺寸。若原图不足，应优先获取官方高分辨率源或矢量源（SVG/PDF）再栅格化。

4. **透明背景与边缘质量**  
   输出必须保留透明背景；重采样使用高质量抗锯齿策略（如 Lanczos），避免 Card1 放大后出现明显锯齿边缘。

## 质量门槛（交付前）

- 若 `logo_scale_factor < 2`，或导出像素低于 2x 目标，视为不合格，需重做。
- 若无法获得足够清晰源图，需在对应 `notes` 字段明确记录限制，不得默默降级。

## Downstream Contract

- `report_validator` 在检测到 `*.card_slots.json` + `logo_asset_path` 时，会读取上述元数据并执行 2x 分辨率校验。
- 元数据缺失将触发 WARNING（交付前必改）。
