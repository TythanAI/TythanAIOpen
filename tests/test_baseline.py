# TythanAI Security Platform — Community Edition
# Copyright (c) 2026 TythanAI Labs
# Licensed under the Business Source License 1.1 (see LICENSE).

"""Tests for the CI baseline (suppress-known / gate-on-new)."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from community import baseline                       # noqa: E402
from community.scanner import CommunityScanner       # noqa: E402


def _scan(path):
    return CommunityScanner(str(path)).run(web3=False)


def test_fingerprint_is_line_independent(tmp_path):
    root = str(tmp_path)
    a = {"rule_id": "TYT-P005", "file": f"{root}/x.py", "cwe": "CWE-502",
         "title": "pickle", "line": 3, "evidence": "pickle.loads(b)"}
    b = dict(a, line=99)                              # same code, different line
    assert baseline.fingerprint(a, root) == baseline.fingerprint(b, root)


def test_fingerprint_differs_on_different_code(tmp_path):
    root = str(tmp_path)
    a = {"rule_id": "TYT-P005", "file": f"{root}/x.py", "cwe": "CWE-502",
         "title": "pickle", "evidence": "pickle.loads(a)"}
    b = dict(a, evidence="pickle.loads(other_source)")
    assert baseline.fingerprint(a, root) != baseline.fingerprint(b, root)


def test_record_then_suppress(tmp_path):
    (tmp_path / "app.py").write_text("import pickle\npickle.loads(x)\n")
    result = _scan(tmp_path)
    assert result.total >= 1

    bl = str(tmp_path / "base.json")
    saved = baseline.save(bl, result.all_findings, str(tmp_path))
    assert saved >= 1

    # A fresh scan of the same code should be fully suppressed by the baseline.
    result2 = _scan(tmp_path)
    suppressed = baseline.apply(result2, baseline.load(bl), str(tmp_path))
    assert suppressed >= 1
    assert result2.total == 0


def test_new_finding_survives_baseline(tmp_path):
    (tmp_path / "app.py").write_text("import pickle\npickle.loads(x)\n")
    result = _scan(tmp_path)
    bl = str(tmp_path / "base.json")
    baseline.save(bl, result.all_findings, str(tmp_path))

    # Introduce a genuinely different issue in a new file.
    (tmp_path / "new.py").write_text("def r(x):\n    return eval(x)\n")
    result2 = _scan(tmp_path)
    baseline.apply(result2, baseline.load(bl), str(tmp_path))
    titles = {f.get("title", "") for f in result2.all_findings}
    assert any("eval" in t.lower() for t in titles)


def test_missing_baseline_file_suppresses_nothing(tmp_path):
    (tmp_path / "app.py").write_text("import pickle\npickle.loads(x)\n")
    result = _scan(tmp_path)
    before = result.total
    suppressed = baseline.apply(result, baseline.load(str(tmp_path / "nope.json")),
                                str(tmp_path))
    assert suppressed == 0
    assert result.total == before
