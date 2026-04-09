# Equity Research Skill

An **equity research** skill pack for AI assistants such as **ChatGPT**, **Claude**, and **Cursor**. Give a **company name** and/or upload **financial statement PDFs** (e.g. U.S. **10-K / 10-Q**, Hong Kong or A-share annual / interim reports).

**Report language:** The orchestrator (**`SKILL.md`**) must **ask once** whether the final HTML should be **English** or **Chinese** if the user did not already specify. **Phase 1 must not start** until the user answers. Intermediate JSON and the final report match that language. **English** reports use the same layout as Chinese; output is `{Company}_Research_EN.html` (header: English name + ticker only). Chinese output remains `{Company}_Research_CN.html`.

The workflow collects data, runs financial and industry analysis, and produces **one interactive HTML research report** with a **Sankey revenue flow**, a **macro-factor waterfall chart**, and a **Porter Five Forces** radar.

**Repository:** [github.com/pppop00/Equity-Research-Skill](https://github.com/pppop00/Equity-Research-Skill)

---

## What you get

- **Single deliverable:** `{Company}_Research_CN.html` — open locally in a browser; light / dark theme toggle included.
- **Intermediate JSON:** financials, macro, news intel, prediction waterfall, Porter analysis — easy to audit or pipe into other tools.
- **Traceable process:** orchestration in **`SKILL.md`** at repo root; sub-tasks in **`agents/`**; formulas and sector β tables in **`references/`**.

> **Note:** Final deliverable is either `*_Research_CN.html` or `*_Research_EN.html` per user choice. Agent instructions may mix English and Chinese; templates are locked separately in `agents/report_writer_cn.md` and `agents/report_writer_en.md`.

---

## Repository layout (after clone or download)

```
Equity-Research-Skill/
├── SKILL.md                 # ★ Start here — main orchestration flow
├── README.md                # This file
├── agents/
│   ├── report_writer_cn.md  # ★ Locked Chinese HTML template
│   ├── report_writer_en.md  # ★ Locked English HTML template (same structure)
│   ├── report_validator.md # HTML structure / data checklist
│   ├── financial_data_collector.md
│   ├── macro_scanner.md
│   └── news_researcher.md
├── references/
│   ├── prediction_factors.md   # Macro model: φ, β, formulas
│   ├── porter_framework.md     # Porter Five Forces writing guide
│   ├── financial_metrics.md    # Metric definitions
│   ├── report_style_guide_cn.md
│   └── report_style_guide_en.md
└── workspace/                  # Example run outputs (`{Company}_{Date}/`, HTML + JSON)
```

> **Do not** change the HTML/CSS/JS skeleton inside `agents/report_writer_cn.md` or `agents/report_writer_en.md`. Dynamic content is injected **only** via placeholders; see the rules at the top of each file.

---

## How to use (by product)

### Common steps

1. **Clone** (or download ZIP and extract):
   ```bash
   git clone https://github.com/pppop00/Equity-Research-Skill.git
   cd Equity-Research-Skill
   ```
2. Add this repo to your AI session **context** (folder upload, `@` workspace, or open the project locally).
3. Instruct the model to **follow `SKILL.md` strictly** and, in Phase 5, to generate HTML using the **locked template** in **`agents/report_writer_cn.md`** or **`agents/report_writer_en.md`** (match the report language chosen in Phase 1).
4. Provide a **company name** and/or **filing PDFs**. Suggested output folder: `workspace/{Company}_{Date}/`.

### Cursor

- Open the directory containing **`SKILL.md`** as the workspace, or copy this repo into your project.
- Reference the skill in **Rules / Skills** (e.g. “for equity reports, read and execute `SKILL.md`”). You may also copy key points into `.cursor/rules`.
- Example: `@SKILL.md Build a Chinese HTML research report from the 2025 interim PDF I uploaded for company XXX.`

### Claude (web / Claude Code)

- **Claude Code:** Open the repo as a project; run the multi-agent steps described in `SKILL.md`.
- **Claude.ai:** Upload or paste `SKILL.md` plus relevant `agents/` and `references/` as project knowledge, then ask for phases in order (single thread if you do not use sub-agents).

### ChatGPT (web / desktop)

- Use **Advanced Data Analysis** (Code Interpreter) or **file upload**: ZIP `SKILL.md`, `agents/`, and `references/`, or paste the critical sections.
- Be explicit: **run the full `SKILL.md` pipeline**; for the final HTML step, **only** fill the template in `report_writer_cn.md` — do not rewrite the page structure.

---

## Input modes (from `SKILL.md`)

| Mode | Input | Notes |
|------|--------|--------|
| A | Company name only | More reliance on web research; some numbers are estimates — label confidence clearly. |
| B | Company name + annual-style PDF | Historical periods anchored to the file; forecasts blend macro and company-specific items. |
| C | Company name + multi-period PDFs | Richest factual basis. |

Hong Kong / A-share **interim and annual** reports also work as **file-mode** inputs. Validation targets the **locked HTML** contract.

---

## License and disclaimer

- Code and docs are licensed under **[Apache License 2.0](https://github.com/pppop00/Equity-Research-Skill/blob/main/LICENSE)** (same as the `LICENSE` file on GitHub).
- Reports are **model-generated research aids**, **not** investment advice. The prediction block is **illustrative / probabilistic** — always verify against original filings and regulatory disclosures.

---

## Contributing and feedback

- **Issues:** Template bugs, drift between `SKILL.md` and agents, or a product that cannot follow the flow — please open an **[Issue](https://github.com/pppop00/Equity-Research-Skill/issues)**.
- **Pull requests:** Copy improvements, β-table documentation, or best practices for non–U.S. filings are welcome; include a short rationale and how you tested.

---

To ship the locked template as a single **`.skill`** zip bundle, pack this directory according to your client’s skill-install guide and naming conventions.
