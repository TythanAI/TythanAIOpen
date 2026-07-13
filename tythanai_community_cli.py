#!/usr/bin/env python3
# TythanAI Security Platform — Community Edition
# Copyright (c) 2026 TythanAI Labs
# Licensed under the Business Source License 1.1 (see LICENSE).

"""
tythanai_community_cli.py — Community Edition CLI entry point.

Usage:
    python tythanai_community_cli.py scan <target>  [options]
    python tythanai_community_cli.py version

Options:
    --no-sast          Skip SAST (built-in offline engine + Semgrep)
    --no-sca           Skip SCA / dependency CVE scan
    --no-secrets       Skip secrets detection
    --no-iac           Skip IaC scan
    --no-web3          Skip Web3 / smart-contract audit
    --sarif <file>     Write SARIF 2.1.0 output to <file>
    --html  <file>     Write HTML report to <file>
    --json  <file>     Write JSON findings to <file>
    --baseline <file>  Suppress findings recorded in <file>; gate CI on new ones
    --update-baseline  Record the current findings to the --baseline file (exit 0)
    --quiet            Suppress progress messages
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

# ── Ensure repo root is on the path ──────────────────────────────────────────
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from community.gates import PREMIUM_FEATURES, UPGRADE_URL
from community.scanner import CommunityScanner
from community.report import write_sarif, write_html

# ─── ANSI colours (graceful fallback on Windows/CI) ──────────────────────────

_NO_COLOR = not sys.stdout.isatty() or os.environ.get("NO_COLOR")

def _c(code: str, text: str) -> str:
    return text if _NO_COLOR else f"\033[{code}m{text}\033[0m"

RED    = lambda t: _c("31", t)
YELLOW = lambda t: _c("33", t)
GREEN  = lambda t: _c("32", t)
CYAN   = lambda t: _c("36", t)
BOLD   = lambda t: _c("1",  t)
DIM    = lambda t: _c("2",  t)
PURPLE = lambda t: _c("35", t)

_SEV_FN = {
    "CRITICAL": RED,
    "HIGH":     lambda t: _c("31;1", t),
    "MEDIUM":   YELLOW,
    "LOW":      CYAN,
    "INFO":     DIM,
}

# ─── Banner ───────────────────────────────────────────────────────────────────

_BANNER = r"""
  ______      __  __               ___    ____
 /_  __/_  __/ /_/ /_  ____ ____  /   |  /  _/
  / / / / / / __/ __ \/ __ `/ _ \/ /| |  / /
 / / / /_/ / /_/ / / / /_/ /  __/ ___ |_/ /
/_/  \__, /\__/_/ /_/\__,_/\___/_/  |_/___/
    /____/   Community Edition  v1.7
"""

def _print_banner() -> None:
    print(PURPLE(_BANNER))
    print(BOLD("  SAST · SCA · Secrets · IaC · TON · Solana · CosmWasm · Solidity"))
    print(DIM("  Free, source-available, no account required — tythanai.io\n"))

# ─── Summary helpers ──────────────────────────────────────────────────────────

_RISK_COLORS = {
    "CRITICAL": RED, "HIGH": lambda t: _c("31;1", t),
    "MEDIUM": YELLOW, "LOW": CYAN, "CLEAN": GREEN,
}

def _print_summary(result) -> None:
    risk = result.risk_level()
    risk_fn = _RISK_COLORS.get(risk, DIM)
    sev = result.by_severity

    print()
    print(BOLD("━" * 60))
    print(BOLD("  SCAN SUMMARY"))
    print(BOLD("━" * 60))
    print(f"  Target    : {result.target}")
    print(f"  Risk      : {risk_fn(BOLD(risk))} ({result.risk_score()}/100)")
    print(f"  Findings  : {BOLD(str(result.total))}")
    print()
    print(f"  {'CRITICAL':10s} {RED(str(sev['CRITICAL'])):>4}")
    print(f"  {'HIGH':10s} {_c('31;1',str(sev['HIGH'])):>4}")
    print(f"  {'MEDIUM':10s} {YELLOW(str(sev['MEDIUM'])):>4}")
    print(f"  {'LOW':10s} {CYAN(str(sev['LOW'])):>4}")
    print(f"  {'INFO':10s} {DIM(str(sev['INFO'])):>4}")
    print()
    print(f"  SAST     : {len(result.sast_findings)} findings")
    print(f"  SCA/CVE  : {len(result.sca_findings)} findings")
    print(f"  Secrets  : {len(result.secrets_findings)} findings")
    print(f"  IaC      : {len(result.iac_findings)} findings")
    print(f"  Web3     : {len(result.web3_findings)} findings")

    if result.errors:
        print()
        print(YELLOW("  Partial scan warnings:"))
        for e in result.errors:
            print(DIM(f"    · {e}"))

    print(BOLD("━" * 60))


def _print_findings(result, quiet: bool) -> None:
    if quiet or not result.all_findings:
        return
    print()
    print(BOLD("  FINDINGS"))
    print()
    for i, f in enumerate(result.all_findings, 1):
        sev = f.get("severity", "INFO").upper()
        fn  = _SEV_FN.get(sev, DIM)
        title = f.get("title", f.get("message", "Finding"))
        file_ = f.get("file", "")
        line  = f.get("line", "")
        src   = f.get("source", "")
        loc   = f"{file_}:{line}" if file_ and line else file_
        print(f"  {DIM(str(i).rjust(3))}  {fn(sev.ljust(8))}  {BOLD(title)}")
        if loc:
            print(f"        {DIM(loc)}")
        rule_id = f.get("rule_id", f.get("id", ""))
        if rule_id:
            print(f"        {DIM(rule_id + '  [' + src + ']')}")
        print()


def _print_gated(result) -> None:
    shown = set()
    lines = []
    for g in result.gated_features:
        if g.feature_key not in shown:
            shown.add(g.feature_key)
            desc = PREMIUM_FEATURES.get(g.feature_key, g.feature_key)
            lines.append(f"  🔒  {desc}")
    if lines:
        print()
        print(BOLD("  PREMIUM FEATURES (not included in Community Edition)"))
        for l in lines:
            print(DIM(l))
        print()
        print(f"  {BOLD('Upgrade:')} {CYAN(UPGRADE_URL)}")
        print()


# ─── Command handlers ─────────────────────────────────────────────────────────

def cmd_scan(args) -> int:
    target = args.target
    if not Path(target).exists():
        print(RED(f"Error: target not found: {target}"), file=sys.stderr)
        return 1

    if not args.quiet:
        _print_banner()
        print(f"  Scanning {BOLD(target)} …\n")

    t0 = time.monotonic()
    scanner = CommunityScanner(target)
    result = scanner.run(
        sast=not args.no_sast,
        sca=not args.no_sca,
        secrets=not args.no_secrets,
        iac=not args.no_iac,
        web3=not args.no_web3,
    )
    elapsed = time.monotonic() - t0

    # ── Baseline handling ──────────────────────────────────────────────────────
    if args.update_baseline:
        if not args.baseline:
            print(RED("Error: --update-baseline requires --baseline <file>"), file=sys.stderr)
            return 1
        from community.baseline import save as _save_baseline
        n = _save_baseline(args.baseline, result.all_findings, result.target)
        if not args.quiet:
            print(GREEN(f"  Baseline written → {args.baseline} ({n} fingerprints)"))
            print()
        return 0

    suppressed = 0
    if args.baseline:
        from community.baseline import load as _load_baseline, apply as _apply_baseline
        suppressed = _apply_baseline(result, _load_baseline(args.baseline), result.target)

    _print_findings(result, args.quiet)
    _print_summary(result)
    if suppressed and not args.quiet:
        print(DIM(f"  Baseline: {suppressed} known finding(s) suppressed — showing new only"))
    _print_gated(result)

    if not args.quiet:
        print(DIM(f"  Completed in {elapsed:.1f}s"))
        print()

    # ── Output files ──────────────────────────────────────────────────────────
    if args.sarif:
        write_sarif(result, args.sarif)
        if not args.quiet:
            print(f"  SARIF   → {args.sarif}")

    if args.html:
        write_html(result, args.html)
        if not args.quiet:
            print(f"  HTML    → {args.html}")

    if args.json:
        payload = {
            "target": result.target,
            "risk_level": result.risk_level(),
            "risk_score": result.risk_score(),
            "total": result.total,
            "by_severity": result.by_severity,
            "findings": result.all_findings,
        }
        Path(args.json).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        if not args.quiet:
            print(f"  JSON    → {args.json}")

    # Exit code: 0 = clean / info only, 1 = low+, 2 = medium+, 3 = critical/high
    risk = result.risk_level()
    if risk == "CLEAN":      return 0
    if risk == "LOW":        return 1
    if risk == "MEDIUM":     return 2
    return 3


def _scan_for_findings(target: str) -> list:
    scanner = CommunityScanner(target)
    return scanner.run().all_findings


def cmd_explain(args) -> int:
    from community.ai.assistant import SecurityAssistant
    if not Path(args.target).exists():
        print(RED(f"Error: target not found: {args.target}"), file=sys.stderr)
        return 1
    findings = _scan_for_findings(args.target)
    assistant = SecurityAssistant()
    print(DIM(f"  AI provider: {assistant.provider_name()}  ·  {len(findings)} findings\n"))
    if not findings:
        print(GREEN("  No findings to explain — looks clean."))
        return 0
    for i, f in enumerate(findings[: args.limit], 1):
        print(BOLD(f"[{i}] ") + assistant.explain(f))
        print()
    return 0


def cmd_ask(args) -> int:
    from community.ai.assistant import SecurityAssistant
    findings = _scan_for_findings(args.scan) if args.scan and Path(args.scan).exists() else []
    assistant = SecurityAssistant()
    print(DIM(f"  AI provider: {assistant.provider_name()}\n"))
    print(assistant.ask(args.question, findings))
    return 0


def cmd_chat(args) -> int:
    from community.ai.assistant import SecurityAssistant
    findings = _scan_for_findings(args.scan) if args.scan and Path(args.scan).exists() else []
    assistant = SecurityAssistant()
    print(BOLD("TythanAI chat") + DIM(f"  (provider: {assistant.provider_name()}, "
          f"{len(findings)} findings in context) — type 'exit' to quit\n"))
    while True:
        try:
            q = input(CYAN("you › "))
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if q.strip().lower() in ("exit", "quit", ":q"):
            break
        if not q.strip():
            continue
        print(BOLD("tythanai › ") + assistant.ask(q, findings) + "\n")
    return 0


def cmd_validate(args) -> int:
    """Authorization-gated, non-destructive exploitability assessment.

    Refuses outright unless an authorization file covers the target — see
    `community/authz.py`. Never runs live exploitation, DoS, or destructive
    payloads, with or without authorization; see `community/active_validation.py`.
    """
    from community.active_validation import ActiveValidator
    from community.authz import AuthorizationError

    if not Path(args.target).exists():
        print(RED(f"Error: target not found: {args.target}"), file=sys.stderr)
        return 1

    validator = ActiveValidator(authz_file=args.authz_file, audit_log=args.audit_log)
    findings = _scan_for_findings(args.target)
    if args.severity:
        order = {"INFO": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
        floor = order.get(args.severity.upper(), 1)
        findings = [f for f in findings
                   if order.get(str(f.get("severity", "INFO")).upper(), 0) >= floor]
    if not findings:
        print(GREEN("  No findings to validate."))
        return 0

    try:
        results = [validator.validate(findings[0], args.target)]
    except AuthorizationError as exc:
        print(RED(f"  {exc}"))
        template = {"authorizations": [{
            "organization": "Your Company",
            "scope": [f"{args.target}/*"],
            "authorized_by": "CISO / person who signed off",
            "permission_ref": "URL or id of the signed letter or recorded video statement",
            "expires": "2026-12-31",
        }]}
        print(DIM(f"\n  Create {args.authz_file} to enable validation, e.g.:\n"
                  + json.dumps(template, indent=2)))
        return 1

    for f in findings[1: args.limit]:
        try:
            results.append(validator.validate(f, args.target))
        except AuthorizationError:
            break

    print(BOLD(f"  Authorized for: {results[0]['authorized_org']}") +
          DIM(f"  (authorization {results[0]['authorization']})\n"))
    for i, r in enumerate(results, 1):
        print(BOLD(f"[{i}] {r['rule_id']} ") + DIM(f"({r['cwe']})"))
        print(f"    Statically reachable: {r['statically_reachable']}")
        print(f"    {r['reproduction_note']}")
    print(DIM(f"\n  {results[0]['note']}"))
    print(DIM(f"  Audit log: {args.audit_log}"))
    return 0


def cmd_version(args) -> int:
    print("TythanAI Community Edition v1.7.0")
    print("Copyright (c) 2026 TythanAI Labs — BSL 1.1")
    print("https://tythanai.io")
    return 0


# ─── Argument parser ──────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="tythanai-community",
        description="TythanAI Community Edition — Web3-native security scanner",
    )
    sub = p.add_subparsers(dest="command")

    scan = sub.add_parser("scan", help="Scan a directory or file")
    scan.add_argument("target", help="Path to scan")
    scan.add_argument("--no-sast",    action="store_true")
    scan.add_argument("--no-sca",     action="store_true")
    scan.add_argument("--no-secrets", action="store_true")
    scan.add_argument("--no-iac",     action="store_true")
    scan.add_argument("--no-web3",    action="store_true")
    scan.add_argument("--sarif", metavar="FILE")
    scan.add_argument("--html",  metavar="FILE")
    scan.add_argument("--json",  metavar="FILE")
    scan.add_argument("--baseline", metavar="FILE",
                      help="suppress findings recorded in FILE (report only new ones)")
    scan.add_argument("--update-baseline", action="store_true",
                      help="write current findings to the --baseline file and exit 0")
    scan.add_argument("--quiet", "-q", action="store_true")

    ex = sub.add_parser("explain", help="Scan a target and explain each finding")
    ex.add_argument("target", help="Path to scan")
    ex.add_argument("--limit", type=int, default=20, help="Max findings to explain")

    ask = sub.add_parser("ask", help="Ask a security question (optionally about a scan)")
    ask.add_argument("question", help="Your question, in quotes")
    ask.add_argument("--scan", metavar="PATH", help="Scan PATH first and use it as context")

    chat = sub.add_parser("chat", help="Interactive security chat")
    chat.add_argument("--scan", metavar="PATH", help="Scan PATH first and use it as context")

    val = sub.add_parser("validate", help="Authorization-gated, non-destructive exploitability "
                                          "assessment (owners with written/video permission only)")
    val.add_argument("target", help="Path to scan and validate")
    val.add_argument("--authz-file", default=".tythanai-authz.json",
                     help="Authorization file (default: .tythanai-authz.json)")
    val.add_argument("--audit-log", default=".tythanai-audit.log",
                     help="Append-only audit log (default: .tythanai-audit.log)")
    val.add_argument("--severity", help="Minimum severity to validate")
    val.add_argument("--limit", type=int, default=10, help="Max findings to validate")

    sub.add_parser("version", help="Show version information")

    return p


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    dispatch = {
        "scan": cmd_scan,
        "explain": cmd_explain,
        "ask": cmd_ask,
        "chat": cmd_chat,
        "validate": cmd_validate,
        "version": cmd_version,
    }
    handler = dispatch.get(args.command)
    if handler:
        sys.exit(handler(args))
    parser.print_help()
    sys.exit(0)


if __name__ == "__main__":
    main()
