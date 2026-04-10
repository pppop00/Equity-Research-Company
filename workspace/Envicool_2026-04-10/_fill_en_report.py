#!/usr/bin/env python3
"""Fill Envicool (英维克) EN report placeholders from workspace JSON (SKILL Phase 5)."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
fd = json.loads((ROOT / "financial_data.json").read_text(encoding="utf-8"))
pred = json.loads((ROOT / "prediction_waterfall.json").read_text(encoding="utf-8"))
macro = json.loads((ROOT / "macro_factors.json").read_text(encoding="utf-8"))
fa = json.loads((ROOT / "financial_analysis.json").read_text(encoding="utf-8"))
skel = (ROOT / "_locked_en_skeleton.html").read_text(encoding="utf-8")

FACTOR_NAME_EN = {
    "联邦基金利率": "Federal funds rate",
    "美国实际 GDP 增速": "U.S. real GDP growth",
    "PCE 通胀": "PCE inflation",
    "美元指数 DXY": "U.S. dollar index (DXY)",
    "WTI 原油价格": "WTI crude oil",
    "美国消费者信心": "U.S. consumer confidence",
}

CY, PY = fd["income_statement"]["current_year"], fd["income_statement"]["prior_year"]
rev, rev_p = CY["revenue"], PY["revenue"]
growth_pct = pred["predicted_revenue_growth_pct"] / 100.0
rev_f = round(rev * (1 + growth_pct))

wf = [
    {"label": "Baseline growth", "start": 0, "end": pred["baseline_revenue_growth_pct"], "value": pred["baseline_revenue_growth_pct"], "type": "baseline"},
    {
        "label": "Macro adjustment",
        "start": pred["baseline_revenue_growth_pct"],
        "end": round(pred["baseline_revenue_growth_pct"] + pred["macro_subtotal_pct"], 2),
        "value": pred["macro_subtotal_pct"],
        "type": "positive" if pred["macro_subtotal_pct"] >= 0 else "negative",
    },
    {
        "label": "Company-specific",
        "start": round(pred["baseline_revenue_growth_pct"] + pred["macro_subtotal_pct"], 2),
        "end": round(pred["predicted_revenue_growth_pct"], 2),
        "value": pred["company_specific_adjustment_pct"],
        "type": "positive" if pred["company_specific_adjustment_pct"] >= 0 else "negative",
    },
    {"label": "Forecast", "start": 0, "end": round(pred["predicted_revenue_growth_pct"], 2), "value": round(pred["predicted_revenue_growth_pct"], 2), "type": "result"},
]
waterfall_js = json.dumps(wf, ensure_ascii=False)

sankey_actual = {
    "nodes": [
        {"name": "Revenue"},
        {"name": "Cost of revenue"},
        {"name": "Gross profit"},
        {"name": "R&D"},
        {"name": "Sales & marketing"},
        {"name": "G&A"},
        {"name": "Operating income"},
        {"name": "Taxes & other"},
        {"name": "Net income"},
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
    name_en = FACTOR_NAME_EN.get(f["name"], f["name"])
    if adj > 0.05:
        direction = '<td class="metric-up">Positive</td>'
    elif adj < -0.05:
        direction = '<td class="metric-down">Negative</td>'
    else:
        direction = "<td>Neutral</td>"
    mc = f["factor_change_pct"]
    mc_s = f"{mc:+.2f}" if mc != 0 else "0.00"
    factor_rows += (
        f"<tr><td>{name_en}</td><td>{mc_s}</td><td>{f['beta']}</td>"
        f"<td>{f['phi']}</td><td>{adj:+.2f}</td>{direction}</tr>"
    )


def porter_lis(scores):
    labels = [
        "Supplier power",
        "Buyer power",
        "New entrants",
        "Substitutes",
        "Industry rivalry",
    ]
    return "".join(
        f'<li><span class="score-dot s{s}">{s}</span>{labels[i]}</li>'
        for i, s in enumerate(scores)
    )


p_c, p_i, p_f = [4, 4, 3, 4, 5], [4, 4, 3, 4, 5], [4, 3, 3, 4, 5]

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

metrics_rows = f"""<tr><td>Gross margin</td><td>{gm_c}%</td><td>{gm_p}%</td><td class="metric-down">{gm_c - gm_p:+.1f} ppt</td></tr>
<tr><td>Operating margin</td><td>{om_c}%</td><td>{om_p}%</td><td class="metric-down">Slightly lower</td></tr>
<tr><td>Net margin</td><td>{nm_c}%</td><td>{nm_p}%</td><td class="metric-up">+{(nm_c - nm_p):.1f} ppt</td></tr>
<tr><td>ROE (approx.)</td><td>{roe}%</td><td>—</td><td>—</td></tr>
<tr><td>ROA</td><td>{roa}%</td><td>—</td><td>—</td></tr>
<tr><td>Debt-to-assets ratio</td><td>{debt_r}%</td><td>—</td><td>Annual report basis</td></tr>
<tr><td>Interest coverage</td><td>{icr:.0f}×</td><td>—</td><td>Illustrative</td></tr>
<tr><td>Diluted EPS (RMB)</td><td>{eps_c}</td><td>{eps_p}</td><td class="metric-up">~+{fa['growth']['eps_growth_yoy_pct']:.1f}% YoY</td></tr>
<tr><td>FCF margin</td><td>{fcf_m}%</td><td>—</td><td>Estimated</td></tr>"""

appendix_rows = """<tr><td>Regulatory filings</td><td>SZSE — Envicool 2024 annual report &amp; summary, 2025 Q3 report (CNINFO)</td><td>Apr 2025 / Oct 2025</td><td>High</td></tr>
<tr><td>Press</td><td>Xinhua Finance, Jiemian and other outlets summarizing 9M2025 results</td><td>Oct 2025</td><td>Medium</td></tr>
<tr><td>Investor Q&amp;A</td><td>Company disclosures on overseas revenue share (via periodic reports)</td><td>Apr 2025</td><td>Medium</td></tr>
<tr><td>Model</td><td>references/prediction_factors.md (Industrials row)</td><td>Built-in</td><td>Medium</td></tr>"""

trend_map = {"positive": "up", "negative": "down", "neutral": "up"}

porter_company = (
    "Shenzhen Envicool Technology is a leading domestic provider of precision thermal control and energy-saving equipment, "
    "with computer-room cooling still the largest revenue line in FY2024 and liquid cooling plus AI compute demand as the core narrative. "
    "The company bridges room-level and cabinet-level portfolios to serve hyperscale data centers and energy-storage installations. "
    "In FY2024 it posted roughly RMB 4.59 billion in revenue (about +30% YoY) and approximately RMB 453 million in net income (about +32% YoY), "
    "driven mainly by growth in IDC-related thermal products. Through 2025, top-line momentum remained strong in the first three quarters, "
    "but profit growth trailed revenue as gross margin faced pressure and operating expenses ran ahead—consistent with scaling capacity, "
    "project mix, and settlement timing. Operating cash flow weakened in FY2024 versus the prior year and turned negative in 9M2025; "
    "management attributed the swing largely to higher procurement and payroll tied to inventory and expansion. "
    "Overseas revenue as a share of sales has moved around year to year; the firm is investing in overseas subsidiaries to improve local delivery and after-sales coverage."
)

porter_industry = (
    "Compute and energy-storage capex are the twin demand engines for thermal management and heat rejection. "
    "Policy on data-center energy efficiency and power costs also shapes build-out cadence in China. "
    "The competitive landscape spans dedicated thermal vendors, broader electromechanical integrators, and offshore suppliers. "
    "Offerings are evolving from boxes to full systems and EPC-style solutions, while technology routes—air cooling upgrades, cold-plate liquid cooling, "
    "and immersion—fragment the market and drive price and standards competition. "
    "Large customers (cloud operators, carriers, and IDC developers) wield substantial procurement leverage through centralized tenders, "
    "so scale, reference projects, and on-time delivery matter as much as headline specification sheets."
)

porter_forward = (
    "If AI data-center capital spending remains elevated, adoption of advanced liquid cooling and high-density rack solutions can continue to rise, "
    "benefiting vendors with proven large-project track records. Conversely, a prolonged price war in cabinet thermal products or a softer energy-storage export cycle "
    "would test gross margin and working-capital efficiency. Geopolitics, tariffs, and trade rules remain swing factors for overseas storage and equipment flows. "
    "Hyperscale and colocation operators are also rebalancing regional capital plans; firms with international certifications and local service networks are better positioned "
    "if overseas AI data-center demand inflects. In sum, the demand story is constructive, but profitability, cash conversion, and competitive intensity warrant a neutral, "
    "evidence-based stance until FY2025 full-year results and margin trends are clearer."
)

rep = {
    "COMPANY_NAME_EN": fd["company_en"],
    "TICKER": fd["ticker"],
    "EXCHANGE": "SZSE",
    "SECTOR": "Industrials · Thermal management / data center cooling",
    "REPORT_DATE": "April 10, 2026",
    "DATA_SOURCE": "SZSE listings via CNINFO, company announcements, and public news",
    "RATING_CLASS": "neutral",
    "RATING_EN": "Neutral",
    "SUMMARY_PARA_1": (
        "Shenzhen Envicool Technology Co., Ltd. is a major China-based supplier of precision thermal control and data-center energy-saving solutions. "
        "In FY2024 consolidated revenue was about RMB 4.59 billion (~+30% YoY) and net profit attributable to shareholders about RMB 453 million (~+32% YoY). "
        "Computer-room thermal products remain the largest segment, with liquid cooling tied to AI compute as the central investment theme."
    ),
    "SUMMARY_PARA_2": (
        "On profitability, FY2024 gross and net margins were broadly stable versus the prior year, but 2025 shows a “faster revenue, slower profit” pattern: "
        "in 9M2025 revenue rose roughly +40% YoY while net profit rose only about +13%, with margin pressure and front-loaded costs in focus. "
        "Operating cash flow was negative in 9M2025; the company cited higher purchases and payroll—consistent with a growth-building phase rather than a steady-state cash profile."
    ),
    "SUMMARY_PARA_3": (
        "As of April 10, 2026 the company had not yet published a complete FY2025 annual report on CNINFO (the latest full-year filing remains FY2024), "
        "so the financial tables compare FY2024 to FY2023 per the skill calendar rule. The revenue forecast label and Sankey forecast tab align to FY2025E "
        "(the next full fiscal year after FY2024 actuals). The macro factor model uses the Industrials β vector with φ = 0.5, yielding an illustrative revenue growth scenario of "
        f"about +{pred['predicted_revenue_growth_pct']:.2f}%—not a consensus sell-side forecast."
    ),
    "HIGHLIGHTS_LI": """<li>FY2024: computer-room thermal revenue was still above half of sales; data-center and energy-storage demand reinforce the growth thesis</li>
<li>9M2025 revenue growth remained strong; contract liabilities and backlog indicators point to continued demand</li>
<li>End-to-end liquid cooling capabilities and large IDC reference projects support brand and delivery barriers</li>
<li>Overseas subsidiaries target international AIDC and energy-storage opportunities</li>""",
    "RISKS_LI": """<li>Prolonged gross-margin compression or price competition would limit operating leverage</li>
<li>Operating cash flow volatility raises working-capital and inventory-management risk</li>
<li>Trade policy, tariffs, and geopolitics may affect overseas energy-storage and equipment exposure</li>
<li>Goodwill and customer concentration have been historical disclosure themes—monitor M&amp;A assets and client mix</li>
<li>The linear macro model poorly captures domestic capex “pulse” effects</li>""",
    "INVESTMENT_THESIS": (
        "In a strong AI data-center and energy-storage build cycle, Envicool benefits from a broad product line and credible project history, "
        "which supports revenue visibility. Margin, cash conversion, and valuation constraints, however, argue for a neutral stance until profitability inflects and "
        "FY2025 annual disclosures reset the baseline."
    ),
    "KPI1_DIRECTION": "up",
    "KPI1_VALUE": "RMB 4.59 bn",
    "KPI1_CHANGE": "~+30.0% YoY",
    "KPI1_YEAR": "2024",
    "KPI2_DIRECTION": "up",
    "KPI2_VALUE": "RMB 453 m",
    "KPI2_CHANGE": "~+31.6% YoY",
    "KPI2_YEAR": "2024",
    "KPI3_DIRECTION": "down",
    "KPI3_VALUE": "RMB ~85 m",
    "KPI3_CHANGE": "FCF estimated; FY2024 operating cash flow weakened",
    "KPI3_YEAR": "2024",
    "KPI4_DIRECTION": "up",
    "KPI4_VALUE": f"{nm_c}%",
    "KPI4_CHANGE": "Broadly flat to slightly up vs. prior year",
    "KPI4_PREV_VALUE": f"{nm_p}%",
    "METRICS_YEAR_CUR": "FY2024",
    "METRICS_YEAR_PREV": "FY2023",
    "METRICS_ROWS": metrics_rows,
    "TREND1_DIRECTION": trend_map[fa["trends"]["net_income"]["class"]],
    "TREND1_TEXT": (
        "FY2024 net income was about RMB 453 million (~+31.6% YoY); non-GAAP-style recurring profit grew even faster, "
        "with IDC thermal products the main driver. In 2025, 9M profit growth lagged revenue as fees, mix, and timing interacted."
    ),
    "TREND2_DIRECTION": trend_map[fa["trends"]["net_margin"]["class"]],
    "TREND2_TEXT": (
        "FY2024 net margin was close to FY2023 at roughly 10%. In the first half of 2025 gross margin trended lower year on year as computer-room mix rose, "
        "which bears watching for the full year."
    ),
    "TREND3_DIRECTION": trend_map[fa["trends"]["fcf"]["class"]],
    "TREND3_TEXT": (
        "FY2024 operating cash flow was near RMB 200 million, down materially YoY; 9M2025 operating cash flow was negative as the company cited procurement and payroll—"
        "aligned with inventory build and expansion."
    ),
    "GEO_REVENUE_TEXT": (
        "The FY2024 annual summary does not break out complete domestic vs. overseas revenue in one line. "
        "Disclosures cited on the exchange: overseas revenue was about 18.0% of sales in FY2023; in H1 2024 overseas was about 16.1% with the mainland still the majority. "
        "More recent materials point to very strong mainland growth and a softer overseas contribution, with mainland share moving toward roughly nine-tenths of revenue. "
        "Use exchange filings as authoritative; this card describes mix only (no FX or DXY discussion)."
    ),
    "PHI_VALUE": "0.5",
    "CONFIDENCE_EN": "Medium",
    "PRED_FISCAL_YEAR": pred["predicted_fiscal_year_label"],
    "FACTOR_ROWS": factor_rows,
    "SANKEY_YEAR_ACTUAL": "FY2024",
    "SANKEY_YEAR_FORECAST": f'{pred["predicted_fiscal_year_label"]} (~+{pred["predicted_revenue_growth_pct"]:.1f}%)',
    "SANKEY_ANALYSIS_TEXT": (
        "Sankey “actual” restates FY2024 consolidated P&amp;L in RMB millions (illustrative split). "
        f'“Forecast” scales the same structure to {pred["predicted_fiscal_year_label"]} using model revenue growth of ~+{pred["predicted_revenue_growth_pct"]:.1f}% YoY. '
        "When FY2025 annual results are published, replace the actual tab with new filing data. Taxes &amp; other is a residual bridge."
    ),
    "PORTER_COMPANY_SCORES": porter_lis(p_c),
    "PORTER_COMPANY_TEXT": porter_company,
    "PORTER_INDUSTRY_SCORES": porter_lis(p_i),
    "PORTER_INDUSTRY_TEXT": porter_industry,
    "PORTER_FORWARD_SCORES": porter_lis(p_f),
    "PORTER_FORWARD_TEXT": porter_forward,
    "APPENDIX_SOURCE_ROWS": appendix_rows,
    "METHODOLOGY_DETAIL": (
        "This report uses the Industrials default β row from references/prediction_factors.md. "
        f'Baseline growth {pred["baseline_revenue_growth_pct"]}%; macro bucket +{pred["macro_subtotal_pct"]:.2f} ppt; '
        f'company-specific +{pred["company_specific_adjustment_pct"]:.2f} ppt; scenario for {pred["predicted_fiscal_year_label"]} ~+{pred["predicted_revenue_growth_pct"]:.2f}%.'
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

(out_path := ROOT / "Envicool_Research_EN.html").write_text(out, encoding="utf-8")
print(f"Wrote {out_path}")
