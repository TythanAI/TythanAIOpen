# TythanAI Security Platform — Community Edition
# Copyright (c) 2026 TythanAI Labs
# Licensed under the Business Source License 1.1 (see LICENSE).

"""
community/baseline.py — suppress known findings so CI only fails on *new* ones.

A baseline is a small JSON file of finding fingerprints. A fingerprint is
line-independent (rule + relative path + CWE + title), so it survives code being
moved around within a file — only a genuinely new issue shows up as new.

Usage from the CLI:
    tythanai scan . --baseline .tythanai-baseline.json --update-baseline  # record
    tythanai scan . --baseline .tythanai-baseline.json                    # gate on new
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Iterable, Set


def fingerprint(finding: dict, root: str) -> str:
    """A stable, line-*independent* id for a finding.

    The key is rule + relative path + CWE + title + the normalised matched code
    (not the line number). Moving code within a file keeps the same fingerprint,
    but a genuinely different occurrence of the same rule gets its own id.
    """
    file = str(finding.get("file", ""))
    try:
        rel = str(Path(file).resolve().relative_to(Path(root).resolve()))
    except Exception:
        rel = Path(file).name or file
    evidence = re.sub(r"\s+", " ", str(finding.get("evidence", ""))).strip()
    key = "|".join([
        str(finding.get("rule_id", finding.get("id", ""))),
        rel,
        str(finding.get("cwe", "")),
        str(finding.get("title", finding.get("message", ""))),
        evidence,
    ])
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]


def load(path: str) -> Set[str]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return set(data.get("fingerprints", []))
    except Exception:
        return set()


def save(path: str, findings: Iterable[dict], root: str) -> int:
    fps = sorted({fingerprint(f, root) for f in findings})
    Path(path).write_text(
        json.dumps({"version": 1, "fingerprints": fps}, indent=2), encoding="utf-8")
    return len(fps)


_CATEGORIES = (
    "sast_findings", "sca_findings", "secrets_findings",
    "iac_findings", "web3_findings",
)


def apply(result, baseline_set: Set[str], root: str) -> int:
    """Drop findings present in the baseline from each category. Returns count."""
    suppressed = 0
    for attr in _CATEGORIES:
        kept = []
        for f in getattr(result, attr):
            if fingerprint(f, root) in baseline_set:
                suppressed += 1
            else:
                kept.append(f)
        setattr(result, attr, kept)
    return suppressed
