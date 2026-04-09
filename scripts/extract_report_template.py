#!/usr/bin/env python3
"""
Extract the locked HTML skeleton from agents/report_writer_cn.md or report_writer_en.md.

This is the canonical, auditable starting point for Phase 5 report generation. Agents and
humans should fill {{PLACEHOLDER}} markers only — never copy structure from another
company's finished HTML in workspace/.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def default_md_path(lang: str) -> Path:
    lang = lang.lower().strip()
    if lang == "cn":
        return REPO_ROOT / "agents" / "report_writer_cn.md"
    if lang == "en":
        return REPO_ROOT / "agents" / "report_writer_en.md"
    raise ValueError("lang must be cn or en")


def extract_html_fenced(md_text: str) -> str:
    # First fenced block that opens with ```html (locked template is a single block)
    m = re.search(r"^```html\s*\r?\n(.*?\r?\n)```\s*", md_text, re.DOTALL | re.MULTILINE)
    if not m:
        raise ValueError("No ```html ... ``` fenced block found in markdown.")
    body = m.group(1).replace("\r\n", "\n").strip("\n")
    return body + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().split("\n")[0])
    p.add_argument(
        "--lang",
        choices=("cn", "en"),
        default="cn",
        help="Which agents/report_writer_{lang}.md to read (default: cn)",
    )
    p.add_argument(
        "--source",
        type=Path,
        help="Override markdown path (must still contain one ```html fenced block)",
    )
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Write extracted HTML to this file instead of stdout",
    )
    p.add_argument(
        "--sha256",
        action="store_true",
        help="Print SHA256 of extracted bytes to stderr (useful for audit logs)",
    )
    args = p.parse_args(argv)

    md_path = args.source.expanduser().resolve() if args.source else default_md_path(args.lang)
    if not md_path.is_file():
        print(f"error: markdown not found: {md_path}", file=sys.stderr)
        return 1

    md_text = md_path.read_text(encoding="utf-8")
    try:
        html = extract_html_fenced(md_text)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    raw = html.encode("utf-8")
    if args.sha256:
        h = hashlib.sha256(raw).hexdigest()
        print(f"sha256={h} bytes={len(raw)} source={md_path}", file=sys.stderr)

    if args.output:
        out = args.output.expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(raw)
        print(f"Wrote {len(raw)} bytes → {out}", file=sys.stderr)
    else:
        sys.stdout.buffer.write(raw)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
