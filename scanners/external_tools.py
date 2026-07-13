# TythanAI Security Platform — Community Edition
# Copyright (c) 2026 TythanAI Labs
# Licensed under the Business Source License 1.1 (see LICENSE).

"""
scanners/external_tools.py — optional third-party engines.

If the user has these tools on their PATH we shell out to them and normalise
their output into TythanAI findings. If they are absent, `available()` returns
False and `scan_directory()` returns `[]` — the scan continues unaffected. No
tool is bundled or required; this is purely additive breadth.

  * Slither     — deep Solidity/EVM analysis (augments the Web3 engine)
  * cargo-audit — RustSec advisories for Cargo.lock (augments SCA)
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional


def _safe_json(text: str) -> dict:
    try:
        data = json.loads(text or "{}")
        return data if isinstance(data, dict) else {}
    except (ValueError, TypeError):
        return {}


# ── Slither (Solidity) ────────────────────────────────────────────────────────

_SLITHER_IMPACT = {
    "High": "HIGH", "Medium": "MEDIUM", "Low": "LOW",
    "Informational": "INFO", "Optimization": "INFO",
}


class SlitherScanner:
    """Deep Solidity analysis via Slither, when it is installed."""

    def available(self) -> bool:
        return shutil.which("slither") is not None

    def scan_directory(self, directory: str, timeout: int = 300) -> List[dict]:
        if not self.available():
            return []
        root = Path(directory)
        if next(root.rglob("*.sol"), None) is None:
            return []
        try:
            proc = subprocess.run(
                ["slither", str(root), "--json", "-"],
                capture_output=True, text=True, timeout=timeout,
            )
        except Exception:
            return []
        data = _safe_json(proc.stdout)
        detectors = (data.get("results") or {}).get("detectors") or []
        findings: List[dict] = []
        for det in detectors:
            file, line = _slither_location(det)
            findings.append({
                "rule_id": f"slither:{det.get('check', 'detector')}",
                "severity": _SLITHER_IMPACT.get(det.get("impact", ""), "INFO"),
                "title": (det.get("description") or det.get("check") or "Slither finding").strip().split("\n")[0],
                "message": (det.get("description") or "").strip(),
                "file": file or str(root),
                "line": line or 0,
                "source": "web3:slither",
                "confidence": det.get("confidence", ""),
            })
        return findings


def _slither_location(det: dict):
    for el in det.get("elements", []) or []:
        sm = el.get("source_mapping") or {}
        name = sm.get("filename_relative") or sm.get("filename_short") or sm.get("filename_absolute")
        if name:
            lines = sm.get("lines") or [0]
            return name, (lines[0] if lines else 0)
    return None, None


# ── cargo-audit (Rust dependencies) ───────────────────────────────────────────

class CargoAuditScanner:
    """RustSec advisories for Cargo.lock via cargo-audit, when installed."""

    def available(self) -> bool:
        return shutil.which("cargo-audit") is not None or shutil.which("cargo") is not None

    def _lockfile(self, directory: str) -> Optional[Path]:
        return next(Path(directory).rglob("Cargo.lock"), None)

    def scan_directory(self, directory: str, timeout: int = 300) -> List[dict]:
        if not self.available():
            return []
        lock = self._lockfile(directory)
        if lock is None:
            return []
        cmd = (["cargo-audit", "audit"] if shutil.which("cargo-audit")
               else ["cargo", "audit"]) + ["--json", "-f", str(lock)]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        except Exception:
            return []
        data = _safe_json(proc.stdout)
        vulns = ((data.get("vulnerabilities") or {}).get("list")) or []
        findings: List[dict] = []
        for v in vulns:
            adv = v.get("advisory") or {}
            pkg = v.get("package") or {}
            findings.append({
                "rule_id": adv.get("id", "RUSTSEC"),
                "severity": _cvss_to_severity(adv.get("cvss")),
                "title": f"{pkg.get('name', 'crate')} {pkg.get('version', '')}: {adv.get('title', 'advisory')}".strip(),
                "message": adv.get("description", ""),
                "file": str(lock),
                "line": 0,
                "source": "sca:cargo-audit",
                "cve": ", ".join(adv.get("aliases", []) or []) or adv.get("id", ""),
            })
        return findings


def _cvss_to_severity(cvss) -> str:
    try:
        score = float(cvss)
    except (TypeError, ValueError):
        return "HIGH"          # RustSec lists it, so treat as HIGH by default
    if score >= 9.0:
        return "CRITICAL"
    if score >= 7.0:
        return "HIGH"
    if score >= 4.0:
        return "MEDIUM"
    return "LOW"
