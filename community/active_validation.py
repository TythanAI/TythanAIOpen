# TythanAI Security Platform — Community Edition
# Copyright (c) 2026 TythanAI Labs
# Licensed under the Business Source License 1.1 (see LICENSE).

"""
community/active_validation.py — authorization-gated, non-destructive validation.

Given a finding and a valid authorization (see `authz.py`), this produces an
*exploitability assessment* — static reachability plus a harmless, local
reproduction description — so an authorised owner can confirm a finding is real.

Hard boundaries, enforced in code:
  * No live exploitation of any system.
  * No denial-of-service, destructive payloads, or data modification.
  * Nothing that targets a system outside the authorised scope.

Live active testing (DAST, sandboxed PoC execution) is a Pro/Enterprise
capability and is itself authorization-gated. The Community Edition ships the
gate and a safe assessment so the workflow is auditable end to end.
"""
from __future__ import annotations

from typing import Optional

from community.authz import (
    Authorization,
    AuditLog,
    AuthorizationError,
    require_authorization,
)

# Verbs we refuse outright, with or without authorization.
_FORBIDDEN = {
    "dos", "ddos", "flood", "bruteforce", "brute-force", "wipe", "destroy",
    "drop-table", "delete-data", "ransomware", "exfiltrate", "lateral-movement",
    "deploy-payload", "weaponize",
}

# Non-destructive, class-specific reproduction notes (descriptions, not attacks).
_REPRO = {
    "CWE-89": "In an owned test database, run the flagged query with an input like "
              "`1 OR 1=1` and confirm it returns more rows than intended. Do not run "
              "this against production or third-party systems.",
    "CWE-78": "In an isolated container you own, pass an input containing `; id` and "
              "confirm the extra command runs. Never do this on shared or production hosts.",
    "CWE-79": "In a local test page, submit `<img src=x onerror=alert(1)>` and confirm "
              "it renders/executes. Keep it to your own test instance.",
    "CWE-502": "In a sandbox, deserialize a benign marker object and confirm the sink "
               "constructs it. Do not deserialize a real gadget chain.",
    "CWE-327": "No exploitation needed — the weakness is the algorithm choice; confirm "
               "by code review and replace with a strong primitive.",
    "CWE-295": "In a test client, present a self-signed cert and confirm the client "
               "accepts it (proving verification is off). Own both ends.",
}


def refuse_if_destructive(action: str) -> None:
    if str(action).strip().lower() in _FORBIDDEN:
        raise AuthorizationError(
            f"Refused: '{action}' is destructive/offensive and is never performed by "
            "TythanAI, regardless of authorization.")


class ActiveValidator:
    """Runs only non-destructive validation, and only within an authorised scope."""

    def __init__(self, authz_file: str = ".tythanai-authz.json",
                 audit_log: str = ".tythanai-audit.log"):
        self.authz_file = authz_file
        self.audit_log = audit_log
        self._log = AuditLog(audit_log)

    def validate(self, finding: dict, target: str, action: str = "assess") -> dict:
        """Return a non-destructive exploitability assessment for a finding.

        Raises AuthorizationError if the target isn't covered by a valid
        authorization, or if a destructive action is requested.
        """
        refuse_if_destructive(action)
        authz: Authorization = require_authorization(target, self.authz_file, self.audit_log)

        cwe = str(finding.get("cwe", "")).upper()
        reachable = bool(finding.get("file")) and finding.get("line", 0) not in (None, 0)
        assessment = {
            "authorized_org": authz.organization,
            "authorization": authz.fingerprint(),
            "non_destructive": True,
            "live_exploitation_performed": False,
            "target": str(target),
            "rule_id": finding.get("rule_id", ""),
            "cwe": cwe,
            "statically_reachable": reachable,
            "reproduction_note": _REPRO.get(cwe, "Confirm by code review in an "
                                            "environment you own; no live test provided "
                                            "for this class in the Community Edition."),
            "note": "Community Edition performs assessment only. Sandbox/DAST PoC "
                    "execution is a Pro/Enterprise capability and remains "
                    "authorization-gated.",
        }
        self._log.record("ASSESSED", target, authz, f"rule={finding.get('rule_id','')}")
        return assessment
