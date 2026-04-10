#!/usr/bin/env python3
"""Fill Envicool (英维克) CN report placeholders."""
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

wf = [
    {"label": "基准增长", "start": 0, "end": pred["baseline_revenue_growth_pct"], "value": pred["baseline_revenue_growth_pct"], "type": "baseline"},
    {"label": "宏观调整", "start": pred["baseline_revenue_growth_pct"], "end": round(pred["baseline_revenue_growth_pct"] + pred["macro_subtotal_pct"], 2), "value": pred["macro_subtotal_pct"], "type": "positive"},
    {"label": "公司特定", "start": round(pred["baseline_revenue_growth_pct"] + pred["macro_subtotal_pct"], 2), "end": round(pred["predicted_revenue_growth_pct"], 2), "value": pred["company_specific_adjustment_pct"], "type": "positive"},
    {"label": "预测结果", "start": 0, "end": round(pred["predicted_revenue_growth_pct"], 2), "value": round(pred["predicted_revenue_growth_pct"], 2), "type": "result"},
]
waterfall_js = json.dumps(wf, ensure_ascii=False)

sankey_actual = {
    "nodes": [
        {"name": "营业收入"},
        {"name": "营业成本"},
        {"name": "毛利润"},
        {"name": "研发费用"},
        {"name": "销售费用"},
        {"name": "管理费用"},
        {"name": "营业利润"},
        {"name": "税及其他"},
        {"name": "净利润"},
    ],
    "links": [
        {"source": 0, "target": 1, "value": CY["cogs"]},
        {"source": 0, "target": 2, "value": CY["gross_profit"]},
        {"source": 2, "target": 3, "value": CY["rd_expense"]},
        {"source": 2, "target": 4, "value": CY["sm_expense"]},
        {"source": 2, "target": 5, "value": CY["ga_expense"]},
        {"source": 2, "target": 6, "value": CY["operating_income"]},
        {"source": 6, "target": 7, "value": CY["operating_income"] - CY["net_income"]},
        {"source": 6, "target": 8, "value": CY["net_income"]},
    ],
}

sf = lambda x: round(x * rev_f / rev)
lnk7, lnk8 = sankey_actual["links"][-2]["value"], sankey_actual["links"][-1]["value"]
sankey_forecast = {
    "nodes": sankey_actual["nodes"][:],
    "links": [
        {"source": 0, "target": 1, "value": sf(CY["cogs"])},
        {"source": 0, "target": 2, "value": sf(CY["gross_profit"])},
        {"source": 2, "target": 3, "value": sf(CY["rd_expense"])},
        {"source": 2, "target": 4, "value": sf(CY["sm_expense"])},
        {"source": 2, "target": 5, "value": sf(CY["ga_expense"])},
        {"source": 2, "target": 6, "value": sf(CY["operating_income"])},
        {"source": 6, "target": 7, "value": sf(lnk7)},
        {"source": 6, "target": 8, "value": sf(lnk8)},
    ],
}

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
    return "".join(f'<li><span class="score-dot s{s}">{s}</span>{labels[i]}</li>' for i, s in enumerate(scores))


p_c, p_i, p_f = [4, 4, 3, 4, 5], [4, 4, 3, 4, 5], [4, 3, 3, 4, 5]

gm_c, gm_p = fa["profitability"]["gross_margin_current"], fa["profitability"]["gross_margin_prior"]
om_c, om_p = fa["profitability"]["operating_margin_current"], fa["profitability"]["operating_margin_prior"]
nm_c, nm_p = fa["profitability"]["net_margin_current"], fa["profitability"]["net_margin_prior"]
roe = fa["profitability"]["roe_current"]
roa = fa["profitability"]["roa_current"]
debt_r = round((fd["balance_sheet"]["total_assets"] - fd["balance_sheet"]["total_equity"]) / fd["balance_sheet"]["total_assets"] * 100, 1)
icr = fa["leverage"]["interest_coverage_ratio"]
eps_c, eps_p = CY["diluted_eps"], PY["diluted_eps"]
fcf = fd["cash_flow"]["free_cash_flow"]
fcf_m = round(fcf / rev * 100, 1)

metrics_rows = f"""<tr><td>毛利率</td><td>{gm_c}%</td><td>{gm_p}%</td><td class="metric-down">{gm_c - gm_p:+.1f} pct</td></tr>
<tr><td>营业利润率</td><td>{om_c}%</td><td>{om_p}%</td><td class="metric-down">略降</td></tr>
<tr><td>净利率</td><td>{nm_c}%</td><td>{nm_p}%</td><td class="metric-up">+{(nm_c - nm_p):.1f} pct</td></tr>
<tr><td>ROE（加权近似）</td><td>{roe}%</td><td>—</td><td>—</td></tr>
<tr><td>ROA</td><td>{roa}%</td><td>—</td><td>—</td></tr>
<tr><td>资产负债率</td><td>{debt_r}%</td><td>—</td><td>年报口径</td></tr>
<tr><td>利息保障倍数</td><td>{icr:.0f}×</td><td>—</td><td>示意</td></tr>
<tr><td>每股收益（EPS）</td><td>{eps_c} 元</td><td>{eps_p} 元</td><td class="metric-up">同比约 +{fa['growth']['eps_growth_yoy_pct']:.1f}%</td></tr>
<tr><td>自由现金流利润率</td><td>{fcf_m}%</td><td>—</td><td>估计值</td></tr>"""

appendix_rows = """<tr><td>法定披露</td><td>深交所 英维克 2024 年年度报告及摘要、2025 年三季报</td><td>2025-04 / 2025-10</td><td>高</td></tr>
<tr><td>媒体报道</td><td>新华财经、界面新闻等对 2025 三季报业绩整理</td><td>2025-10</td><td>中</td></tr>
<tr><td>互动平台</td><td>公司就境内外收入占比答复（转引定期报告）</td><td>2025-04</td><td>中</td></tr>
<tr><td>β 与模型</td><td>references/prediction_factors.md（Industrials）</td><td>内置</td><td>中</td></tr>"""

trend_map = {"positive": "up", "negative": "down", "neutral": "up"}

rep = {
    "COMPANY_NAME_CN": "英维克",
    "COMPANY_NAME_EN": fd["company_en"],
    "TICKER": "002837",
    "EXCHANGE": "深交所",
    "SECTOR": "工业 / 温控设备",
    "REPORT_DATE": "2026年4月10日",
    "DATA_SOURCE": "深交所定期报告、巨潮资讯及公开新闻整理",
    "RATING_CLASS": "neutral",
    "RATING_CN": "中性",
    "SUMMARY_PARA_1": "深圳市英维克科技股份有限公司为国内精密温控与数据中心节能解决方案主要供应商之一。FY2024 营业总收入约 45.89 亿元，同比约 +30.0%；归母净利润约 4.53 亿元，同比约 +31.6%。机房温控仍为第一大产品，液冷与算力需求为公司核心叙事。",
    "SUMMARY_PARA_2": "盈利侧，FY2024 毛利率与净利率基本稳健，但 2025 年以来出现「增收快于增利」特征：前三季度营收同比约 +40%，归母净利润同比约 +13%，毛利率承压与费用前置为市场关注焦点；经营性现金流在 2025 年前三季度转负，公司解释为采购与薪酬支出增加。需区分扩张期节奏与长期盈利能力。",
    "SUMMARY_PARA_3": "截至 2026 年 4 月 10 日公司尚未披露 FY2025 完整年报（巨潮最新年度报告仍为 2024 年度），故财务表维持 FY2024 对 FY2023。收入预测财年与 Sankey 预测 tab 对齐为 FY2025E（相对 FY2024 的下一完整财年），宏观因子模型 β 取 Industrials、φ=0.5，示意增速约 +22.1%，非卖方一致预期。",
    "HIGHLIGHTS_LI": """<li>FY2024 机房温控收入占比过半，数据中心与储能需求双轮驱动</li>
<li>2025 年前三季度收入延续高增，合同负债等指标反映在手需求</li>
<li>全链条液冷方案与大型 IDC 项目案例强化品牌与交付壁垒</li>
<li>海外子公司布局有望承接海外 AIDC 与储能订单</li>""",
    "RISKS_LI": """<li>毛利率回落与价格竞争若持续，将压制利润弹性</li>
<li>经营性现金流波动加大营运资本与备货管理难度</li>
<li>贸易政策、关税与地缘因素可能影响境外储能等业务</li>
<li>商誉减值与客户集中度高为历史关注点，需跟踪并购标的与客户结构</li>
<li>线性宏观模型难以刻画国内 Capex 脉冲式波动</li>""",
    "INVESTMENT_THESIS": "在智算与储能建设高景气阶段，英维克具备产品线齐全与项目履历优势，收入端能见度相对较高；但利润率、现金流与估值三重约束下，更适合以中性视角跟踪业绩兑现与毛利拐点，再等更清晰的风险溢价重估信号。",
    "KPI1_DIRECTION": "up",
    "KPI1_VALUE": "45.9亿元",
    "KPI1_CHANGE": "同比约 +30.0%",
    "KPI1_YEAR": "2024",
    "KPI2_DIRECTION": "up",
    "KPI2_VALUE": "4.53亿元",
    "KPI2_CHANGE": "同比约 +31.6%",
    "KPI2_YEAR": "2024",
    "KPI3_DIRECTION": "down",
    "KPI3_VALUE": "约0.85亿元",
    "KPI3_CHANGE": "FCF 为估计值；经营现金流 FY2024 已走弱",
    "KPI3_YEAR": "2024",
    "KPI4_DIRECTION": "up",
    "KPI4_VALUE": f"{nm_c}%",
    "KPI4_CHANGE": "同比大致持平略升",
    "KPI4_PREV_VALUE": f"{nm_p}%",
    "METRICS_YEAR_CUR": "FY2024",
    "METRICS_YEAR_PREV": "FY2023",
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
    "SANKEY_YEAR_ACTUAL": "FY2024",
    "SANKEY_YEAR_FORECAST": f'{pred["predicted_fiscal_year_label"]}（+{pred["predicted_revenue_growth_pct"]:.1f}%）',
    "SANKEY_ANALYSIS_TEXT": f"桑基图「实际」为 FY2024 合并报表示意拆分（百万人民币）。「预测」为 {pred['predicted_fiscal_year_label']}，按模型营收增速约 +{pred['predicted_revenue_growth_pct']:.1f}% 同比缩放；FY2025 完整年报披露后应以新数据替换实际 tab。税及其他为轧差近似。",
    "PORTER_COMPANY_SCORES": porter_lis(p_c),
    "PORTER_COMPANY_TEXT": pa["company_level"],
    "PORTER_INDUSTRY_SCORES": porter_lis(p_i),
    "PORTER_INDUSTRY_TEXT": pa["industry_level"],
    "PORTER_FORWARD_SCORES": porter_lis(p_f),
    "PORTER_FORWARD_TEXT": pa["forward_looking"],
    "APPENDIX_SOURCE_ROWS": appendix_rows,
    "METHODOLOGY_DETAIL": (
        "本报告 Industrials 默认 β。"
        f'基准增速 {pred["baseline_revenue_growth_pct"]}%；宏观合计 +{pred["macro_subtotal_pct"]:.2f} pct；'
        f'公司特定 +{pred["company_specific_adjustment_pct"]:.2f} pct；得 {pred["predicted_fiscal_year_label"]} 情景约 +{pred["predicted_revenue_growth_pct"]:.2f}%。'
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

out = out.replace("<!-- 填入 3-5 条，每条 <li>{{内容}}</li> -->", "<!-- highlights/risks li -->")

(out_path := ROOT / "Envicool_Research_CN.html").write_text(out, encoding="utf-8")
print(f"Wrote {out_path}")
