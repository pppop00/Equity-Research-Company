#!/usr/bin/env python3
"""Fill Alibaba (阿里巴巴) CN report — FY2025 actual vs FY2026E forecast (SKILL Phase 5)."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
fd = json.loads((ROOT / "financial_data.json").read_text(encoding="utf-8"))
pred = json.loads((ROOT / "prediction_waterfall.json").read_text(encoding="utf-8"))
macro = json.loads((ROOT / "macro_factors.json").read_text(encoding="utf-8"))
fa = json.loads((ROOT / "financial_analysis.json").read_text(encoding="utf-8"))
pa = json.loads((ROOT / "porter_analysis.json").read_text(encoding="utf-8"))
skel = (ROOT / "_locked_cn_skeleton.html").read_text(encoding="utf-8")

CY, PY = fd["income_statement"]["current_year"], fd["income_statement"]["prior_year"]
rev, rev_p = CY["revenue"], PY["revenue"]
growth_pct = pred["predicted_revenue_growth_pct"] / 100.0
rev_f = round(rev * (1 + growth_pct))

gp = CY["gross_profit"]
rd, sm, ga = CY["rd_expense"], CY["sm_expense"], CY["ga_expense"]
op = CY["operating_income"]
ni = CY["net_income"]
other_gross = gp - rd - sm - ga - op

wf = [
    {"label": "基准增长", "start": 0, "end": pred["baseline_revenue_growth_pct"], "value": pred["baseline_revenue_growth_pct"], "type": "baseline"},
    {
        "label": "宏观调整",
        "start": pred["baseline_revenue_growth_pct"],
        "end": round(pred["baseline_revenue_growth_pct"] + pred["macro_subtotal_pct"], 2),
        "value": pred["macro_subtotal_pct"],
        "type": "positive" if pred["macro_subtotal_pct"] >= 0 else "negative",
    },
    {
        "label": "公司特定",
        "start": round(pred["baseline_revenue_growth_pct"] + pred["macro_subtotal_pct"], 2),
        "end": round(pred["predicted_revenue_growth_pct"], 2),
        "value": pred["company_specific_adjustment_pct"],
        "type": "positive" if pred["company_specific_adjustment_pct"] >= 0 else "negative",
    },
    {"label": "预测结果", "start": 0, "end": round(pred["predicted_revenue_growth_pct"], 2), "value": round(pred["predicted_revenue_growth_pct"], 2), "type": "result"},
]
waterfall_js = json.dumps(wf, ensure_ascii=False)

tax_bridge = max(0, op - ni)

sankey_actual = {
    "nodes": [
        {"name": "营业收入"},
        {"name": "营业成本"},
        {"name": "毛利润"},
        {"name": "研发费用"},
        {"name": "销售与市场费用"},
        {"name": "管理费用"},
        {"name": "其他经营净损益"},
        {"name": "营业利润"},
        {"name": "税及其他"},
        {"name": "归母净利润"},
    ],
    "links": [
        {"source": 0, "target": 1, "value": CY["cogs"]},
        {"source": 0, "target": 2, "value": CY["gross_profit"]},
        {"source": 2, "target": 3, "value": rd},
        {"source": 2, "target": 4, "value": sm},
        {"source": 2, "target": 5, "value": ga},
        {"source": 2, "target": 6, "value": other_gross},
        {"source": 2, "target": 7, "value": op},
        {"source": 7, "target": 8, "value": tax_bridge},
        {"source": 7, "target": 9, "value": ni},
    ],
}

sf = lambda x: round(x * rev_f / rev)


def scale_sankey(base):
    out = {"nodes": json.loads(json.dumps(base["nodes"])), "links": []}
    for L in base["links"]:
        out["links"].append(
            {"source": L["source"], "target": L["target"], "value": sf(L["value"])}
        )
    return out


sankey_forecast = scale_sankey(sankey_actual)

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
        f'<li><span class="score-dot s{s}">{s}</span><span class="score-label">{labels[i]}</span></li>'
        for i, s in enumerate(scores)
    )


p_c, p_i, p_f = [3, 4, 4, 4, 4], [4, 4, 3, 4, 5], [3, 4, 4, 4, 4]

gm_c, gm_p = fa["profitability"]["gross_margin_current"], fa["profitability"]["gross_margin_prior"]
om_c, om_p = fa["profitability"]["operating_margin_current"], fa["profitability"]["operating_margin_prior"]
nm_c, nm_p = fa["profitability"]["net_margin_current"], fa["profitability"]["net_margin_prior"]
roe = fa["profitability"]["roe_current"]
roa = fa["profitability"]["roa_current"]
debt_r = round(
    (fd["balance_sheet"]["total_assets"] - fd["balance_sheet"]["total_equity"])
    / fd["balance_sheet"]["total_assets"]
    * 100,
    1,
)
icr = fa["leverage"]["interest_coverage_ratio"]
eps_c, eps_p = CY["diluted_eps"], PY["diluted_eps"]
fcf = fd["cash_flow"]["free_cash_flow"]
fcf_m = round(fcf / rev * 100, 1)

metrics_rows = f"""<tr><td>毛利率</td><td>{gm_c}%</td><td>{gm_p}%</td><td class="metric-up">{gm_c - gm_p:+.1f} pct</td></tr>
<tr><td>营业利润率</td><td>{om_c}%</td><td>{om_p}%</td><td class="metric-up">+{(om_c - om_p):.1f} pct</td></tr>
<tr><td>净利率（归母）</td><td>{nm_c}%</td><td>{nm_p}%</td><td class="metric-up">+{(nm_c - nm_p):.1f} pct</td></tr>
<tr><td>ROE（归属权益口径近似）</td><td>{roe}%</td><td>—</td><td>—</td></tr>
<tr><td>ROA</td><td>{roa}%</td><td>—</td><td>—</td></tr>
<tr><td>资产负债率</td><td>{debt_r}%</td><td>—</td><td>合并报表负债/资产</td></tr>
<tr><td>利息保障倍数</td><td>{icr:.1f}×</td><td>—</td><td>营业利润/利息费用</td></tr>
<tr><td>每股收益（稀释）</td><td>{eps_c} 元</td><td>{eps_p} 元</td><td class="metric-up">约 +{fa['growth']['eps_growth_yoy_pct']:.1f}%</td></tr>
<tr><td>自由现金流利润率</td><td>{fcf_m}%</td><td>—</td><td>年报披露 FCF</td></tr>"""

appendix_rows = """<tr><td>法定披露</td><td>港交所 9988 / Alibaba Group FY2025 业绩公告与 Form 20-F</td><td>2025-05</td><td>高</td></tr>
<tr><td>媒体报道</td><td>PR Newswire、财经媒体对 FY2025 业绩的整理</td><td>2025-05</td><td>中</td></tr>
<tr><td>β 与模型</td><td>references/prediction_factors.md（Consumer Discretionary + 大中华）</td><td>内置</td><td>中</td></tr>"""

trend_map = {"positive": "up", "negative": "down", "neutral": "up"}

rev_b = round(rev / 10000, 0)
ni_b = round(ni / 10000, 0)
fcf_b = round(fcf / 10000, 0)

rep = {
    "COMPANY_NAME_CN": "阿里巴巴",
    "COMPANY_NAME_EN": fd["company_en"],
    "TICKER": "9988",
    "EXCHANGE": "港交所",
    "SECTOR": "非必需消费 / 数字商业与云",
    "REPORT_DATE": "2026年4月10日",
    "DATA_SOURCE": "港交所业绩公告、公司年报及公开新闻整理",
    "RATING_CLASS": "neutral",
    "RATING_CN": "中性",
    "SUMMARY_PARA_1": (
        "阿里巴巴集团是中国与全球领先的数字商业与云计算基础设施平台之一，核心护城河为淘天、菜鸟、本地生活与云智能的协同网络。"
        f"FY2025（截至 2025-03-31）营收约 {rev_b:.0f} 亿元，同比约 +6%；归母净利润（普通股股东）约 {ni_b:.0f} 亿元，同比约 +6 成，含投资收益与公允价值变动影响。"
    ),
    "SUMMARY_PARA_2": (
        "盈利能力改善：毛利率约 40%，营业利润率约 14%；云与 AI 相关收入连续多季高增，国际数字商业收入同比约 +29%。"
        "同时，云基础设施资本开支显著上升，FY2025 自由现金流约 739 亿元，同比约 −53%，是本报告对利润与现金流跟踪的核心矛盾。"
    ),
    "SUMMARY_PARA_3": (
        "本报告财务表采用 FY2025 对 FY2024（完整年报已发布；财年截止 3 月 31 日）。收入预测财年与 Sankey 预测 tab 对齐为 FY2026E（下一完整财年截止 2026-03-31 的收入预测）。"
        f'第三节宏观因子表采用「大中华」主营业地序列（LPR、中国 GDP/CPI、美元兑人民币、布伦特油价、中国消费者信心等），Consumer Discretionary 行业 β、φ=0.5，'
        f'示意营收增速约 +{pred["predicted_revenue_growth_pct"]:.2f}%，非卖方一致预期。'
    ),
    "HIGHLIGHTS_LI": """<li>FY2025 云智能收入同比 +11%，AI 相关产品收入连续多季高速增长</li>
<li>淘宝天猫客户管理与变现效率改善，国际数字商业收入同比 +29%</li>
<li>全年回购与分红提升股东回报，流通股净减少</li>
<li>淘天、菜鸟、本地生活与云形成协同网络，规模与数据壁垒仍显著</li>""",
    "RISKS_LI": """<li>云与 AI Capex 上升压制自由现金流与短期利润率</li>
<li>国内电商与公有云竞争加剧，价格战与营销投入侵蚀利润</li>
<li>国际业务扩张与合规成本不确定</li>
<li>投资收益与市场波动影响归母净利波动</li>
<li>宏观因子模型为示意，国内传导与政策节奏可能与表内弹性不一致</li>""",
    "INVESTMENT_THESIS": (
        "阿里巴巴正处于「主业盈利修复 + 云 AI 再投资 + 股东回报」三条线的交叉期；中长期价值取决于云与 AI 收入能否覆盖算力折旧与资本开支，以及国际商业能否在减亏前提下扩大规模。"
        "在估值与南向资金偏好下，本报告采用中性评级，侧重跟踪 Capex、云增速与淘天利润率三条线的边际变化。"
    ),
    "KPI1_DIRECTION": "up",
    "KPI1_VALUE": f"{rev_b:.0f}亿元",
    "KPI1_CHANGE": "同比约 +6%",
    "KPI1_YEAR": "2025",
    "KPI2_DIRECTION": "up",
    "KPI2_VALUE": f"{ni_b:.0f}亿元",
    "KPI2_CHANGE": "归母净利同比大幅改善（含投资损益）",
    "KPI2_YEAR": "2025",
    "KPI3_DIRECTION": "down",
    "KPI3_VALUE": f"{fcf_b:.0f}亿元",
    "KPI3_CHANGE": "自由现金流同比约 −53%",
    "KPI3_YEAR": "2025",
    "KPI4_DIRECTION": "up",
    "KPI4_VALUE": f"{nm_c}%",
    "KPI4_CHANGE": "归母净利率同比明显扩张",
    "KPI4_PREV_VALUE": f"{nm_p}%",
    "METRICS_YEAR_CUR": "FY2025",
    "METRICS_YEAR_PREV": "FY2024",
    "METRICS_ROWS": metrics_rows,
    "TREND1_DIRECTION": trend_map[fa["trends"]["net_income"]["class"]],
    "TREND1_TEXT": fa["trends"]["net_income"]["analysis"],
    "TREND2_DIRECTION": trend_map[fa["trends"]["net_margin"]["class"]],
    "TREND2_TEXT": fa["trends"]["net_margin"]["analysis"],
    "TREND3_DIRECTION": trend_map[fa["trends"]["fcf"]["class"]],
    "TREND3_TEXT": fa["trends"]["fcf"]["analysis"],
    "GEO_REVENUE_TEXT": fa["geographic_revenue"]["analysis"],
    "PHI_VALUE": "0.5",
    "CONFIDENCE_CN": "中等",
    "PRED_FISCAL_YEAR": pred["predicted_fiscal_year_label"],
    "FACTOR_ROWS": factor_rows,
    "SANKEY_YEAR_ACTUAL": "FY2025",
    "SANKEY_YEAR_FORECAST": f'{pred["predicted_fiscal_year_label"]}（+{pred["predicted_revenue_growth_pct"]:.1f}%）',
    "SANKEY_ANALYSIS_TEXT": (
        "桑基图「实际」基于 FY2025 合并利润表示意拆分（百万人民币），研发费用、销售与市场、管理费用及无形资产摊销与商誉减值等并入「其他经营净损益」以轧差至营业利润；"
        "「税及其他」连接归母净利润。"
        f'「预测」为 {pred["predicted_fiscal_year_label"]}，按模型营收增速约 +{pred["predicted_revenue_growth_pct"]:.1f}% 同比缩放结构；非精确指引。'
    ),
    "PORTER_COMPANY_SCORES": porter_lis(p_c),
    "PORTER_COMPANY_TEXT": pa["company_level"],
    "PORTER_INDUSTRY_SCORES": porter_lis(p_i),
    "PORTER_INDUSTRY_TEXT": pa["industry_level"],
    "PORTER_FORWARD_SCORES": porter_lis(p_f),
    "PORTER_FORWARD_TEXT": pa["forward_looking"],
    "APPENDIX_SOURCE_ROWS": appendix_rows,
    "METHODOLOGY_DETAIL": (
        "本报告采用 Consumer Discretionary 默认 β。"
        f'基准增速 {pred["baseline_revenue_growth_pct"]}%；宏观合计 {pred["macro_subtotal_pct"]:+.2f} pct；'
        f'公司特定 {pred["company_specific_adjustment_pct"]:+.2f} pct；得 {pred["predicted_fiscal_year_label"]} 情景约 +{pred["predicted_revenue_growth_pct"]:.2f}%。'
    ),
    "WATERFALL_JS_DATA": waterfall_js,
    "SANKEY_ACTUAL_JS_DATA": json.dumps(sankey_actual, ensure_ascii=False),
    "SANKEY_FORECAST_JS_DATA": json.dumps(sankey_forecast, ensure_ascii=False),
    "PORTER_COMPANY_SCORES_ARRAY": json.dumps(p_c),
    "PORTER_INDUSTRY_SCORES_ARRAY": json.dumps(p_i),
    "PORTER_FORWARD_SCORES_ARRAY": json.dumps(p_f),
}

out = skel
for k in sorted(rep.keys(), key=len, reverse=True):
    out = out.replace("{{" + k + "}}", str(rep[k]))

left = re.findall(r"\{\{([A-Z_0-9]+)\}\}", out)
if left:
    raise SystemExit(f"Unresolved: {left}")

out = out.replace(
    "<!-- 填入 3-5 条，每条 <li>{{内容}}</li> -->",
    "<!-- highlights/risks li -->",
)

(out_path := ROOT / "Alibaba_Research_CN.html").write_text(out, encoding="utf-8")
print(f"Wrote {out_path}")
