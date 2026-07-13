# TythanAI Security Platform — Community Edition
# Copyright (c) 2026 TythanAI Labs
# Licensed under the Business Source License 1.1 (see LICENSE).

"""
community/ai/knowledge.py — offline CWE knowledge base.

Deterministic, curated explanations and remediations for the weakness classes
the scanner reports. This is what makes `tythanai explain` work with **no LLM
and no network** — preserving the Community Edition's local-first promise. An
LLM provider (Claude / Ollama), when configured, builds on top of this.
"""
from __future__ import annotations

from typing import Dict, Optional

# cwe -> {name, why, fix, reference}
KB: Dict[str, dict] = {
    "CWE-327": {
        "name": "Use of a broken or risky cryptographic algorithm",
        "why": "MD5/SHA-1/DES/RC4 and ECB mode are broken or weak: collisions, "
               "brute force, or revealed plaintext structure make them unsafe for "
               "security decisions (passwords, signatures, tokens).",
        "fix": "Use SHA-256+ for hashing, a password hash (bcrypt/argon2/scrypt) "
               "for passwords, and AES-GCM (never ECB) for encryption.",
        "ref": "https://cwe.mitre.org/data/definitions/327.html",
    },
    "CWE-295": {
        "name": "Improper certificate validation",
        "why": "Disabling TLS verification (verify=False, InsecureSkipVerify, "
               "rejectUnauthorized:false) lets an attacker man-in-the-middle the "
               "connection and read or tamper with everything.",
        "fix": "Leave certificate and hostname verification enabled; pin or add a "
               "trusted CA if you need a private root, don't disable checks.",
        "ref": "https://cwe.mitre.org/data/definitions/295.html",
    },
    "CWE-502": {
        "name": "Deserialization of untrusted data",
        "why": "pickle/marshal, yaml.load, Java ObjectInputStream and "
               "BinaryFormatter can construct arbitrary objects — deserializing "
               "attacker data leads to remote code execution.",
        "fix": "Use a data-only format (JSON) for untrusted input, or yaml.safe_load "
               "/ an allow-list of permitted types.",
        "ref": "https://cwe.mitre.org/data/definitions/502.html",
    },
    "CWE-95": {
        "name": "Code injection (eval/exec)",
        "why": "eval()/exec() on any attacker-influenced string runs arbitrary code "
               "with your process's privileges.",
        "fix": "Remove dynamic evaluation. Use ast.literal_eval for literals, a "
               "dispatch dict for a fixed set of actions, or a real parser.",
        "ref": "https://cwe.mitre.org/data/definitions/95.html",
    },
    "CWE-78": {
        "name": "OS command injection",
        "why": "Building a shell command from input (os.system, shell=True, "
               "exec.Command('sh','-c',...), Runtime.exec) lets an attacker append "
               "their own commands.",
        "fix": "Call the program directly with an argument list (subprocess.run("
               "['ping', host]), execFile) — no shell, no string concatenation.",
        "ref": "https://cwe.mitre.org/data/definitions/78.html",
    },
    "CWE-89": {
        "name": "SQL injection",
        "why": "Concatenating or interpolating input into SQL lets an attacker "
               "change the query — read, modify, or delete data, sometimes run "
               "commands.",
        "fix": "Use parameterised queries / prepared statements: pass values as "
               "bind parameters (execute(sql, params)), never format them into the "
               "SQL string.",
        "ref": "https://cwe.mitre.org/data/definitions/89.html",
    },
    "CWE-79": {
        "name": "Cross-site scripting / template injection",
        "why": "Rendering unescaped input (render_template_string, mark_safe, "
               "innerHTML=) lets an attacker inject markup or a server-side template "
               "that executes.",
        "fix": "Auto-escape by default, render fixed templates with a context, and "
               "use textContent (not innerHTML) for dynamic text.",
        "ref": "https://cwe.mitre.org/data/definitions/79.html",
    },
    "CWE-330": {
        "name": "Use of insufficiently random values",
        "why": "random / Math.random / java.util.Random are predictable; using them "
               "for tokens, keys, or password resets lets an attacker guess them.",
        "fix": "Use a cryptographically secure RNG: Python secrets, Java "
               "SecureRandom, Node crypto.randomBytes.",
        "ref": "https://cwe.mitre.org/data/definitions/330.html",
    },
    "CWE-611": {
        "name": "XML external entity (XXE)",
        "why": "Parsing XML with entity resolution enabled lets an attacker read "
               "local files or reach internal services via external entities.",
        "fix": "Disable DTD/entity resolution: lxml XMLParser(resolve_entities="
               "False, no_network=True), or use defusedxml.",
        "ref": "https://cwe.mitre.org/data/definitions/611.html",
    },
    "CWE-22": {
        "name": "Path traversal",
        "why": "Passing user input into open()/file paths lets an attacker use ../ "
               "to read or write files outside the intended directory.",
        "fix": "Take os.path.basename, then join onto a fixed safe root and verify "
               "the resolved path stays inside it.",
        "ref": "https://cwe.mitre.org/data/definitions/22.html",
    },
    "CWE-676": {
        "name": "Use of a dangerous function",
        "why": "strcpy/strcat/sprintf/gets don't bound their writes — classic "
               "buffer overflows leading to crashes or code execution.",
        "fix": "Use bounded variants (strncpy/snprintf) or safe string types; never "
               "use gets — use fgets.",
        "ref": "https://cwe.mitre.org/data/definitions/676.html",
    },
    "CWE-643": {
        "name": "XPath injection",
        "why": "Building an XPath expression from input lets an attacker rewrite the "
               "query and read parts of the document they shouldn't.",
        "fix": "Use XPath variables / parameterisation, or strictly validate and "
               "escape the input.",
        "ref": "https://cwe.mitre.org/data/definitions/643.html",
    },
    "CWE-90": {
        "name": "LDAP injection",
        "why": "Building an LDAP filter from raw input lets an attacker alter the "
               "filter to bypass auth or read extra entries.",
        "fix": "Escape values with your LDAP library's filter escaper "
               "(ldap.filter.escape_filter_chars) before building the filter.",
        "ref": "https://cwe.mitre.org/data/definitions/90.html",
    },
    "CWE-506": {
        "name": "Embedded / obfuscated malicious code",
        "why": "Dangerous logic hidden behind base64/hex/split-string encoding is a "
               "hallmark of malware or a backdoor trying to evade review and scanners.",
        "fix": "Review the decoded payload; if it isn't a legitimate, documented "
               "resource, remove it and investigate how it got in.",
        "ref": "https://cwe.mitre.org/data/definitions/506.html",
    },
    "CWE-798": {
        "name": "Use of hard-coded credentials",
        "why": "Secrets committed in source are readable by anyone with repo access "
               "and often leak publicly; they can't be rotated without a code change.",
        "fix": "Move secrets to environment variables or a secrets manager; rotate "
               "any that were committed.",
        "ref": "https://cwe.mitre.org/data/definitions/798.html",
    },
}


def lookup(cwe: Optional[str]) -> Optional[dict]:
    if not cwe:
        return None
    return KB.get(str(cwe).upper())


def offline_explanation(finding: dict) -> str:
    """A deterministic, LLM-free explanation of a finding."""
    cwe = finding.get("cwe", "")
    entry = lookup(cwe)
    title = finding.get("title", finding.get("rule_id", "Finding"))
    loc = finding.get("file", "")
    line = finding.get("line", "")
    where = f"{loc}:{line}" if loc and line else loc
    sev = finding.get("severity", "")
    lines = [f"● {title}  [{sev}]  {cwe}".rstrip()]
    if where:
        lines.append(f"  Location: {where}")
    if entry:
        lines.append(f"\n  What it is: {entry['name']}.")
        lines.append(f"  Why it matters: {entry['why']}")
        lines.append(f"  How to fix it: {entry['fix']}")
        lines.append(f"  Reference: {entry['ref']}")
    else:
        msg = finding.get("message") or finding.get("description") or ""
        if msg:
            lines.append(f"\n  {msg}")
        lines.append("  (No knowledge-base entry for this CWE — configure an AI "
                     "provider for a deeper explanation.)")
    return "\n".join(lines)
