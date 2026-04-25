#!/usr/bin/env python3
"""
Validate workflow_meta.json structure for the Equity Research Skill.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_META = REPO_ROOT / "workflow_meta.json"

REQUIRED_TOP_KEYS = {
    "version",
    "description",
    "gates",
    "phase_order",
    "artifacts",
    "packaging_profiles",
    "default_cleanup_targets",
}

REQUIRED_ARTIFACT_KEYS = {
    "core",
    "locked_skeleton",
    "final_html",
    "sec_api_optional",
    "qc_optional",
}

REQUIRED_PROFILE_KEYS = {
    "requires_sec_api_bundle",
    "requires_qc_files",
    "required_files_zh",
    "required_files_en",
}


def _die(msg: str) -> int:
    print(f"ERROR: {msg}", file=sys.stderr)
    return 1


def _is_list_of_str(v: object) -> bool:
    return isinstance(v, list) and all(isinstance(x, str) and x for x in v)


def validate(path: Path) -> int:
    if not path.is_file():
        return _die(f"meta file not found: {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return _die(f"invalid JSON in {path}: {e}")

    if not isinstance(data, dict):
        return _die("top-level JSON must be an object")

    missing = sorted(REQUIRED_TOP_KEYS - set(data.keys()))
    if missing:
        return _die(f"missing top-level keys: {', '.join(missing)}")

    gates = data["gates"]
    if not isinstance(gates, list) or not gates:
        return _die("gates must be a non-empty array")
    for i, gate in enumerate(gates):
        if not isinstance(gate, dict):
            return _die(f"gates[{i}] must be an object")
        for k in ("id", "name", "must_resolve_before"):
            if k not in gate:
                return _die(f"gates[{i}] missing key: {k}")
        if not isinstance(gate["id"], str) or not gate["id"].strip():
            return _die(f"gates[{i}].id must be non-empty string")
        if not isinstance(gate["name"], str) or not gate["name"].strip():
            return _die(f"gates[{i}].name must be non-empty string")
        if not _is_list_of_str(gate["must_resolve_before"]):
            return _die(f"gates[{i}].must_resolve_before must be non-empty string array")

    if not _is_list_of_str(data["phase_order"]):
        return _die("phase_order must be a non-empty string array")

    artifacts = data["artifacts"]
    if not isinstance(artifacts, dict):
        return _die("artifacts must be an object")
    missing_artifact_keys = sorted(REQUIRED_ARTIFACT_KEYS - set(artifacts.keys()))
    if missing_artifact_keys:
        return _die(f"artifacts missing keys: {', '.join(missing_artifact_keys)}")
    for k in REQUIRED_ARTIFACT_KEYS:
        if not _is_list_of_str(artifacts[k]):
            return _die(f"artifacts.{k} must be a non-empty string array")

    profiles = data["packaging_profiles"]
    if not isinstance(profiles, dict) or not profiles:
        return _die("packaging_profiles must be a non-empty object")

    allowed_files = set()
    for vals in artifacts.values():
        allowed_files.update(vals)
    allowed_files.add("report_validation.txt")
    allowed_files.add("structure_conformance.json")

    for profile_name, profile in profiles.items():
        if not isinstance(profile, dict):
            return _die(f"profile {profile_name} must be an object")
        missing_profile_keys = sorted(REQUIRED_PROFILE_KEYS - set(profile.keys()))
        if missing_profile_keys:
            return _die(
                f"profile {profile_name} missing keys: {', '.join(missing_profile_keys)}"
            )
        if not isinstance(profile["requires_sec_api_bundle"], bool):
            return _die(f"profile {profile_name}.requires_sec_api_bundle must be boolean")
        if not isinstance(profile["requires_qc_files"], bool):
            return _die(f"profile {profile_name}.requires_qc_files must be boolean")
        for lang_key in ("required_files_zh", "required_files_en"):
            files = profile[lang_key]
            if not _is_list_of_str(files):
                return _die(f"profile {profile_name}.{lang_key} must be non-empty string array")
            if "report_validation.txt" not in files:
                return _die(f"profile {profile_name}.{lang_key} must include report_validation.txt")
            if "structure_conformance.json" not in files:
                return _die(f"profile {profile_name}.{lang_key} must include structure_conformance.json")
            unknown = [
                f
                for f in files
                if f not in allowed_files
                and not f.startswith("{Company}_Research_")
                and not f.startswith("_locked_")
            ]
            if unknown:
                return _die(
                    f"profile {profile_name}.{lang_key} contains unknown file(s): {', '.join(unknown)}"
                )

    if not _is_list_of_str(data["default_cleanup_targets"]):
        return _die("default_cleanup_targets must be a non-empty string array")

    print(f"OK: {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate workflow_meta.json")
    parser.add_argument(
        "--meta",
        type=Path,
        default=DEFAULT_META,
        help=f"Path to workflow meta file (default: {DEFAULT_META})",
    )
    args = parser.parse_args(argv)
    return validate(args.meta.expanduser().resolve())


if __name__ == "__main__":
    raise SystemExit(main())
