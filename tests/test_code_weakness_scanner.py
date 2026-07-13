# TythanAI Security Platform — Community Edition
# Copyright (c) 2026 TythanAI Labs
# Licensed under the Business Source License 1.1 (see LICENSE).

"""Tests for the built-in offline SAST engine and its benchmark corpus."""
from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scanners.code_weakness_scanner import CodeWeaknessScanner, RULES  # noqa: E402


def _scan(tmp_path, name, code):
    p = tmp_path / name
    p.write_text(code)
    return CodeWeaknessScanner().scan_file(str(p))


def _cwes(findings):
    return {f["cwe"] for f in findings}


# ── Positive detections (Python) ──────────────────────────────────────────────

@pytest.mark.parametrize("name,code,cwe", [
    ("h.py", "import hashlib\nx = hashlib.md5(b).hexdigest()\n", "CWE-327"),
    ("h2.py", "import hashlib\nx = hashlib.new('sha1', b)\n", "CWE-327"),
    ("c.py", "from Crypto.Cipher import DES\nc = DES.new(k, DES.MODE_ECB)\n", "CWE-327"),
    ("t.py", "import requests\nrequests.get(u, verify=False)\n", "CWE-295"),
    ("p.py", "import pickle\npickle.loads(x)\n", "CWE-502"),
    ("y.py", "import yaml\nyaml.load(s)\n", "CWE-502"),
    ("e.py", "def f(x):\n    return eval(x)\n", "CWE-95"),
    ("o.py", "import os\nos.system('ping ' + h)\n", "CWE-78"),
    ("s.py", "import subprocess\nsubprocess.run(c, shell=True)\n", "CWE-78"),
    ("q.py", "def f(cur, i):\n    cur.execute(f'SELECT {i}')\n", "CWE-89"),
    ("q2.py", "def f(cur, n):\n    cur.execute('SELECT ' + n)\n", "CWE-89"),
])
def test_python_positive(tmp_path, name, code, cwe):
    findings = _scan(tmp_path, name, code)
    assert cwe in _cwes(findings), f"{name}: expected {cwe}, got {findings}"


# ── Positive detections (JavaScript) ──────────────────────────────────────────

@pytest.mark.parametrize("name,code,cwe", [
    ("e.js", "const r = eval(req.query.x);\n", "CWE-95"),
    ("c.js", "cp.exec(`ls ${d}`);\n", "CWE-78"),
    ("d.js", "el.innerHTML = `<b>${n}</b>`;\n", "CWE-79"),
    ("m.js", "crypto.createHash('md5').update(x);\n", "CWE-327"),
    ("t.js", "new https.Agent({ rejectUnauthorized: false });\n", "CWE-295"),
])
def test_js_positive(tmp_path, name, code, cwe):
    findings = _scan(tmp_path, name, code)
    assert cwe in _cwes(findings), f"{name}: expected {cwe}, got {findings}"


# ── Negative cases — correct code must not be flagged ─────────────────────────

@pytest.mark.parametrize("name,code", [
    ("ok_hash.py", "import hashlib\nx = hashlib.sha256(b).hexdigest()\n"),
    ("ok_tls.py", "import requests\nrequests.get(u, verify=True)\n"),
    ("ok_yaml.py", "import yaml\nyaml.safe_load(s)\n"),
    ("ok_yaml2.py", "import yaml\nyaml.load(s, Loader=yaml.SafeLoader)\n"),
    ("ok_sql.py", "def f(cur, i):\n    cur.execute('SELECT * FROM t WHERE id=?', (i,))\n"),
    ("ok_sub.py", "import subprocess\nsubprocess.run(['ls', '-l'])\n"),
    ("ok_eval.py", "import ast\nast.literal_eval(x)\n"),
    ("ok.js", "const r = JSON.parse(req.query.x);\nel.textContent = n;\n"),
    ("ok_tls.js", "new https.Agent({ rejectUnauthorized: true });\n"),
])
def test_negative_no_false_positive(tmp_path, name, code):
    assert _scan(tmp_path, name, code) == [], f"false positive in {name}"


# ── Robustness ────────────────────────────────────────────────────────────────

def test_syntax_error_is_ignored(tmp_path):
    # A file that does not parse must not raise — just yields nothing.
    assert _scan(tmp_path, "bad.py", "def (:\n  broken\n") == []


def test_non_source_file_skipped(tmp_path):
    assert _scan(tmp_path, "notes.txt", "eval(x)\n") == []


def test_every_finding_has_required_fields(tmp_path):
    findings = _scan(tmp_path, "app.py", "import pickle\npickle.loads(x)\n")
    assert findings
    for f in findings:
        assert f["rule_id"] in RULES
        assert f["severity"] in {"CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"}
        assert f["cwe"].startswith("CWE-")
        assert f["line"] >= 1
        assert f["title"]


def test_scan_directory_walks_and_skips_vendor(tmp_path):
    (tmp_path / "a.py").write_text("import os\nos.system(x)\n")
    vendor = tmp_path / "node_modules"
    vendor.mkdir()
    (vendor / "b.js").write_text("eval(x)\n")
    findings = CodeWeaknessScanner().scan_directory(str(tmp_path))
    files = {os.path.basename(f["file"]) for f in findings}
    assert "a.py" in files
    assert "b.js" not in files   # vendored dir is skipped


# ── The published scorecard must stay honest ──────────────────────────────────

def test_benchmark_scorecard_holds():
    """Modelled recall == 100%, zero false positives across the whole corpus."""
    from benchmarks.community_corpus import CASES, COVERAGE_GAPS
    scanner = CodeWeaknessScanner()

    def flags(code, lang):
        import tempfile
        ext = ".py" if lang == "python" else ".js"
        fd, path = tempfile.mkstemp(suffix=ext)
        try:
            with os.fdopen(fd, "w") as fh:
                fh.write(code)
            return scanner.scan_file(path)
        finally:
            os.unlink(path)

    modelled_tp = 0
    false_positives = []
    for cid, lang, cwe, vuln, secure in CASES:
        if any(f["cwe"] == cwe for f in flags(vuln, lang)):
            modelled_tp += 1
        if flags(secure, lang):
            false_positives.append(cid)
    for cid, lang, cwe, vuln, secure in COVERAGE_GAPS:
        if flags(secure, lang):
            false_positives.append(cid)

    assert false_positives == [], f"false positives: {false_positives}"
    assert modelled_tp == len(CASES), f"modelled recall dropped: {modelled_tp}/{len(CASES)}"
