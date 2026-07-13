# TythanAI Security Platform — Community Edition
# Copyright (c) 2026 TythanAI Labs
# Licensed under the Business Source License 1.1 (see LICENSE).

"""
community/ai/assistant.py — the security assistant.

Explains findings, proposes fixes, and answers free-form questions about a scan.
It always grounds answers in the deterministic knowledge base, then (if a
provider is configured) asks the LLM to expand — so it is useful offline and
smarter online.
"""
from __future__ import annotations

from typing import List, Optional

from community.ai.knowledge import lookup, offline_explanation
from community.ai.providers import select_provider

_SYSTEM = (
    "You are TythanAI, a precise application-security assistant. You explain "
    "vulnerabilities, their real-world impact, and concrete fixes for the user's "
    "code. Be specific and actionable; show corrected code when useful. Never "
    "invent findings, and never provide instructions for attacking systems the "
    "user does not own. If unsure, say so."
)


class SecurityAssistant:
    def __init__(self, provider=None):
        self.provider = provider or select_provider()

    # ── Explain a single finding ──────────────────────────────────────────────
    def explain(self, finding: dict, code: str = "") -> str:
        base = offline_explanation(finding)
        if self.provider.name == "offline":
            return base
        cwe = finding.get("cwe", "")
        entry = lookup(cwe) or {}
        context = (
            f"Finding: {finding.get('title','')} ({cwe}) at "
            f"{finding.get('file','')}:{finding.get('line','')}\n"
            f"Rule: {finding.get('rule_id','')}  Severity: {finding.get('severity','')}\n"
            f"Known guidance: {entry.get('why','')} Fix: {entry.get('fix','')}\n"
            + (f"Code:\n{code}\n" if code else "")
        )
        prompt = ("Explain this finding to the developer: why it's exploitable in "
                  "their context and the smallest change that fixes it. Keep it tight.")
        try:
            return base + "\n\n— AI analysis —\n" + self.provider.complete(_SYSTEM, prompt, context)
        except Exception as exc:
            return base + f"\n\n(AI provider error: {exc})"

    # ── Propose a fix diff ────────────────────────────────────────────────────
    def propose_fix(self, finding: dict, code: str) -> str:
        entry = lookup(finding.get("cwe", "")) or {}
        if self.provider.name == "offline":
            fix = entry.get("fix", "Apply the standard remediation for this class.")
            return f"Recommended fix ({finding.get('cwe','')}): {fix}"
        context = (f"Vulnerable code for {finding.get('rule_id','')} "
                   f"({finding.get('cwe','')}):\n{code}\nGuidance: {entry.get('fix','')}")
        prompt = ("Rewrite only the vulnerable part to fix it, preserving behaviour. "
                  "Output the corrected code plus one sentence explaining the change.")
        try:
            return self.provider.complete(_SYSTEM, prompt, context)
        except Exception as exc:
            fix = entry.get("fix", "")
            return f"Recommended fix: {fix}\n(AI provider error: {exc})"

    # ── Free-form question about a scan ───────────────────────────────────────
    def ask(self, question: str, findings: Optional[List[dict]] = None) -> str:
        findings = findings or []
        summary = _summarise(findings)
        if self.provider.name == "offline":
            return (f"[offline] {summary}\n\nAsk again with an AI provider "
                    "(TYTHANAI_AI=ollama|claude) for a reasoned answer. "
                    "Meanwhile, `tythanai explain` gives per-finding guidance.")
        context = f"Scan summary:\n{summary}"
        try:
            return self.provider.complete(_SYSTEM, question, context)
        except Exception as exc:
            return f"{summary}\n(AI provider error: {exc})"

    def provider_name(self) -> str:
        return self.provider.name


def _summarise(findings: List[dict]) -> str:
    if not findings:
        return "No findings provided."
    by_sev: dict = {}
    by_cwe: dict = {}
    for f in findings:
        by_sev[f.get("severity", "INFO")] = by_sev.get(f.get("severity", "INFO"), 0) + 1
        if f.get("cwe"):
            by_cwe[f["cwe"]] = by_cwe.get(f["cwe"], 0) + 1
    sev = " · ".join(f"{k} {v}" for k, v in sorted(by_sev.items()))
    top = ", ".join(f"{k} ×{v}" for k, v in sorted(by_cwe.items(), key=lambda x: -x[1])[:5])
    return f"{len(findings)} findings ({sev}). Most common: {top or 'n/a'}."
