# Equity Research Skill

An **equity research** skill pack for AI assistants such as **ChatGPT**, **Claude**, and **Cursor**. Give a **company name** and/or upload **financial statement PDFs** (e.g. U.S. **10-K / 10-Q**, Hong Kong or A-share annual / interim reports).

**P0 gates (`SKILL.md` Step 0A.0):** Nothing else runs until (1) **report language** is **`en` or `zh`** per explicit cues in §0A.1 or the user’s answer to the language question, and (2) when the **SEC EDGAR API** path applies, the user supplies a **real email** or **explicitly declines** — **no** `workspace/`, **no** Phase 1, **no** company research before that. Do **not** infer language from chat language alone.

**Report language:** If the user did not use an explicit phrase from **`SKILL.md` §0A.1**, the orchestrator asks the single English/Chinese question and **stops** until answered. Intermediate JSON and the final report match that language. **English** output: `{Company}_Research_EN.html` (header: English name + ticker only). **Chinese:** `{Company}_Research_CN.html`.

**US SEC API (optional path):** For **Mode A** + **US-listed SEC filer**, the orchestrator **must** prompt for email (or accept decline) per **`SKILL.md` Step 0A.2** before research — never assume `no email` without an explicit user decline.

The workflow collects data, runs financial and industry analysis, and produces **one interactive HTML research report** with a **Sankey revenue flow**, a **macro-factor waterfall chart**, and a **Porter Five Forces** radar.

**Repository:** [github.com/pppop00/Equity-Research-Skill](https://github.com/pppop00/Equity-Research-Skill)

---

## What you get

- **Single deliverable:** `{Company}_Research_CN.html` — open locally in a browser; light / dark theme toggle included.
- **Intermediate JSON:** financials, macro, news intel, prediction waterfall, Porter analysis, optional **`qc_audit_trail.json`** after adversarial QC — easy to audit or pipe into other tools.
- **Traceable process:** orchestration in **`SKILL.md`** at repo root; sub-tasks in **`agents/`**; formulas and sector β tables in **`references/`**.

> **Note:** Final deliverable is either `*_Research_CN.html` or `*_Research_EN.html` per user choice. Agent instructions may mix English and Chinese; templates are locked separately in `agents/report_writer_cn.md` and `agents/report_writer_en.md`.

---

## Repository layout (after clone or download)

```
Equity-Research-Skill/
├── SKILL.md                 # ★ Start here — main orchestration flow
├── README.md                # This file
├── scripts/
│   └── extract_report_template.py  # ★ Extract locked HTML fenced block from report_writer_*.md (Phase 5)
├── tests/
│   └── test_extract_report_template.py  # CN/EN extraction + CLI + SHA256 snapshot tests
├── agents/
│   ├── report_writer_cn.md  # ★ Locked Chinese HTML template
│   ├── report_writer_en.md  # ★ Locked English HTML template (same structure)
│   ├── report_validator.md # HTML structure / data checklist
│   ├── financial_data_collector.md
│   ├── macro_scanner.md
│   ├── news_researcher.md
│   ├── qc_macro_peer_a.md / qc_macro_peer_b.md  # Adversarial QC on macro & prediction
│   ├── qc_porter_peer_a.md / qc_porter_peer_b.md  # Adversarial QC on Porter
│   └── qc_resolution_merge.md  # Merge QC challenges → updated JSON + qc_audit_trail.json
├── references/
│   ├── prediction_factors.md   # Macro model: φ, β, formulas
│   ├── porter_framework.md     # Porter Five Forces writing guide
│   ├── financial_metrics.md    # Metric definitions
│   ├── report_style_guide_cn.md
│   └── report_style_guide_en.md
└── workspace/                  # Example run outputs (`{Company}_{Date}/`, HTML + JSON)
```

> **Do not** change the HTML/CSS/JS skeleton inside `agents/report_writer_cn.md` or `agents/report_writer_en.md`. Dynamic content is injected **only** via placeholders; see the rules at the top of each file.

**Auditable HTML generation:** To reproduce the locked skeleton without copying another company’s finished report, run:

```bash
python3 scripts/extract_report_template.py --lang cn --sha256 -o workspace/MyCo_2026-04-08/_locked_cn_skeleton.html
# or: --lang en
```

Then replace `{{PLACEHOLDER}}` markers only. See `SKILL.md` Phase 5.

**Tests (template extract, Chinese + English):**

```bash
python3 -m unittest discover -s tests -v
```

If you change the fenced HTML inside `agents/report_writer_*.md`, update the expected SHA256 hashes in `tests/test_extract_report_template.py`.

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
