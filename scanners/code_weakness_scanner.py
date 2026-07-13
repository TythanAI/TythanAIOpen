# TythanAI Security Platform — Community Edition
# Copyright (c) 2026 TythanAI Labs
# Licensed under the Business Source License 1.1 (see LICENSE).

"""
scanners/code_weakness_scanner.py — built-in, offline SAST rule engine.

Dependency-free static checks for the weakness classes that a taint engine
*doesn't* model (weak crypto, insecure deserialization, disabled TLS
verification, code/command injection, dynamic SQL, weak randomness, XXE,
direct-user-input file access). Python is analysed with the `ast` module
(structural, low false-positive) including a light *local* def-use pass so SQL
built into a variable and then executed is still caught, plus an intra-module
pass that flags dynamic SQL passed into a query-helper function. JavaScript/
TypeScript, Go, Java, PHP, Ruby, C#, Kotlin, Rust and C/C++ are analysed with a
small set of conservative, comment-aware line patterns.

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
from typing import Callable, Dict, List, Optional, Set

# ── File selection ────────────────────────────────────────────────────────────

_PY_EXTS = {".py", ".pyi"}
_JS_EXTS = {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx"}
_GO_EXTS = {".go"}
_JAVA_EXTS = {".java"}
_PHP_EXTS = {".php", ".php5", ".phtml"}
_RUBY_EXTS = {".rb"}
_CS_EXTS = {".cs"}
_KOTLIN_EXTS = {".kt", ".kts"}
_RUST_EXTS = {".rs"}
_CPP_EXTS = {".c", ".cc", ".cpp", ".cxx", ".h", ".hpp", ".hh"}
_ALL_EXTS = (_PY_EXTS | _JS_EXTS | _GO_EXTS | _JAVA_EXTS
             | _PHP_EXTS | _RUBY_EXTS | _CS_EXTS
             | _KOTLIN_EXTS | _RUST_EXTS | _CPP_EXTS)
_SKIP_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv", "env",
    "dist", "build", ".tox", ".mypy_cache", ".pytest_cache", "site-packages",
    "vendor", "target", "third_party",
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
    "TYT-P012": {"cwe": "CWE-330", "severity": "MEDIUM", "title": "Insecure randomness for a security value"},
    "TYT-P013": {"cwe": "CWE-611", "severity": "MEDIUM", "title": "XML parsed without external-entity protection (XXE)"},
    "TYT-P014": {"cwe": "CWE-22",  "severity": "HIGH",   "title": "User-controlled path passed to open() (traversal)"},
    "TYT-P015": {"cwe": "CWE-89",  "severity": "HIGH",   "title": "Dynamic SQL passed to a query helper (injection)"},
    # JavaScript / TypeScript
    "TYT-J001": {"cwe": "CWE-95",  "severity": "HIGH",   "title": "Code injection via eval()"},
    "TYT-J002": {"cwe": "CWE-78",  "severity": "HIGH",   "title": "Command execution with interpolated input"},
    "TYT-J003": {"cwe": "CWE-79",  "severity": "MEDIUM", "title": "innerHTML assigned dynamic content (DOM XSS)"},
    "TYT-J004": {"cwe": "CWE-327", "severity": "MEDIUM", "title": "Weak hash algorithm (MD5/SHA-1)"},
    "TYT-J005": {"cwe": "CWE-295", "severity": "HIGH",   "title": "TLS certificate validation disabled"},
    # Go
    "TYT-G001": {"cwe": "CWE-327", "severity": "MEDIUM", "title": "Weak hash/cipher (MD5/SHA-1/DES/RC4)"},
    "TYT-G002": {"cwe": "CWE-295", "severity": "HIGH",   "title": "TLS verification disabled (InsecureSkipVerify)"},
    "TYT-G003": {"cwe": "CWE-78",  "severity": "HIGH",   "title": "Command execution with concatenated input"},
    "TYT-G004": {"cwe": "CWE-89",  "severity": "HIGH",   "title": "SQL built from dynamic string (injection)"},
    # Java
    "TYT-A001": {"cwe": "CWE-327", "severity": "MEDIUM", "title": "Weak hash/cipher (MD5/SHA-1/DES/ECB)"},
    "TYT-A002": {"cwe": "CWE-78",  "severity": "HIGH",   "title": "Command execution with concatenated input"},
    "TYT-A003": {"cwe": "CWE-89",  "severity": "HIGH",   "title": "SQL built from string concatenation (injection)"},
    "TYT-A004": {"cwe": "CWE-502", "severity": "HIGH",   "title": "Unsafe Java deserialization (ObjectInputStream)"},
    "TYT-A005": {"cwe": "CWE-330", "severity": "MEDIUM", "title": "Insecure randomness for a security value (use SecureRandom)"},
    # PHP
    "TYT-H001": {"cwe": "CWE-327", "severity": "MEDIUM", "title": "Weak hash (md5/sha1)"},
    "TYT-H002": {"cwe": "CWE-78",  "severity": "HIGH",   "title": "Command execution with variable input"},
    "TYT-H003": {"cwe": "CWE-89",  "severity": "HIGH",   "title": "SQL built from interpolated/concatenated string"},
    "TYT-H004": {"cwe": "CWE-502", "severity": "HIGH",   "title": "Unsafe deserialization (unserialize)"},
    "TYT-H005": {"cwe": "CWE-95",  "severity": "HIGH",   "title": "Code injection via eval()"},
    # Ruby
    "TYT-R001": {"cwe": "CWE-327", "severity": "MEDIUM", "title": "Weak hash (Digest::MD5/SHA1)"},
    "TYT-R002": {"cwe": "CWE-78",  "severity": "HIGH",   "title": "Command execution with interpolation"},
    "TYT-R003": {"cwe": "CWE-89",  "severity": "HIGH",   "title": "SQL built from string interpolation"},
    "TYT-R004": {"cwe": "CWE-502", "severity": "HIGH",   "title": "Unsafe deserialization (Marshal/YAML.load)"},
    "TYT-R005": {"cwe": "CWE-95",  "severity": "HIGH",   "title": "Code injection via eval()"},
    # C#
    "TYT-C001": {"cwe": "CWE-327", "severity": "MEDIUM", "title": "Weak hash/cipher (MD5/SHA-1/DES)"},
    "TYT-C002": {"cwe": "CWE-78",  "severity": "HIGH",   "title": "Command execution with concatenated input"},
    "TYT-C003": {"cwe": "CWE-89",  "severity": "HIGH",   "title": "SQL built from concatenation/interpolation"},
    "TYT-C004": {"cwe": "CWE-502", "severity": "HIGH",   "title": "Unsafe deserialization (BinaryFormatter)"},
    # Kotlin
    "TYT-K001": {"cwe": "CWE-327", "severity": "MEDIUM", "title": "Weak hash/cipher (MD5/SHA-1/DES/ECB)"},
    "TYT-K002": {"cwe": "CWE-78",  "severity": "HIGH",   "title": "Command execution with concatenated/interpolated input"},
    "TYT-K003": {"cwe": "CWE-89",  "severity": "HIGH",   "title": "SQL built from concatenation/interpolation"},
    "TYT-K004": {"cwe": "CWE-502", "severity": "HIGH",   "title": "Unsafe deserialization (ObjectInputStream)"},
    # Rust
    "TYT-U001": {"cwe": "CWE-327", "severity": "MEDIUM", "title": "Weak hash (MD5/SHA-1)"},
    "TYT-U002": {"cwe": "CWE-78",  "severity": "HIGH",   "title": "Command built with format!()"},
    "TYT-U003": {"cwe": "CWE-89",  "severity": "HIGH",   "title": "SQL built with format!() (injection)"},
    # C / C++
    "TYT-X001": {"cwe": "CWE-676", "severity": "HIGH",   "title": "Dangerous unbounded function (strcpy/strcat/sprintf/gets)"},
    "TYT-X002": {"cwe": "CWE-78",  "severity": "HIGH",   "title": "Command execution via system() with dynamic input"},
    "TYT-X003": {"cwe": "CWE-327", "severity": "MEDIUM", "title": "Weak hash primitive (MD5/SHA-1)"},
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
_RANDOM_FUNCS = {"random", "randint", "randrange", "choice", "getrandbits",
                 "uniform", "sample", "shuffle", "choices"}
_SECURITY_NAME = re.compile(
    r"(token|secret|api[_-]?key|passwd|password|pwd|nonce|salt|otp|seed|"
    r"session|csrf|cookie|private|credential)", re.I)
_REQUEST_ACCESS = re.compile(r"(args\.get|form\.get|values\.get|\.GET|\.POST|request)", re.I)
_XML_PARSE = ("etree.fromstring", "etree.parse", "etree.XML")


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


def _collect_dynamic_vars(body: List[ast.stmt]) -> Set[str]:
    """Names assigned a runtime-built string within one scope (no nested defs)."""
    names: Set[str] = set()

    def walk(stmts: List[ast.stmt]) -> None:
        for s in stmts:
            if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue                                     # separate scope
            if isinstance(s, ast.Assign) and _is_dynamic_str(s.value):
                for t in s.targets:
                    if isinstance(t, ast.Name):
                        names.add(t.id)
            if isinstance(s, ast.AnnAssign) and _is_dynamic_str(s.value) \
                    and isinstance(s.target, ast.Name):
                names.add(s.target.id)
            for field in ("body", "orelse", "finalbody"):
                sub = getattr(s, field, None)
                if isinstance(sub, list):
                    walk(sub)
            for handler in getattr(s, "handlers", []) or []:
                walk(handler.body)
    walk(body)
    return names


_SQL_SINK_METHODS = {"execute", "executemany", "executescript"}


def _collect_sql_sink_funcs(tree: ast.AST) -> Dict[str, tuple]:
    """Map module-level function name -> (param_names, sink_param_names).

    A *sink* parameter is one passed as the sole argument to a SQL execute()
    call inside the function body — i.e. the helper runs whatever SQL string it
    is handed, unparameterised. Callers that pass a dynamic string into such a
    parameter are then flagged (light intra-module taint). Helpers that
    parameterise (execute(sql, args), two args) are NOT sinks, so the common
    safe pattern never triggers.
    """
    sinks: Dict[str, tuple] = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        params = [a.arg for a in node.args.args]
        sink_params: Set[str] = set()
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute) \
                    and sub.func.attr in _SQL_SINK_METHODS \
                    and len(sub.args) == 1 and not sub.keywords \
                    and isinstance(sub.args[0], ast.Name) and sub.args[0].id in params:
                sink_params.add(sub.args[0].id)
        if sink_params:
            sinks[node.name] = (params, sink_params)
    return sinks


class _PyVisitor(ast.NodeVisitor):
    def __init__(self, file: str, add: Callable[[dict], None], src_lines: List[str],
                 sinks: Optional[Dict[str, tuple]] = None):
        self.file = file
        self.add = add
        self.lines = src_lines
        self.sinks = sinks or {}
        self.scopes: List[Set[str]] = []          # stack of dynamic-var sets

    def _ev(self, node: ast.AST) -> str:
        ln = getattr(node, "lineno", 0)
        return self.lines[ln - 1] if 0 < ln <= len(self.lines) else ""

    def _emit(self, rule_id: str, node: ast.AST, detail: str = "") -> None:
        ln = getattr(node, "lineno", 0)
        self.add(_finding(rule_id, self.file, ln, self._ev(node), detail))

    def _is_dynamic_var(self, node: ast.AST) -> bool:
        return isinstance(node, ast.Name) and any(node.id in s for s in self.scopes)

    # -- scope tracking for local def-use (dynamic SQL through a variable) ------
    def visit_Module(self, node: ast.Module) -> None:
        self.scopes.append(_collect_dynamic_vars(node.body))
        self.generic_visit(node)
        self.scopes.pop()

    def _visit_func(self, node) -> None:
        self.scopes.append(_collect_dynamic_vars(node.body))
        self.generic_visit(node)
        self.scopes.pop()

    visit_FunctionDef = _visit_func
    visit_AsyncFunctionDef = _visit_func

    # -- attribute access: ECB mode --------------------------------------------
    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr == "MODE_ECB" or node.attr == "ECB":
            self._emit("TYT-P003", node, "ECB reveals plaintext structure; use GCM/CBC with a random IV")
        self.generic_visit(node)

    # -- assignments: weak randomness for a security value ---------------------
    def visit_Assign(self, node: ast.Assign) -> None:
        target_names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        if any(_SECURITY_NAME.search(n) for n in target_names):
            for sub in ast.walk(node.value):
                if isinstance(sub, ast.Call):
                    d = _dotted(sub.func)
                    if d.split(".")[0] == "random" and d.split(".")[-1] in _RANDOM_FUNCS:
                        self._emit("TYT-P012", node,
                                   "use the `secrets` module for tokens/keys, not `random`")
                        break
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
        if low == "ssl._create_unverified_context":
            self._emit("TYT-P004", node, "unverified SSL context accepts any certificate")

        # TYT-P005 unsafe deserialization
        if low in _PICKLE_LOADS:
            self._emit("TYT-P005", node, "deserializing untrusted data can execute arbitrary code")

        # TYT-P006 unsafe yaml.load
        if low in ("yaml.load", "yaml.load_all"):
            loader = next((kw.value for kw in node.keywords if kw.arg == "Loader"), None)
            loader_name = _dotted(loader).split(".")[-1] if loader is not None else ""
            second = _dotted(node.args[1]).split(".")[-1] if len(node.args) >= 2 else ""
            if loader_name in ("", "Loader", "UnsafeLoader") and \
                    second not in ("SafeLoader", "FullLoader", "CSafeLoader"):
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

        # TYT-P010 dynamic SQL (direct or via a locally-built string)
        if attr in ("execute", "executemany", "executescript", "raw", "extra"):
            if node.args and (_is_dynamic_str(node.args[0]) or self._is_dynamic_var(node.args[0])):
                self._emit("TYT-P010", node, "pass parameters as bind values, not string-formatted SQL")

        # TYT-P011 SSTI / XSS sinks
        if attr == "render_template_string" or low.endswith("render_template_string"):
            if node.args and not _is_const_str(node.args[0]):
                self._emit("TYT-P011", node, "rendering a dynamic template enables SSTI")
        if (name == "mark_safe" or attr == "mark_safe") and node.args and not _is_const_str(node.args[0]):
            self._emit("TYT-P011", node, "mark_safe on dynamic input bypasses auto-escaping")

        # TYT-P013 XXE — lxml parse without an explicit hardened parser
        if any(low.endswith(x.lower()) for x in _XML_PARSE):
            has_parser = any(kw.arg == "parser" for kw in node.keywords) or len(node.args) >= 2
            if not has_parser:
                self._emit("TYT-P013", node,
                           "configure an XMLParser(resolve_entities=False, no_network=True)")

        # TYT-P014 user-controlled path into open()
        if (name == "open" or low in ("os.open", "io.open", "codecs.open")) and node.args:
            first = node.args[0]
            if isinstance(first, ast.Call) and _REQUEST_ACCESS.search(_dotted(first.func)):
                self._emit("TYT-P014", node, "validate and confine the path (basename + safe root)")

        # TYT-P015 dynamic SQL flowing into a query-helper parameter
        if name in self.sinks:
            params, sink_params = self.sinks[name]
            for sp in sink_params:
                idx = params.index(sp)
                arg = node.args[idx] if idx < len(node.args) else None
                if arg is None:
                    arg = next((kw.value for kw in node.keywords if kw.arg == sp), None)
                if arg is not None and (_is_dynamic_str(arg) or self._is_dynamic_var(arg)):
                    self._emit("TYT-P015", node,
                               f"dynamic SQL passed to '{name}()' — parameterise at the call site")
                    break

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
    sinks = _collect_sql_sink_funcs(tree)
    _PyVisitor(file, out.append, text.splitlines(), sinks).visit(tree)
    return out


# ── Line-pattern analysis for JS / Go / Java ──────────────────────────────────

_JS_RULES: List[tuple] = [
    ("TYT-J001", re.compile(r"(^|[^.\w])eval\s*\(")),
    ("TYT-J002", re.compile(r"\b(exec|execSync|spawn)\s*\([^)]*(`[^`]*\$\{|['\"][^'\"]*['\"]\s*\+)")),
    ("TYT-J003", re.compile(r"\.innerHTML\s*=\s*[^;]*(`[^`]*\$\{|\+)")),
    ("TYT-J004", re.compile(r"createHash\s*\(\s*['\"](md5|sha1)['\"]")),
    ("TYT-J005", re.compile(r"(rejectUnauthorized\s*:\s*false|NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*['\"]?0)")),
]

_GO_RULES: List[tuple] = [
    ("TYT-G001", re.compile(r"\b(md5|sha1|des|rc4)\.New(Cipher)?\s*\(")),
    ("TYT-G002", re.compile(r"InsecureSkipVerify\s*:\s*true")),
    ("TYT-G003", re.compile(r"exec\.Command(Context)?\s*\([^)]*(\+|fmt\.Sprintf|\"-c\")")),
    ("TYT-G004", re.compile(r"\.(Query|QueryRow|Exec|QueryContext|ExecContext)\s*\([^)]*(fmt\.Sprintf|\"\s*\+|\+\s*\w)")),
]

_JAVA_RULES: List[tuple] = [
    ("TYT-A001", re.compile(r"getInstance\s*\(\s*\"(MD5|SHA-?1|DES|DES/|RC4|AES/ECB)", re.I)),
    ("TYT-A002", re.compile(r"(Runtime\.getRuntime\(\)\.exec|new\s+ProcessBuilder)\s*\([^)]*\+")),
    ("TYT-A003", re.compile(r"\.(executeQuery|executeUpdate|execute)\s*\(\s*\"[^\"]*\"\s*\+")),
    ("TYT-A004", re.compile(r"new\s+ObjectInputStream\s*\(")),
    ("TYT-A005", re.compile(r"new\s+Random\s*\(")),
]

_PHP_RULES: List[tuple] = [
    ("TYT-H005", re.compile(r"(^|[^.\w])eval\s*\(")),
    ("TYT-H002", re.compile(r"\b(system|exec|shell_exec|passthru|popen|proc_open)\s*\([^)]*(\$|\.)")),
    ("TYT-H003", re.compile(r"(->query|->exec|mysqli_query)\s*\(\s*[\"'][^\"']*(\$\w|[\"']\s*\.\s*\$)")),
    ("TYT-H001", re.compile(r"(^|[^.\w>])(md5|sha1)\s*\(")),
    ("TYT-H004", re.compile(r"\bunserialize\s*\(")),
]

_RUBY_RULES: List[tuple] = [
    ("TYT-R005", re.compile(r"(^|[^.\w:])eval\s*[\s(]")),
    ("TYT-R002", re.compile(r"(`[^`]*#\{|\b(system|exec)\s*\([^)]*#\{|%x[\{(][^})]*#\{)")),
    ("TYT-R003", re.compile(r"\.(execute|where|find_by_sql|from|order|group)\s*\(\s*[\"'].*#\{")),
    ("TYT-R004", re.compile(r"(Marshal\.load|YAML\.load)\s*\(")),
    ("TYT-R001", re.compile(r"Digest::(MD5|SHA1)\b")),
]

_CS_RULES: List[tuple] = [
    ("TYT-C001", re.compile(r"(MD5|SHA1|DES|TripleDES)\.Create\s*\(|new\s+(MD5|SHA1|DES)CryptoServiceProvider")),
    ("TYT-C002", re.compile(r"Process\.Start\s*\([^)]*\+")),
    ("TYT-C003", re.compile(r"(new\s+SqlCommand\s*\(|CommandText\s*=)\s*(\$@?\"|@?\"[^\"]*\"\s*\+)")),
    ("TYT-C004", re.compile(r"new\s+BinaryFormatter\s*\(")),
]

_KOTLIN_RULES: List[tuple] = [
    ("TYT-K001", re.compile(r"getInstance\s*\(\s*\"(MD5|SHA-?1|DES|DES/|RC4|AES/ECB)", re.I)),
    ("TYT-K002", re.compile(r"(Runtime\.getRuntime\(\)\.exec|ProcessBuilder)\s*\([^)]*(\+|\$)")),
    ("TYT-K003", re.compile(r"\.(executeQuery|executeUpdate|execute|rawQuery)\s*\(\s*\"[^\"]*(\$\{?\w|\"\s*\+)")),
    ("TYT-K004", re.compile(r"ObjectInputStream\s*\(")),
]

_RUST_RULES: List[tuple] = [
    ("TYT-U001", re.compile(r"\b(Md5::new|Sha1::new|md5::compute)\b")),
    ("TYT-U002", re.compile(r"(\.arg|\.args|Command::new)\s*\(\s*&?format!\s*\(")),
    ("TYT-U003", re.compile(r"\b(query|execute|query_as)\s*\(\s*&?format!\s*\(")),
]

_CPP_RULES: List[tuple] = [
    ("TYT-X001", re.compile(r"\b(strcpy|strcat|sprintf|gets)\s*\(")),
    ("TYT-X002", re.compile(r"\bsystem\s*\([^)]*(\+|c_str\s*\()")),
    ("TYT-X003", re.compile(r"\b(MD5_Init|SHA1_Init|EVP_md5|EVP_sha1)\s*\(")),
]

_COMMENT = re.compile(r"^\s*(//|\*|/\*|#)")
_JAVA_A005_CONTEXT = re.compile(
    r"(token|secret|key|passwd|password|pwd|nonce|salt|otp|session|csrf)", re.I)


def _scan_lines(text: str, file: str, rules: List[tuple],
                gated: Optional[Dict[str, re.Pattern]] = None) -> List[dict]:
    out: List[dict] = []
    for i, line in enumerate(text.splitlines(), 1):
        if _COMMENT.match(line):
            continue
        for rule_id, rx in rules:
            if not rx.search(line):
                continue
            if gated and rule_id in gated and not gated[rule_id].search(line):
                continue           # require an extra context signal to fire
            out.append(_finding(rule_id, file, i, line))
    return out


def _scan_js(text: str, file: str) -> List[dict]:
    return _scan_lines(text, file, _JS_RULES)


def _scan_go(text: str, file: str) -> List[dict]:
    return _scan_lines(text, file, _GO_RULES)


def _scan_java(text: str, file: str) -> List[dict]:
    # new Random() only fires when the line clearly concerns a security value,
    # so ordinary java.util.Random for non-security use is not flagged.
    return _scan_lines(text, file, _JAVA_RULES, gated={"TYT-A005": _JAVA_A005_CONTEXT})


def _scan_php(text: str, file: str) -> List[dict]:
    return _scan_lines(text, file, _PHP_RULES)


def _scan_ruby(text: str, file: str) -> List[dict]:
    return _scan_lines(text, file, _RUBY_RULES)


def _scan_csharp(text: str, file: str) -> List[dict]:
    return _scan_lines(text, file, _CS_RULES)


def _scan_kotlin(text: str, file: str) -> List[dict]:
    return _scan_lines(text, file, _KOTLIN_RULES)


def _scan_rust(text: str, file: str) -> List[dict]:
    return _scan_lines(text, file, _RUST_RULES)


def _scan_cpp(text: str, file: str) -> List[dict]:
    return _scan_lines(text, file, _CPP_RULES)


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
        if ext in _GO_EXTS:
            return _scan_go(text, str(p))
        if ext in _JAVA_EXTS:
            return _scan_java(text, str(p))
        if ext in _PHP_EXTS:
            return _scan_php(text, str(p))
        if ext in _RUBY_EXTS:
            return _scan_ruby(text, str(p))
        if ext in _CS_EXTS:
            return _scan_csharp(text, str(p))
        if ext in _KOTLIN_EXTS:
            return _scan_kotlin(text, str(p))
        if ext in _RUST_EXTS:
            return _scan_rust(text, str(p))
        if ext in _CPP_EXTS:
            return _scan_cpp(text, str(p))
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
            if path.suffix.lower() not in _ALL_EXTS:
                continue
            seen += 1
            out.extend(self.scan_file(str(path)))
        return out
