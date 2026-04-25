# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Run all tests:**
```bash
python3 -m unittest discover -s tests -v
```

**Validate machine-readable workflow contract:**
```bash
python3 scripts/validate_workflow_meta.py --meta workflow_meta.json
```

**Run a single test class or method:**
```bash
python3 -m unittest tests.test_extract_report_template.TestSha256Stable -v
python3 -m unittest tests.test_extract_report_template.TestSha256Stable.test_cn_hash_matches_known_snapshot -v
```

**Extract the locked HTML skeleton (for auditing or Phase 5 generation):**
```bash
python3 scripts/extract_report_template.py --lang cn --sha256 -o workspace/MyCo_2026-04-08/_locked_cn_skeleton.html
python3 scripts/extract_report_template.py --lang en --sha256 -o workspace/MyCo_2026-04-08/_locked_en_skeleton.html
```

**US SEC EDGAR bundle (Agent 1 API-first path; orchestrator obtains a real user email per `SKILL.md` Step 0A.2, then passes `--user-agent`):**
```bash
python3 scripts/sec_edgar_fetch.py --ticker MSFT --user-agent "EquityResearchSkill/1.0 (you@example.com)" --report-date 2026-04-11 -o workspace/Microsoft_2026-04-11/sec_edgar_bundle.json
```

## Architecture

This is an **AI skill pack** — not a traditional software application. The "code" is primarily markdown files that instruct AI assistants (Claude, ChatGPT, Cursor) how to produce equity research reports.

### Execution flow

1. **`workflow_meta.json`** — Machine-readable contract. Defines gate IDs, phase order, and Phase 6 packaging profiles (`strict_18_full_qc_secapi`, `strict_17_full_qc_no_secapi`, `strict_13_fast_no_qc_secapi`, `strict_12_fast_no_qc_no_secapi`).
2. **`SKILL.md`** — The orchestrator. An AI assistant reads and executes this as its instructions. **P0 gates (Step 0A.0):** resolve report language (`en`/`zh`) per explicit rules **and** resolve SEC email or explicit decline when §0A.2 applies — **before** `workspace/`, Phase 1, or any research. Then set up `workspace/{Company}_{Date}/` and coordinate parallel agents.
3. **`agents/`** — Sub-task instruction files. The orchestrator runs Phase 1 **Agents 1–3** in parallel (financials, macro, news); **Agent 4** (`edge_insight_writer.md`) may start once **Agents 1 and 3** finish, while Agent 2 may still be running; the standard full workflow then runs **dual QC on macro/Porter** followed by **`qc_resolution_merge.md`**. Phase 5 uses **`report_writer_*.md`**; **`final_report_data_validator.md`** performs the final professional data validation pass; **`report_validator.md`** performs final HTML structure / delivery validation and selects Phase 6 packaging profile from `workflow_meta.json`. Workspace holds JSON throughout (plus HTML after Phase 5). For Porter, scores are threat/pressure scores (**1–2 green low threat, 3 amber, 4–5 red high threat**); intense competitive rivalry must score high/red, not low/green. The Porter workflow is **draft → peer challenges → merge verdict → report wording**: only a QC item that **actually changes the score in the audit trail** may be written as **“from X to Y”**; reasoning-only QC that preserves the score must be written as **“maintain X”**, not as a fabricated score change. For revenue prediction, treat `news_intel.json` as the **raw event layer** and `prediction_waterfall.json` as the **final model layer**: when `company_events_detail[]` is present, it should bridge `raw_impact_pct` to `final_impact_pct` using explicit timing / overlap / run-rate / probability / realization fields so QC can recompute the final adjustment. Skip adversarial QC only in intentionally shortened runs.
4. **`references/`** — Domain knowledge: financial metric definitions, macro model formulas (φ, β), **sector regime / transmission** notes in `prediction_factors.md`, Porter Five Forces guide, style guides.
5. **Phase 5 (report generation)** — The AI fills `{{PLACEHOLDER}}` markers in the locked HTML template from `agents/report_writer_cn.md` or `agents/report_writer_en.md`. It must use `scripts/extract_report_template.py` to get the canonical skeleton rather than copying from an existing workspace HTML.

### The locked HTML templates

`agents/report_writer_cn.md` and `agents/report_writer_en.md` each contain a single ` ```html ``` ` fenced block — the locked interactive HTML skeleton with Sankey, waterfall, and Porter radar charts. **Do not change the structure**; only `{{PLACEHOLDER}}` substitutions are allowed.

`scripts/extract_report_template.py` extracts this block. The SHA256 hashes of the extracted bytes are pinned in `tests/test_extract_report_template.py`. If the templates change intentionally, update both the template and the expected hashes in `TestSha256Stable`.

### Key constraint: SHA256 snapshot tests

`TestSha256Stable` pins the exact bytes of both HTML templates. Any edit to the fenced block in `agents/report_writer_cn.md` or `agents/report_writer_en.md` will break these tests — this is intentional (audit trail). Update the expected digests in the test file when templates are deliberately changed.
