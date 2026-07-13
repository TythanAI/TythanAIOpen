# TythanAI Security Platform — Community Edition
# Copyright (c) 2026 TythanAI Labs
# Licensed under the Business Source License 1.1 (see LICENSE).

"""
benchmarks/gen_rules_doc.py — generate docs/RULES.md from the rule catalogue.

The built-in SAST engine's rules live in one place (``RULES`` in
``scanners/code_weakness_scanner.py``). This renders them into a human-readable
reference so the docs can never drift from the code. Run:

    python -m benchmarks.gen_rules_doc          # write docs/RULES.md
    python -m benchmarks.gen_rules_doc --check   # verify it is up to date (CI)
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scanners.code_weakness_scanner import RULES              # noqa: E402

_DOC_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "RULES.md")

# Rule-id prefix -> (language label, ordering key)
_PREFIX = {
    "TYT-P": ("Python", 0),
    "TYT-J": ("JavaScript / TypeScript", 1),
    "TYT-G": ("Go", 2),
    "TYT-A": ("Java", 3),
    "TYT-H": ("PHP", 4),
    "TYT-R": ("Ruby", 5),
    "TYT-C": ("C#", 6),
    "TYT-K": ("Kotlin", 7),
    "TYT-U": ("Rust", 8),
    "TYT-X": ("C / C++", 9),
}


def _language_of(rule_id: str) -> tuple:
    # Longest matching prefix wins (all are 5 chars here, but stay defensive).
    for prefix in sorted(_PREFIX, key=len, reverse=True):
        if rule_id.startswith(prefix):
            return _PREFIX[prefix]
    return ("Other", 99)


def render() -> str:
    groups: dict = {}
    for rid, meta in RULES.items():
        label, order = _language_of(rid)
        groups.setdefault((order, label), []).append((rid, meta))

    classes = sorted({m["cwe"] for m in RULES.values()})
    langs = [label for _, label in sorted(groups)]

    out = []
    out.append("# Built-in SAST rules")
    out.append("")
    out.append("> Auto-generated from `scanners/code_weakness_scanner.py` by "
               "`python -m benchmarks.gen_rules_doc`. Do not edit by hand.")
    out.append("")
    out.append(f"The offline engine ships **{len(RULES)} rules** across "
               f"**{len(langs)} languages** and **{len(classes)} CWE classes** "
               f"({', '.join(classes)}). Every rule runs with no external tools "
               "and no network, and each is exercised by the benchmark corpus "
               "(`python -m benchmarks.measure`).")
    out.append("")

    for (_, label), rows in sorted(groups.items()):
        out.append(f"## {label}")
        out.append("")
        out.append("| Rule | CWE | Severity | Detects |")
        out.append("|------|-----|----------|---------|")
        for rid, meta in sorted(rows):
            out.append(f"| `{rid}` | {meta['cwe']} | {meta['severity']} | {meta['title']} |")
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    content = render()
    check = "--check" in sys.argv
    if check:
        try:
            current = open(_DOC_PATH, encoding="utf-8").read()
        except OSError:
            current = ""
        if current != content:
            print("docs/RULES.md is out of date — run: python -m benchmarks.gen_rules_doc")
            return 1
        print("docs/RULES.md is up to date.")
        return 0
    os.makedirs(os.path.dirname(_DOC_PATH), exist_ok=True)
    with open(_DOC_PATH, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"Wrote {_DOC_PATH} ({len(RULES)} rules).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
