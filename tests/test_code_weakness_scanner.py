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
    ("q3.py", "def f(cur, i):\n    q = f'SELECT {i}'\n    cur.execute(q)\n", "CWE-89"),
    ("r.py", "import random\ntoken = str(random.randint(0, 9))\n", "CWE-330"),
    ("x.py", "from lxml import etree\netree.fromstring(data)\n", "CWE-611"),
    ("pt.py", "def r(req):\n    return open(req.args.get('f')).read()\n", "CWE-22"),
])
def test_python_positive(tmp_path, name, code, cwe):
    findings = _scan(tmp_path, name, code)
    assert cwe in _cwes(findings), f"{name}: expected {cwe}, got {findings}"


# ── Positive detections (Go) ──────────────────────────────────────────────────

@pytest.mark.parametrize("name,code,cwe", [
    ("h.go", "func f() { h := md5.New() }\n", "CWE-327"),
    ("t.go", "cfg := &tls.Config{InsecureSkipVerify: true}\n", "CWE-295"),
    ("c.go", "exec.Command(\"sh\", \"-c\", \"ls \"+dir)\n", "CWE-78"),
    ("q.go", "db.Query(\"SELECT * FROM u WHERE id = \" + id)\n", "CWE-89"),
])
def test_go_positive(tmp_path, name, code, cwe):
    findings = _scan(tmp_path, name, code)
    assert cwe in _cwes(findings), f"{name}: expected {cwe}, got {findings}"


# ── Positive detections (Java) ────────────────────────────────────────────────

@pytest.mark.parametrize("name,code,cwe", [
    ("h.java", "MessageDigest.getInstance(\"MD5\");\n", "CWE-327"),
    ("c.java", "Runtime.getRuntime().exec(\"ping \" + host);\n", "CWE-78"),
    ("q.java", "stmt.executeQuery(\"SELECT x FROM t WHERE id=\" + id);\n", "CWE-89"),
    ("d.java", "new ObjectInputStream(in).readObject();\n", "CWE-502"),
    ("r.java", "String token = String.valueOf(new Random().nextInt());\n", "CWE-330"),
])
def test_java_positive(tmp_path, name, code, cwe):
    findings = _scan(tmp_path, name, code)
    assert cwe in _cwes(findings), f"{name}: expected {cwe}, got {findings}"


# ── Positive detections (PHP / Ruby / C#) ─────────────────────────────────────

@pytest.mark.parametrize("name,code,cwe", [
    ("a.php", "<?php\n$h = md5($p);\n", "CWE-327"),
    ("b.php", "<?php\nsystem('ls ' . $dir);\n", "CWE-78"),
    ("c.php", "<?php\n$db->query(\"SELECT * FROM u WHERE id = $id\");\n", "CWE-89"),
    ("d.php", "<?php\n$o = unserialize($_GET['x']);\n", "CWE-502"),
    ("e.php", "<?php\neval($_GET['c']);\n", "CWE-95"),
    ("a.rb", "d = Digest::MD5.hexdigest(x)\n", "CWE-327"),
    ("b.rb", "system(\"ls #{dir}\")\n", "CWE-78"),
    ("c.rb", "User.where(\"name = '#{n}'\")\n", "CWE-89"),
    ("d.rb", "o = Marshal.load(x)\n", "CWE-502"),
    ("e.rb", "eval(params[:x])\n", "CWE-95"),
    ("a.cs", "var h = MD5.Create().ComputeHash(x);\n", "CWE-327"),
    ("b.cs", "Process.Start(\"ping \" + host);\n", "CWE-78"),
    ("c.cs", "var cmd = new SqlCommand(\"SELECT x WHERE id=\" + id, conn);\n", "CWE-89"),
    ("d.cs", "var o = new BinaryFormatter().Deserialize(s);\n", "CWE-502"),
])
def test_php_ruby_csharp_positive(tmp_path, name, code, cwe):
    findings = _scan(tmp_path, name, code)
    assert cwe in _cwes(findings), f"{name}: expected {cwe}, got {findings}"


# ── Positive detections (Kotlin / Rust / C++) ─────────────────────────────────

@pytest.mark.parametrize("name,code,cwe", [
    ("a.kt", "val md = MessageDigest.getInstance(\"MD5\")\n", "CWE-327"),
    ("b.kt", "Runtime.getRuntime().exec(\"ping \" + host)\n", "CWE-78"),
    ("c.kt", "stmt.executeQuery(\"SELECT x WHERE id = $id\")\n", "CWE-89"),
    ("d.kt", "val ois = ObjectInputStream(input)\n", "CWE-502"),
    ("a.rs", "let h = Md5::new();\n", "CWE-327"),
    ("b.rs", "Command::new(\"sh\").arg(format!(\"ls {}\", d));\n", "CWE-78"),
    ("c.rs", "sqlx::query(&format!(\"SELECT {}\", id));\n", "CWE-89"),
    ("a.cpp", "strcpy(dst, src);\n", "CWE-676"),
    ("b.cpp", "system((\"rm \" + p).c_str());\n", "CWE-78"),
    ("c.cpp", "MD5_Init(&ctx);\n", "CWE-327"),
])
def test_kotlin_rust_cpp_positive(tmp_path, name, code, cwe):
    findings = _scan(tmp_path, name, code)
    assert cwe in _cwes(findings), f"{name}: expected {cwe}, got {findings}"


# ── XPath (CWE-643) and LDAP (CWE-90) injection ───────────────────────────────

@pytest.mark.parametrize("name,code,cwe", [
    ("xp.py", "def f(t, n):\n    return t.xpath(f\"//u[@n='{n}']\")\n", "CWE-643"),
    ("xp.java", "Object r = xpath.evaluate(\"//u[@id='\" + id + \"']\", d);\n", "CWE-643"),
    ("xp.php", "<?php\n$n = $xml->xpath(\"//u[@n='$name']\");\n", "CWE-643"),
    ("xp.cs", "var n = doc.SelectNodes(\"//u[@id='\" + id + \"']\");\n", "CWE-643"),
    ("ld.py", "def f(c, b, u):\n    return c.search_s(b, S, \"(uid=\" + u + \")\")\n", "CWE-90"),
])
def test_xpath_ldap_positive(tmp_path, name, code, cwe):
    findings = _scan(tmp_path, name, code)
    assert cwe in _cwes(findings), f"{name}: expected {cwe}, got {findings}"


@pytest.mark.parametrize("name,code", [
    ("okxp.py", "def f(t, n):\n    return t.xpath(\"//u[@n=$n]\", n=n)\n"),
    ("okxp.php", "<?php\n$n = $xml->xpath(\"//u[@active='1']\");\n"),
    ("okxp.cs", "var n = doc.SelectNodes(\"//u[@active='1']\");\n"),
    ("okld.py", "import ldap.filter\ndef f(c, b, u):\n    return c.search_s(b, S, \"(uid=\" + ldap.filter.escape_filter_chars(u) + \")\")\n"),
])
def test_xpath_ldap_negative(tmp_path, name, code):
    assert _scan(tmp_path, name, code) == [], f"false positive in {name}"


# ── Cross-function (intra-module) dynamic SQL ─────────────────────────────────

def test_crossfunc_sql_flagged(tmp_path):
    code = ("def query(cur, sql):\n    cur.execute(sql)\n"
            "def h(cur, uid):\n    query(cur, f'SELECT {uid}')\n")
    assert "CWE-89" in _cwes(_scan(tmp_path, "cf.py", code))


def test_crossfunc_parameterised_helper_not_flagged(tmp_path):
    # A helper that parameterises (execute(sql, args)) is not a sink.
    code = ("def query(cur, sql, args):\n    cur.execute(sql, args)\n"
            "def h(cur, uid):\n    query(cur, f'SELECT {uid}', (uid,))\n")
    assert _scan(tmp_path, "cf2.py", code) == []


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
    ("ok_indirect.py", "def f(cur, i):\n    q = 'SELECT * FROM t WHERE id=?'\n    cur.execute(q, (i,))\n"),
    ("ok_random.py", "import secrets\ntoken = secrets.token_hex(16)\n"),
    ("ok_xxe.py", "from lxml import etree\netree.fromstring(data, safe_parser)\n"),
    ("ok_path.py", "import os\ndef r(req):\n    n = os.path.basename(req.args.get('f'))\n    return open(os.path.join(D, n)).read()\n"),
    ("ok.go", "func f() { h := sha256.New() }\ncfg := &tls.Config{InsecureSkipVerify: false}\n"),
    ("ok_sql.go", "db.Query(\"SELECT * FROM u WHERE id = $1\", id)\n"),
    ("ok.java", "MessageDigest.getInstance(\"SHA-256\");\n"),
    ("ok_rand.java", "String token = String.valueOf(new SecureRandom().nextInt());\n"),
    ("ok_random_nonsec.java", "int dieRoll = new Random().nextInt(6);\n"),
    ("ok.php", "<?php\n$h = password_hash($p, PASSWORD_DEFAULT);\n$s = $db->prepare(\"SELECT * FROM u WHERE id = ?\");\n"),
    ("ok.rb", "d = Digest::SHA256.hexdigest(x)\nUser.where(\"name = ?\", n)\n"),
    ("ok.cs", "var cmd = new SqlCommand(\"SELECT * FROM u WHERE id = @id\", conn);\n"),
    ("ok.kt", "val md = MessageDigest.getInstance(\"SHA-256\")\nconn.prepareStatement(\"SELECT * FROM u WHERE id = ?\")\n"),
    ("ok.rs", "let h = Sha256::new();\nCommand::new(\"ls\").arg(dir);\n"),
    ("ok.cpp", "strncpy(dst, src, n);\nexecvp(\"rm\", args);\nSHA256_Init(&ctx);\n"),
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

    ext_map = {"python": ".py", "javascript": ".js", "go": ".go", "java": ".java",
               "php": ".php", "ruby": ".rb", "csharp": ".cs",
               "kotlin": ".kt", "rust": ".rs", "cpp": ".cpp"}

    def flags(code, lang):
        import tempfile
        fd, path = tempfile.mkstemp(suffix=ext_map[lang])
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


def test_rules_doc_is_in_sync():
    """docs/RULES.md must match the rule catalogue (regenerate if this fails)."""
    from benchmarks import gen_rules_doc
    expected = gen_rules_doc.render()
    with open(gen_rules_doc._DOC_PATH, encoding="utf-8") as fh:
        assert fh.read() == expected, "run: python -m benchmarks.gen_rules_doc"


def test_every_rule_has_a_corpus_case():
    """Every rule id fires on at least one corpus vulnerable snippet."""
    import tempfile
    from benchmarks.community_corpus import CASES
    ext = {"python": ".py", "javascript": ".js", "go": ".go", "java": ".java",
           "php": ".php", "ruby": ".rb", "csharp": ".cs", "kotlin": ".kt",
           "rust": ".rs", "cpp": ".cpp"}
    scanner = CodeWeaknessScanner()
    fired = set()
    for _cid, lang, _cwe, vuln, _secure in CASES:
        fd, path = tempfile.mkstemp(suffix=ext[lang])
        try:
            with os.fdopen(fd, "w") as fh:
                fh.write(vuln)
            fired.update(f["rule_id"] for f in scanner.scan_file(path))
        finally:
            os.unlink(path)
    missing = set(RULES) - fired
    assert not missing, f"rules with no corpus coverage: {sorted(missing)}"
