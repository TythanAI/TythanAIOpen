# TythanAI Security Platform — Community Edition
# Copyright (c) 2026 TythanAI Labs
# Licensed under the Business Source License 1.1 (see LICENSE).

"""
scanners/evasion_scanner.py — anti-evasion (de-obfuscation) preprocessing.

Attackers hide dangerous payloads from naive scanners by encoding them:
base64, hex escapes, split string concatenation, char-code arrays. This module
*reverses* those tricks, then checks the revealed content for dangerous tokens.
It hardens detection — it never helps anyone evade it.

Returns TYT-E001 findings (CWE-506, embedded/obfuscated command) when a decoded
blob resolves to something like `eval`, a shell command, or a destructive SQL
statement. Conservative by design: only decodes that yield printable ASCII *and*
contain a known-dangerous token are reported.
"""
from __future__ import annotations

import base64
import binascii
import re
from pathlib import Path
from typing import List

_MAX_FILE_BYTES = 1_500_000

# Tokens that make a *decoded* blob suspicious (they were hidden for a reason).
_DANGEROUS = re.compile(
    r"(?i)\b(eval|exec|system|popen|subprocess|/bin/sh|/bin/bash|cmd\.exe|"
    r"powershell|Invoke-Expression|IEX|base64_decode|shell_exec|passthru|"
    r"rm\s+-rf|DROP\s+TABLE|DELETE\s+FROM|UNION\s+SELECT|os\.system|"
    r"import\s+os|__import__|require\(|child_process|wget\s|curl\s+-)")

_B64 = re.compile(r"['\"`]([A-Za-z0-9+/]{16,}={0,2})['\"`]")
_HEX = re.compile(r"((?:\\x[0-9A-Fa-f]{2}){8,})")
_CONCAT = re.compile(r"['\"]\s*[+.]\s*['\"]")
_CHR_CHAIN = re.compile(r"(?:chr\(\s*\d{1,3}\s*\)\s*[+.]\s*){2,}chr\(\s*\d{1,3}\s*\)", re.IGNORECASE)
_CHR_NUM = re.compile(r"chr\(\s*(\d{1,3})\s*\)", re.IGNORECASE)
_FROMCHARCODE = re.compile(r"(?:String\s*\.\s*)?fromCharCode\(\s*([\d,\s]{5,})\)", re.IGNORECASE)


def _printable(b: bytes) -> str:
    try:
        s = b.decode("utf-8")
    except UnicodeDecodeError:
        return ""
    return s if s and all(31 < ord(c) < 127 or c in "\t\n\r" for c in s) else ""


def _decode_b64(text: str) -> List[tuple]:
    out = []
    for m in _B64.finditer(text):
        blob = m.group(1)
        if len(blob) % 4:
            continue
        try:
            decoded = _printable(base64.b64decode(blob, validate=True))
        except (binascii.Error, ValueError):
            continue
        if decoded and _DANGEROUS.search(decoded):
            out.append(("base64", decoded, text[:m.start()].count("\n") + 1))
    return out


def _decode_hex(text: str) -> List[tuple]:
    out = []
    for m in _HEX.finditer(text):
        raw = m.group(1)
        try:
            decoded = _printable(bytes.fromhex(raw.replace("\\x", "")))
        except ValueError:
            continue
        if decoded and _DANGEROUS.search(decoded):
            out.append(("hex", decoded, text[:m.start()].count("\n") + 1))
    return out


def _nums_to_printable(nums: List[int]) -> str:
    if len(nums) < 3 or any(n < 0 or n > 255 for n in nums):
        return ""
    try:
        return _printable(bytes(nums))
    except ValueError:
        return ""


def _decode_charcode(text: str) -> List[tuple]:
    """Char-code arrays: Python/PHP `chr(101)+chr(118)+...`, JS `String.fromCharCode(...)`."""
    out = []
    for m in _CHR_CHAIN.finditer(text):
        nums = [int(n) for n in _CHR_NUM.findall(m.group(0))]
        decoded = _nums_to_printable(nums)
        if decoded and _DANGEROUS.search(decoded):
            out.append(("char-code", decoded, text[:m.start()].count("\n") + 1))
    for m in _FROMCHARCODE.finditer(text):
        try:
            nums = [int(n.strip()) for n in m.group(1).split(",") if n.strip()]
        except ValueError:
            continue
        decoded = _nums_to_printable(nums)
        if decoded and _DANGEROUS.search(decoded):
            out.append(("char-code", decoded, text[:m.start()].count("\n") + 1))
    return out


def _find_concat_evasion(text: str) -> List[tuple]:
    """Split-string concatenation used to hide a dangerous token (e.g. "ev"+"al")."""
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        if not _CONCAT.search(line):
            continue
        # Join the string fragments on the line and re-check for a hidden token.
        joined = "".join(re.findall(r"['\"]([^'\"]*)['\"]", line))
        if joined and _DANGEROUS.search(joined) and not _DANGEROUS.search(line):
            out.append(("concat", joined, i))
    return out


def _finding(kind: str, revealed: str, file: str, line: int) -> dict:
    return {
        "rule_id": "TYT-E001",
        "severity": "HIGH",
        "title": "Obfuscated payload reveals dangerous content",
        "message": f"{kind}-encoded content decodes to a dangerous command; "
                   f"revealed: {revealed[:120]}",
        "cwe": "CWE-506",
        "file": file,
        "line": line,
        "evidence": revealed[:200],
        "source": "evasion",
    }


class EvasionScanner:
    """De-obfuscates encoded payloads and flags hidden dangerous content."""

    def scan_file(self, path: str) -> List[dict]:
        p = Path(path)
        try:
            if p.stat().st_size > _MAX_FILE_BYTES:
                return []
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return []
        return self.scan_text(text, str(p))

    def scan_text(self, text: str, file: str = "<memory>") -> List[dict]:
        out: List[dict] = []
        for kind, revealed, line in (_decode_b64(text) + _decode_hex(text)
                                     + _decode_charcode(text) + _find_concat_evasion(text)):
            out.append(_finding(kind, revealed, file, line))
        return out

    def scan_directory(self, directory: str, max_files: int = 5000) -> List[dict]:
        # Reuse the code-weakness engine's file selection so both passes agree.
        from scanners.code_weakness_scanner import _ALL_EXTS, _SKIP_DIRS
        root = Path(directory)
        if root.is_file():
            return self.scan_file(str(root))
        out: List[dict] = []
        seen = 0
        for path in sorted(root.rglob("*")):
            if seen >= max_files:
                break
            if not path.is_file() or any(part in _SKIP_DIRS for part in path.parts):
                continue
            if path.suffix.lower() not in _ALL_EXTS:
                continue
            seen += 1
            out.extend(self.scan_file(str(path)))
        return out
