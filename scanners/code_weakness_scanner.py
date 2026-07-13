# TythanAI Security Platform — Community Edition
# Copyright (c) 2026 TythanAI Labs
# Licensed under the Business Source License 1.1 (see LICENSE).

"""
scanners/code_weakness_scanner.py — built-in, offline SAST rule engine.

Dependency-free static checks for the weakness classes that a taint engine
*doesn't* model (weak crypto, insecure deserialization, disabled TLS
verification, code/command injection, dynamic SQL). Python is analysed with
the `ast` module (structural, low false-positive); JavaScript/TypeScript with
a small set of conservative line patterns.

This runs with **no network and no external tools**, so `tythanai scan`
always produces SAST results even when Semgrep is not installed. When Semgrep
*is* available its findings are merged on top for breadth.

Every rule is anchored to a CWE and exercised by the benchmark corpus in
`benchmarks/` — see `python -m benchmarks.measure`.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Callable, Dict, List, Optional

# ── File selection ────────────────────────────────────────────────────────────

_PY_EXTS = {".py", ".pyi"}
_JS_EXTS = {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx"}
_SKIP_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv", "env",
    "dist", "build", ".tox", ".mypy_cache", ".pytest_cache", "site-packages",
}
_MAX_FILE_BYTES = 1_500_000


# ── Rule catalogue (id → CWE, severity, human title) ──────────────────────────

RULES: Dict[str, Dict[str, str]] = {
    # Python
    "TYT-P001": {"cwe": "CWE-327", "severity": "MEDIUM", "title": "Weak hash algorithm (MD5/SHA-1)"},
    "TYT-P002": {"cwe": "CWE-327", "severity": "HIGH",   "title": "Broken/weak cipher (DES/RC4/RC2/Blowfish)"},
    "TYT-P003": {"cwe": "CWE-327", "severity": "MEDIUM", "title": "Insecure ECB cipher mode"},
    "TYT-P004": {"cwe": "CWE-295", "severity": "HIGH",   "title": "TLS certificate verification disabled"},
    "TYT-P005": {"cwe": "CWE-502", "severity": "HIGH",   "title": "Unsafe deserialization (pickle/marshal)"},
    "TYT-P006": {"cwe": "CWE-502", "severity": "HIGH",   "title": "Unsafe YAML load (arbitrary object construction)"},
    "TYT-P007": {"cwe": "CWE-95",  "severity": "HIGH",   "title": "Code injection via eval()/exec()"},
    "TYT-P008": {"cwe": "CWE-78",  "severity": "HIGH",   "title": "OS command execution (os.system/os.popen)"},
    "TYT-P009": {"cwe": "CWE-78",  "severity": "HIGH",   "title": "subprocess with shell=True"},
    "TYT-P010": {"cwe": "CWE-89",  "severity": "HIGH",   "title": "SQL built from dynamic string (injection)"},
    "TYT-P011": {"cwe": "CWE-79",  "severity": "MEDIUM", "title": "Template/markup rendered from dynamic input (XSS/SSTI)"},
    # JavaScript / TypeScript
    "TYT-J001": {"cwe": "CWE-95",  "severity": "HIGH",   "title": "Code injection via eval()"},
    "TYT-J002": {"cwe": "CWE-78",  "severity": "HIGH",   "title": "Command execution with interpolated input"},
    "TYT-J003": {"cwe": "CWE-79",  "severity": "MEDIUM", "title": "innerHTML assigned dynamic content (DOM XSS)"},
    "TYT-J004": {"cwe": "CWE-327", "severity": "MEDIUM", "title": "Weak hash algorithm (MD5/SHA-1)"},
    "TYT-J005": {"cwe": "CWE-295", "severity": "HIGH",   "title": "TLS certificate validation disabled"},
}


def _finding(rule_id: str, file: str, line: int, evidence: str = "",
             detail: str = "") -> dict:
    meta = RULES[rule_id]
    return {
        "rule_id": rule_id,
        "severity": meta["severity"],
        "title": meta["title"],
        "message": detail or meta["title"],
        "cwe": meta["cwe"],
        "file": file,
        "line": line,
        "evidence": evidence.strip()[:200],
    }


# ── Python AST analysis ───────────────────────────────────────────────────────

_WEAK_HASH = {"md5", "sha1", "md4"}
_WEAK_CIPHER = {"DES", "DES3", "ARC4", "ARC2", "Blowfish", "RC4", "RC2"}
_PICKLE_LOADS = {
    "pickle.loads", "pickle.load", "cpickle.loads", "cpickle.load",
    "_pickle.loads", "_pickle.load", "marshal.loads", "marshal.load",
    "dill.loads", "dill.load", "shelve.open",
}
_OS_EXEC = {"os.system", "os.popen"}


def _dotted(node: ast.AST) -> str:
    """Return the dotted call/attribute name, e.g. 'hashlib.md5'. Best-effort."""
    parts: List[str] = []
    cur = node
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        parts.append(cur.id)
    return ".".join(reversed(parts))


def _is_const_str(node: ast.AST) -> bool:
    return isinstance(node, ast.Constant) and isinstance(node.value, str)


def _is_dynamic_str(node: Optional[ast.AST]) -> bool:
    """True when a value is a string assembled at runtime — the SQLi signal."""
    if node is None:
        return False
    if isinstance(node, ast.JoinedStr):                      # f"...{x}..."
        return any(isinstance(v, ast.FormattedValue) for v in node.values)
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Mod)):
        return True                                          # "..." + x  /  "..." % x
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        return node.func.attr == "format"                    # "...".format(x)
    return False


class _PyVisitor(ast.NodeVisitor):
    def __init__(self, file: str, add: Callable[[dict], None], src_lines: List[str]):
        self.file = file
        self.add = add
        self.lines = src_lines

    def _ev(self, node: ast.AST) -> str:
        ln = getattr(node, "lineno", 0)
        return self.lines[ln - 1] if 0 < ln <= len(self.lines) else ""

    def _emit(self, rule_id: str, node: ast.AST, detail: str = "") -> None:
        ln = getattr(node, "lineno", 0)
        self.add(_finding(rule_id, self.file, ln, self._ev(node), detail))

    # -- attribute access: ECB mode, weak-cipher module refs -------------------
    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr in ("MODE_ECB",) or node.attr == "ECB":
            self._emit("TYT-P003", node, "ECB reveals plaintext structure; use GCM/CBC with a random IV")
        self.generic_visit(node)

    # -- calls: the bulk of the rules ------------------------------------------
    def visit_Call(self, node: ast.Call) -> None:
        dotted = _dotted(node.func)
        low = dotted.lower()
        attr = node.func.attr if isinstance(node.func, ast.Attribute) else ""
        name = node.func.id if isinstance(node.func, ast.Name) else ""

        # TYT-P001 weak hash
        if low in ("hashlib.md5", "hashlib.sha1", "md5.new", "sha.new") or name in _WEAK_HASH:
            self._emit("TYT-P001", node, "MD5/SHA-1 are broken for security use; prefer SHA-256+")
        elif low == "hashlib.new" and node.args and _is_const_str(node.args[0]) \
                and node.args[0].value.lower() in _WEAK_HASH:
            self._emit("TYT-P001", node, "MD5/SHA-1 are broken for security use; prefer SHA-256+")

        # TYT-P002 weak cipher
        if attr == "new" and isinstance(node.func, ast.Attribute):
            mod = _dotted(node.func.value).split(".")[-1]
            if mod in _WEAK_CIPHER:
                self._emit("TYT-P002", node, f"{mod} is cryptographically broken; use AES-GCM")

        # TYT-P004 TLS verification disabled
        for kw in node.keywords:
            if kw.arg == "verify" and _is_false(kw.value):
                self._emit("TYT-P004", node, "verify=False disables certificate checking (MITM)")
            if kw.arg == "check_hostname" and _is_false(kw.value):
                self._emit("TYT-P004", node, "check_hostname=False disables hostname verification")
        if low in ("ssl._create_unverified_context",):
            self._emit("TYT-P004", node, "unverified SSL context accepts any certificate")

        # TYT-P005 unsafe deserialization
        if low in _PICKLE_LOADS:
            self._emit("TYT-P005", node, "deserializing untrusted data can execute arbitrary code")

        # TYT-P006 unsafe yaml.load
        if low in ("yaml.load", "yaml.load_all"):
            loader = next((kw.value for kw in node.keywords if kw.arg == "Loader"), None)
            loader_name = _dotted(loader).split(".")[-1] if loader is not None else ""
            if loader_name in ("", "Loader", "UnsafeLoader") and not (
                    len(node.args) >= 2 and _dotted(node.args[1]).split(".")[-1]
                    in ("SafeLoader", "FullLoader", "CSafeLoader")):
                self._emit("TYT-P006", node, "use yaml.safe_load / Loader=SafeLoader")

        # TYT-P007 eval / exec
        if name in ("eval", "exec") and node.args and not _all_const(node.args):
            self._emit("TYT-P007", node, f"{name}() on dynamic input executes attacker-controlled code")

        # TYT-P008 os.system / os.popen
        if low in _OS_EXEC:
            self._emit("TYT-P008", node, "shell string is injectable; use subprocess with an argument list")

        # TYT-P009 subprocess(..., shell=True)
        if low.startswith("subprocess.") or name in ("Popen", "call", "run", "check_output"):
            if any(kw.arg == "shell" and _is_true(kw.value) for kw in node.keywords):
                self._emit("TYT-P009", node, "shell=True with dynamic input enables command injection")

        # TYT-P010 dynamic SQL
        if attr in ("execute", "executemany", "executescript", "raw", "extra"):
            if node.args and _is_dynamic_str(node.args[0]):
                self._emit("TYT-P010", node, "pass parameters as bind values, not string-formatted SQL")

        # TYT-P011 SSTI / XSS sinks
        if attr == "render_template_string" or low.endswith("render_template_string"):
            if node.args and not _is_const_str(node.args[0]):
                self._emit("TYT-P011", node, "rendering a dynamic template enables SSTI")
        if name == "mark_safe" or attr == "mark_safe":
            if node.args and not _is_const_str(node.args[0]):
                self._emit("TYT-P011", node, "mark_safe on dynamic input bypasses auto-escaping")

        self.generic_visit(node)


def _is_false(node: ast.AST) -> bool:
    return isinstance(node, ast.Constant) and node.value is False


def _is_true(node: ast.AST) -> bool:
    return isinstance(node, ast.Constant) and node.value is True


def _all_const(nodes: List[ast.AST]) -> bool:
    return all(isinstance(n, ast.Constant) for n in nodes)


def _scan_python(text: str, file: str) -> List[dict]:
    out: List[dict] = []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return out
    _PyVisitor(file, out.append, text.splitlines()).visit(tree)
    return out


# ── JavaScript / TypeScript analysis (conservative line patterns) ─────────────

_JS_RULES: List[tuple] = [
    ("TYT-J001", re.compile(r"(^|[^.\w])eval\s*\(")),
    ("TYT-J002", re.compile(r"\b(exec|execSync|spawn)\s*\([^)]*(`[^`]*\$\{|['\"][^'\"]*['\"]\s*\+)")),
    ("TYT-J003", re.compile(r"\.innerHTML\s*=\s*[^;]*(`[^`]*\$\{|\+)")),
    ("TYT-J004", re.compile(r"createHash\s*\(\s*['\"](md5|sha1)['\"]")),
    ("TYT-J005", re.compile(r"(rejectUnauthorized\s*:\s*false|NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*['\"]?0)")),
]
_JS_COMMENT = re.compile(r"^\s*(//|\*|/\*)")


def _scan_js(text: str, file: str) -> List[dict]:
    out: List[dict] = []
    for i, line in enumerate(text.splitlines(), 1):
        if _JS_COMMENT.match(line):
            continue
        for rule_id, rx in _JS_RULES:
            if rx.search(line):
                out.append(_finding(rule_id, file, i, line))
    return out


# ── Public scanner ────────────────────────────────────────────────────────────

class CodeWeaknessScanner:
    """Offline SAST rule engine. Returns a flat list of finding dicts."""

    def __init__(self, max_files: int = 5000) -> None:
        self.max_files = max_files

    def scan_file(self, path: str) -> List[dict]:
        p = Path(path)
        try:
            if p.stat().st_size > _MAX_FILE_BYTES:
                return []
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return []
        ext = p.suffix.lower()
        if ext in _PY_EXTS:
            return _scan_python(text, str(p))
        if ext in _JS_EXTS:
            return _scan_js(text, str(p))
        return []

    def scan_directory(self, directory: str) -> List[dict]:
        root = Path(directory)
        if root.is_file():
            return self.scan_file(str(root))
        out: List[dict] = []
        seen = 0
        for path in sorted(root.rglob("*")):
            if seen >= self.max_files:
                break
            if not path.is_file():
                continue
            if any(part in _SKIP_DIRS for part in path.parts):
                continue
            if path.suffix.lower() not in (_PY_EXTS | _JS_EXTS):
                continue
            seen += 1
            out.extend(self.scan_file(str(path)))
        return out
