# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Run all tests:**
```bash
python3 -m unittest discover -s tests -v
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

## Architecture

This is an **AI skill pack** — not a traditional software application. The "code" is primarily markdown files that instruct AI assistants (Claude, ChatGPT, Cursor) how to produce equity research reports.

### Execution flow

1. **`SKILL.md`** — The orchestrator. An AI assistant reads and executes this as its instructions. It gates on language selection (EN/ZH), sets up a `workspace/{Company}_{Date}/` output folder, then coordinates parallel agents.
2. **`agents/`** — Sub-task instruction files. The orchestrator spawns or calls these (collectors in parallel; optional **dual QC** + **`qc_resolution_merge.md`**). Each produces JSON in the workspace.
3. **`references/`** — Domain knowledge: financial metric definitions, macro model formulas (φ, β), Porter Five Forces guide, style guides.
4. **Phase 5 (report generation)** — The AI fills `{{PLACEHOLDER}}` markers in the locked HTML template from `agents/report_writer_cn.md` or `agents/report_writer_en.md`. It must use `scripts/extract_report_template.py` to get the canonical skeleton rather than copying from an existing workspace HTML.

### The locked HTML templates

`agents/report_writer_cn.md` and `agents/report_writer_en.md` each contain a single ` ```html ``` ` fenced block — the locked interactive HTML skeleton with Sankey, waterfall, and Porter radar charts. **Do not change the structure**; only `{{PLACEHOLDER}}` substitutions are allowed.

`scripts/extract_report_template.py` extracts this block. The SHA256 hashes of the extracted bytes are pinned in `tests/test_extract_report_template.py`. If the templates change intentionally, update both the template and the expected hashes in `TestSha256Stable`.

### Key constraint: SHA256 snapshot tests

`TestSha256Stable` pins the exact bytes of both HTML templates. Any edit to the fenced block in `agents/report_writer_cn.md` or `agents/report_writer_en.md` will break these tests — this is intentional (audit trail). Update the expected digests in the test file when templates are deliberately changed.
