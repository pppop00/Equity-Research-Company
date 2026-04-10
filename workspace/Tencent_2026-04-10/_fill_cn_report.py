#!/usr/bin/env python3
"""Fill Tencent (腾讯) CN report — FY2025 actual vs FY2026E forecast (SKILL Phase 5)."""
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
other_gross = max(0, gp - rd - sm - ga - op)

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
        {"name": "销售费用"},
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
    """Scale all link values by revenue ratio for forecast tab."""
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
        f'<li><span class="score-dot s{s}">{s}</span>{labels[i]}</li>'
        for i, s in enumerate(scores)
    )


p_c, p_i, p_f = [3, 4, 3, 4, 5], [4, 4, 3, 4, 5], [3, 4, 3, 4, 5]

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
<tr><td>利息保障倍数</td><td>{icr:.0f}×</td><td>—</td><td>营业利润/财务费用近似</td></tr>
<tr><td>每股收益（稀释）</td><td>{eps_c} 元</td><td>{eps_p} 元</td><td class="metric-up">约 +{fa['growth']['eps_growth_yoy_pct']:.1f}%</td></tr>
<tr><td>自由现金流利润率</td><td>{fcf_m}%</td><td>—</td><td>年报披露 FCF</td></tr>"""

appendix_rows = """<tr><td>法定披露</td><td>港交所 腾讯控股《截至2025年12月31日止年度业绩》及演示材料</td><td>2026-03-18</td><td>高</td></tr>
<tr><td>媒体报道</td><td>PR Newswire、财经媒体对 FY2025 业绩的整理</td><td>2026-03</td><td>中</td></tr>
<tr><td>β 与模型</td><td>references/prediction_factors.md（Communication Services）</td><td>内置</td><td>中</td></tr>"""

trend_map = {"positive": "up", "negative": "down", "neutral": "up"}

rep = {
    "COMPANY_NAME_CN": "腾讯",
    "COMPANY_NAME_EN": fd["company_en"],
    "TICKER": "0700",
    "EXCHANGE": "港交所",
    "SECTOR": "通信服务 / 数字内容",
    "REPORT_DATE": "2026年4月10日",
    "DATA_SOURCE": "港交所业绩公告、公司年报 PDF 及公开新闻整理",
    "RATING_CLASS": "neutral",
    "RATING_CN": "中性",
    "SUMMARY_PARA_1": (
        "腾讯控股是全球领先的互联网与数字内容平台，核心护城河为微信生态与长青游戏 IP。FY2025 营收约 7518 亿元，同比约 +14%；"
        "归母净利润约 2248 亿元，同比约 +16%。增值服务、营销服务（广告）与金融科技及企业服务为三大收入支柱，AI 已嵌入广告投放、云与企业产品提效。"
    ),
    "SUMMARY_PARA_2": (
        "盈利能力改善明显：毛利率约 56%，归母净利率约 30%；自由现金流约 1826 亿元，同比约 +18%，现金创造力仍强。"
        "全年资本开支约 792 亿元，管理层提示 AI 算力供给约束与 2026 年继续加码投入，利润增速可能阶段性慢于收入，是本报告核心跟踪矛盾。"
    ),
    "SUMMARY_PARA_3": (
        "本报告财务表采用 FY2025 对 FY2024（完整年报已发布）。收入预测财年与 Sankey 预测 tab 对齐为 FY2026E（相对 FY2025 的下一完整财年）。"
        f'宏观因子模型采用 Communication Services 行业 β、φ=0.5，示意营收增速约 +{pred["predicted_revenue_growth_pct"]:.2f}%，非卖方一致预期。'
    ),
    "HIGHLIGHTS_LI": """<li>FY2025 营销服务收入同比 +19%，AI 广告定向与视频号库存扩张为主要驱动</li>
<li>游戏本土与国际双线增长，国际游戏收入创历史新高</li>
<li>自由现金流同比 +18%，在创纪录 Capex 下仍保持强内生现金流</li>
<li>微信及 Weixin 合并月活约 14.2 亿，超级 App 商业闭环韧性突出</li>""",
    "RISKS_LI": """<li>AI 与云 Capex 上升可能压制短期利润率与 FCF 弹性</li>
<li>高端算力可得性与折旧节奏不确定</li>
<li>游戏版号、平台合规与未成年人保护政策仍可影响节奏</li>
<li>广告与游戏竞争加剧、用户时长被短视频等分流</li>
<li>宏观模型对以内需为主的现实传导有限，预测仅作示意</li>""",
    "INVESTMENT_THESIS": (
        "腾讯仍是中国数字商业基础设施级平台，利润与现金流质量在大型科技股中突出；AI 已实质性增厚广告与游戏效率，但重资产算力投入将考验 2026–2027 年盈利斜率。"
        "在估值与南向/全球资金风险偏好配合下，采用中性偏长期增持的行业视角，跟踪 Capex、云增速与监管三件套的边际变化。"
    ),
    "KPI1_DIRECTION": "up",
    "KPI1_VALUE": "7518亿元",
    "KPI1_CHANGE": "同比约 +13.9%",
    "KPI1_YEAR": "2025",
    "KPI2_DIRECTION": "up",
    "KPI2_VALUE": "2248亿元",
    "KPI2_CHANGE": "归母净利约 +15.9%",
    "KPI2_YEAR": "2025",
    "KPI3_DIRECTION": "up",
    "KPI3_VALUE": "1826亿元",
    "KPI3_CHANGE": "自由现金流约 +18%",
    "KPI3_YEAR": "2025",
    "KPI4_DIRECTION": "up",
    "KPI4_VALUE": f"{nm_c}%",
    "KPI4_CHANGE": "归母净利率同比小幅扩张",
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
        "桑基图「实际」基于 FY2025 合并利润表示意拆分（百万人民币），含研发/销售/管理及其他经营轧差至营业利润，底部「税及其他」连接归母净利润。"
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
        "本报告 Communication Services 默认 β。"
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

(out_path := ROOT / "Tencent_Research_CN.html").write_text(out, encoding="utf-8")
print(f"Wrote {out_path}")
