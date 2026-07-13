# TythanAI Security Platform — Community Edition
# Copyright (c) 2026 TythanAI Labs
# Licensed under the Business Source License 1.1 (see LICENSE).

"""
community/mcp_server.py — expose TythanAI as MCP tools.

Model Context Protocol (MCP) is how agentic environments — Claude Code, Cursor,
VS Code (Continue/Cline), and the Claude API's `mcp_servers` — plug in external
tools. Running this server lets the agent *scan code, explain findings, and get
fix suggestions* locally, as tool calls, right inside the IDE.

Run it:                  python -m community.mcp_server
Install the MCP runtime: pip install "mcp[cli]"

Register in Claude Code / Cursor (`.mcp.json`):

    {
      "mcpServers": {
        "tythanai": { "command": "python", "args": ["-m", "community.mcp_server"] }
      }
    }

The tool logic lives in plain functions below (import-safe and unit-tested); the
MCP wrappers are thin.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


# ── Tool implementations (always importable; no MCP dependency) ───────────────

def scan_path_impl(path: str, min_severity: str = "LOW") -> dict:
    """Run a TythanAI scan and return a structured summary + findings."""
    from community.scanner import CommunityScanner
    if not Path(path).exists():
        return {"error": f"path not found: {path}"}
    result = CommunityScanner(path).run()
    order = {"INFO": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
    floor = order.get(min_severity.upper(), 1)
    findings = [
        {k: f.get(k) for k in ("rule_id", "severity", "title", "cwe", "file", "line", "source")}
        for f in result.all_findings
        if order.get(str(f.get("severity", "INFO")).upper(), 0) >= floor
    ]
    return {
        "target": result.target,
        "risk_level": result.risk_level(),
        "risk_score": result.risk_score(),
        "total": len(findings),
        "by_severity": result.by_severity,
        "findings": findings[:200],
    }


def explain_finding_impl(finding_json: str) -> str:
    """Explain a finding (JSON dict) — grounded, offline-capable."""
    from community.ai.assistant import SecurityAssistant
    try:
        finding = json.loads(finding_json)
    except (ValueError, TypeError):
        return "Invalid finding JSON."
    return SecurityAssistant().explain(finding)


def suggest_fix_impl(finding_json: str, code: str = "") -> str:
    """Propose a fix for a finding, optionally given the surrounding code."""
    from community.ai.assistant import SecurityAssistant
    try:
        finding = json.loads(finding_json)
    except (ValueError, TypeError):
        return "Invalid finding JSON."
    return SecurityAssistant().propose_fix(finding, code)


def list_rules_impl(language: Optional[str] = None) -> dict:
    """List the built-in SAST rules, optionally filtered by language prefix."""
    from scanners.code_weakness_scanner import RULES
    prefix = {
        "python": "TYT-P", "javascript": "TYT-J", "go": "TYT-G", "java": "TYT-A",
        "php": "TYT-H", "ruby": "TYT-R", "csharp": "TYT-C", "kotlin": "TYT-K",
        "rust": "TYT-U", "cpp": "TYT-X",
    }.get((language or "").lower())
    rules = {rid: m for rid, m in RULES.items() if not prefix or rid.startswith(prefix)}
    return {"count": len(rules), "rules": rules}


# ── MCP wiring (optional dependency) ──────────────────────────────────────────

def main() -> int:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        print("The MCP runtime is not installed. Install it with:\n"
              "    pip install \"mcp[cli]\"\n"
              "then run:  python -m community.mcp_server")
        return 1

    server = FastMCP("tythanai")

    @server.tool()
    def scan_path(path: str, min_severity: str = "LOW") -> dict:
        """Scan a file or directory for security issues (SAST/SCA/secrets/IaC/Web3)."""
        return scan_path_impl(path, min_severity)

    @server.tool()
    def explain_finding(finding_json: str) -> str:
        """Explain a single finding (pass a finding object as a JSON string)."""
        return explain_finding_impl(finding_json)

    @server.tool()
    def suggest_fix(finding_json: str, code: str = "") -> str:
        """Suggest a concrete fix for a finding, given the finding and its code."""
        return suggest_fix_impl(finding_json, code)

    @server.tool()
    def list_rules(language: str = "") -> dict:
        """List built-in SAST rules; optionally filter by language."""
        return list_rules_impl(language or None)

    server.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
