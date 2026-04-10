#!/usr/bin/env python3
"""One-off placeholder fill for OpenAI CN report from locked skeleton."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
skel = (ROOT / "_locked_cn_skeleton.html").read_text(encoding="utf-8")

pred = json.loads((ROOT / "prediction_waterfall.json").read_text(encoding="utf-8"))
macro = json.loads((ROOT / "macro_factors.json").read_text(encoding="utf-8"))
fa = json.loads((ROOT / "financial_analysis.json").read_text(encoding="utf-8"))

# --- JS structures ---
wf = [
    {"label": "基准增长", "start": 0, "end": pred["baseline_revenue_growth_pct"], "value": pred["baseline_revenue_growth_pct"], "type": "baseline"},
    {"label": "宏观调整", "start": pred["baseline_revenue_growth_pct"], "end": round(pred["baseline_revenue_growth_pct"] + pred["macro_subtotal_pct"], 2), "value": pred["macro_subtotal_pct"], "type": "positive"},
    {"label": "公司特定", "start": round(pred["baseline_revenue_growth_pct"] + pred["macro_subtotal_pct"], 2), "end": round(pred["predicted_revenue_growth_pct"], 2), "value": pred["company_specific_adjustment_pct"], "type": "positive"},
    {"label": "预测结果", "start": 0, "end": round(pred["predicted_revenue_growth_pct"], 2), "value": round(pred["predicted_revenue_growth_pct"], 2), "type": "result"},
]
waterfall_js = json.dumps(wf, ensure_ascii=False)

rev = 20000
growth = pred["predicted_revenue_growth_pct"] / 100.0
rev_f = round(rev * (1 + growth))
# Sankey: millions USD; positive EBIT stub for visualization (see note in HTML)
sankey_actual = {
    "nodes": [
        {"name": "年化收入（ARR示意）"},
        {"name": "算力与交付成本"},
        {"name": "毛利润"},
        {"name": "研发费用"},
        {"name": "销售与市场费用"},
        {"name": "一般及管理费用"},
        {"name": "营业利润（示意）"},
    ],
    "links": [
        {"source": 0, "target": 1, "value": 11000},
        {"source": 0, "target": 2, "value": 9000},
        {"source": 2, "target": 3, "value": 5000},
        {"source": 2, "target": 4, "value": 2200},
        {"source": 2, "target": 5, "value": 1500},
        {"source": 2, "target": 6, "value": 300},
    ],
}
scale = rev_f / rev
sf = lambda x: round(x * scale)
sankey_forecast = {
    "nodes": sankey_actual["nodes"][:],
    "links": [
        {"source": 0, "target": 1, "value": sf(11000)},
        {"source": 0, "target": 2, "value": sf(9000)},
        {"source": 2, "target": 3, "value": sf(5000)},
        {"source": 2, "target": 4, "value": sf(2200)},
        {"source": 2, "target": 5, "value": sf(1500)},
        {"source": 2, "target": 6, "value": sf(300)},
    ],
}

# Factor table rows (Technology β)
factor_rows = ""
for f in macro["factors"]:
    adj = f["adjustment_pct"]
    if adj > 0.05:
        direction = '<td class="metric-up">正向</td>'
    elif adj < -0.05:
        direction = '<td class="metric-down">负向</td>'
    else:
        direction = "<td>中性</td>"
    mc = f["factor_change_pct"]
    mc_s = f"{mc:+.2f}" if mc != 0 else "0.00"
    factor_rows += (
        f'<tr><td>{f["name"]}</td><td>{mc_s}</td><td>{f["beta"]}</td>'
        f'<td>{f["phi"]}</td><td>{adj:+.2f}</td>{direction}</tr>'
    )

def porter_lis(scores):
    labels = ["供应商议价能力", "买方议价能力", "新进入者威胁", "替代品威胁", "行业竞争强度"]
    return "".join(
        f'<li><span class="score-dot s{s}">{s}</span>{labels[i]}</li>'
        for i, s in enumerate(scores)
    )

p_c, p_i, p_f = [5, 3, 4, 4, 5], [5, 3, 4, 4, 5], [5, 3, 4, 5, 5]

metrics_rows = """<tr><td>毛利率（示意）</td><td>45.0%</td><td>40.0%</td><td class="metric-up">+5.0 pct</td></tr>
<tr><td>营业利润率（示意）</td><td>-2.5%</td><td>-33.3%</td><td class="metric-up">显著收窄但仍为负</td></tr>
<tr><td>净利率（示意）</td><td>-40.0%</td><td>-83.3%</td><td class="metric-up">亏损率略改善</td></tr>
<tr><td>ROE</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td>ROA</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td>资产负债率</td><td>—</td><td>—</td><td>未披露</td></tr>
<tr><td>利息保障倍数</td><td>—</td><td>—</td><td>未披露</td></tr>
<tr><td>每股收益（EPS）</td><td>不适用</td><td>不适用</td><td>私营</td></tr>
<tr><td>自由现金流利润率</td><td>负（推断）</td><td>负（推断）</td><td class="metric-down">高资本开支</td></tr>"""

appendix_rows = """<tr><td>官方/高管</td><td>OpenAI CFO 博文《A business that scales…》（2026-01-18）；企业侧公开 PDF 报告</td><td>2026-01</td><td>高（ARR 轨迹）</td></tr>
<tr><td>通讯社</td><td>Reuters 对 ARR 与融资报道</td><td>2026-01～03</td><td>中</td></tr>
<tr><td>科技媒体</td><td>Decrypt 等引述 CRO 企业收入占比</td><td>2026</td><td>中</td></tr>
<tr><td>社交媒体</td><td>X 上高管里程碑帖（需交叉验证口径）</td><td>2025～2026</td><td>低</td></tr>
<tr><td>β 与模型</td><td>references/prediction_factors.md（Technology）</td><td>内置</td><td>中</td></tr>"""

rep = {
    "COMPANY_NAME_CN": "OpenAI",
    "COMPANY_NAME_EN": "OpenAI, Inc.",
    "TICKER": "未上市",
    "EXCHANGE": "私营企业",
    "SECTOR": "科技 / 生成式 AI",
    "REPORT_DATE": "2026年4月10日",
    "DATA_SOURCE": "OpenAI 官方博文、路透社/科技媒体、X 高管披露与第三方统计交叉验证；利润表系示意",
    "RATING_CLASS": "neutral",
    "RATING_CN": "中性",
    "SUMMARY_PARA_1": "OpenAI 为未上市私营公司，无 SEC 10-K 类完整财务披露。本报告将首席财务官 Sarah Friar 于 2026 年 1 月在官网发布的 ARR 轨迹（约 20 亿→60 亿→200 亿+美元，2023–2025）作为核心收入锚，并与路透社、The Information、Decrypt 及 X 上高管帖文进行交叉验证；所有成本、利润与现金流数字均为媒体区间或模型示意，置信度标记为「低」。",
    "SUMMARY_PARA_2": "商业化结构正从「消费者订阅驱动」转向「企业 + API」更高 mix：Decrypt 等引述首席营收官称企业收入已超总收入四成，并预期 2026 年末与消费者侧接近均衡。与此同时，算力与研发投入同步飙升，媒体多次指公司仍处深度亏损与高现金消耗路径，须以未来 S-1 或完整审计报表为准。",
    "SUMMARY_PARA_3": "收入预测采用技能包宏观因子模型，行业 β 取 Technology；在 38% 的 ARR 基准增速（基数已大、主观下修）上叠加宏观与公司事件调整，得到 FY2027E 情景约 +40.9%（φ=0.5）。该预测对超高速增长私营公司仅作压力测试式示意，不构成估值或投资建议。",
    "HIGHLIGHTS_LI": """<li>官方披露 ARR 三年约 10×，与算力装机曲线强相关，社交媒体与新闻交叉印证斜率仍陡</li>
<li>企业侧收入占比快速上升，有助缓冲纯 C 端竞品与广告实验带来的波动</li>
<li>巨额私募融资与云生态合作在一定程度上保障 capacity 与渠道</li>
<li>全球多市场企业客户增速在公开 PDF 材料中有国别案例背书</li>""",
    "RISKS_LI": """<li>无经审计合并报表，社交/媒体报道口径（ARR、GAAP、递延收入）混用易导致误判</li>
<li>算力、电力与资本开支竞赛可能长期压制利润与现金流</li>
<li>监管、版权、数据合规与地缘因素或拖累跨国 ARPU</li>
<li>与微软等协议中的分成与结算可能使 headline 收入高于公司内部留存现金</li>
<li>宏观线性模型难以刻画 AI 需求非线性爆发或断崖</li>""",
    "INVESTMENT_THESIS": "在「能力—算力—商业化」飞轮仍同步加速的基准情景下，OpenAI 具备稀缺品牌与分发；但私营阶段信息严重不对称，宜把官方与社交披露视为方向性线索，而非精确财务。中性评级反映：上行在于企业工作流锁定与 ARPU；下行在于亏损持续性、监管与竞争降价。",
    "KPI1_DIRECTION": "up",
    "KPI1_VALUE": "约200亿美元",
    "KPI1_CHANGE": "ARR 同比约 +233%（CFO 口径 2024→2025）",
    "KPI1_YEAR": "2025（run-rate）",
    "KPI2_DIRECTION": "down",
    "KPI2_VALUE": "大额净亏损（示意）",
    "KPI2_CHANGE": "媒体称亏损随投入扩大；具体数以未披露为准",
    "KPI2_YEAR": "2025",
    "KPI3_DIRECTION": "down",
    "KPI3_VALUE": "显著为负（推断）",
    "KPI3_CHANGE": "无官方 FCF；CAPEX 军备竞赛",
    "KPI3_YEAR": "2025",
    "KPI4_DIRECTION": "up",
    "KPI4_VALUE": "-40%（示意）",
    "KPI4_CHANGE": "亏损率较 2024 示意值略有收敛",
    "KPI4_PREV_VALUE": "-83%（示意）",
    "METRICS_YEAR_CUR": "2025 run-rate",
    "METRICS_YEAR_PREV": "2024 run-rate",
    "METRICS_ROWS": metrics_rows,
    "TREND1_DIRECTION": "down",
    "TREND1_TEXT": fa["trends"]["net_income"]["analysis"],
    "TREND2_DIRECTION": "down",
    "TREND2_TEXT": fa["trends"]["net_margin"]["analysis"],
    "TREND3_DIRECTION": "down",
    "TREND3_TEXT": fa["trends"]["fcf"]["analysis"],
    "GEO_REVENUE_TEXT": fa["geographic_revenue"]["analysis"],
    "PHI_VALUE": "0.5",
    "CONFIDENCE_CN": "低",
    "PRED_FISCAL_YEAR": pred["predicted_fiscal_year_label"],
    "FACTOR_ROWS": factor_rows,
    "SANKEY_YEAR_ACTUAL": "2025 ARR",
    "SANKEY_YEAR_FORECAST": f'FY2027 情景（+{pred["predicted_revenue_growth_pct"]:.1f}%）',
    "SANKEY_ANALYSIS_TEXT": "私营公司无公开利润表；桑基图按「年化收入（ARR）—主要成本池—示意营业利润」拆解，金额单位百万美元，与 CFO 披露的约 200 亿美元量级一致。营业利润小正仅为绘图平衡项，不代表真实 GAAP；净亏损、税项与一次性项目在正文与 KPI 中另行说明。预测 tab 按约 +{:.1f}% 收入增速同比缩放。请勿将本图用于精密投研引用。".format(pred["predicted_revenue_growth_pct"]),
    "PORTER_COMPANY_SCORES": porter_lis(p_c),
}
pa = json.loads((ROOT / "porter_analysis.json").read_text(encoding="utf-8"))
rep["PORTER_COMPANY_TEXT"] = pa["company_level"]
rep["PORTER_INDUSTRY_SCORES"] = porter_lis(p_i)
rep["PORTER_INDUSTRY_TEXT"] = pa["industry_level"]
rep["PORTER_FORWARD_SCORES"] = porter_lis(p_f)
rep["PORTER_FORWARD_TEXT"] = pa["forward_looking"]
rep["APPENDIX_SOURCE_ROWS"] = appendix_rows
rep["METHODOLOGY_DETAIL"] = (
    "本报告采用 Technology 行业默认可 β。"
    f'基准增速 {pred["baseline_revenue_growth_pct"]}%；宏观合计 {pred["macro_subtotal_pct"]:+.2f} pct；'
    f'公司特定 {pred["company_specific_adjustment_pct"]:+.2f} pct；得 {pred["predicted_fiscal_year_label"]} 情景约 +{pred["predicted_revenue_growth_pct"]:.2f}%。'
    "私营公司与社交披露场景下，模型 Uncertainty 极高。"
)
rep["WATERFALL_JS_DATA"] = waterfall_js
rep["SANKEY_ACTUAL_JS_DATA"] = json.dumps(sankey_actual, ensure_ascii=False)
rep["SANKEY_FORECAST_JS_DATA"] = json.dumps(sankey_forecast, ensure_ascii=False)
rep["PORTER_COMPANY_SCORES_ARRAY"] = json.dumps(p_c)
rep["PORTER_INDUSTRY_SCORES_ARRAY"] = json.dumps(p_i)
rep["PORTER_FORWARD_SCORES_ARRAY"] = json.dumps(p_f)

# Replace longest keys first
out = skel
for k in sorted(rep.keys(), key=len, reverse=True):
    out = out.replace("{{" + k + "}}", str(rep[k]))

left = re.findall(r"\{\{([A-Z_0-9]+)\}\}", out)
if left:
    raise SystemExit(f"Unresolved placeholders: {left}")

out_path = ROOT / "OpenAI_Research_CN.html"
out_path.write_text(out, encoding="utf-8")
print(f"Wrote {out_path}")
