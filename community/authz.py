# TythanAI Security Platform — Community Edition
# Copyright (c) 2026 TythanAI Labs
# Licensed under the Business Source License 1.1 (see LICENSE).

"""
community/authz.py — authorization gate for active-mode security testing.

Active testing (anything beyond reading source) is dangerous and, on systems you
don't own, illegal. TythanAI refuses to run it without a recorded authorization:
an organisation, an explicit scope, who authorised it, a reference to the signed
written permission or video statement, and an expiry. Every gated action is
appended to a tamper-evident audit log.

This module is the GATE. It does **not** contain exploits: even with valid
authorization, TythanAI only performs *non-destructive* validation (see
`active_validation.py`). It never runs denial-of-service, destructive payloads,
or attacks against third-party systems — those are out of scope and refused.
"""
from __future__ import annotations

import datetime as _dt
import fnmatch
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

DEFAULT_AUTHZ_FILE = ".tythanai-authz.json"
DEFAULT_AUDIT_LOG = ".tythanai-audit.log"


class AuthorizationError(PermissionError):
    """Raised when active testing is attempted without valid authorization."""


@dataclass
class Authorization:
    organization: str
    scope: List[str]                 # target globs the authorization covers
    authorized_by: str               # name/role of the person who authorised it
    permission_ref: str              # URL/id of the signed letter or video statement
    expires: str                     # ISO date, e.g. "2026-12-31"
    contact: str = ""
    issued: str = field(default_factory=lambda: _dt.date.today().isoformat())

    def is_valid_today(self) -> bool:
        try:
            return _dt.date.fromisoformat(self.expires) >= _dt.date.today()
        except ValueError:
            return False

    def covers(self, target: str) -> bool:
        t = str(target)
        return any(fnmatch.fnmatch(t, pat) or t.startswith(pat.rstrip("*"))
                   for pat in self.scope)

    def fingerprint(self) -> str:
        raw = f"{self.organization}|{self.authorized_by}|{self.permission_ref}|{self.expires}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def load_authorizations(path: str = DEFAULT_AUTHZ_FILE) -> List[Authorization]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    out = []
    for entry in data.get("authorizations", []):
        try:
            out.append(Authorization(**{k: entry[k] for k in (
                "organization", "scope", "authorized_by", "permission_ref", "expires")},
                contact=entry.get("contact", ""),
                issued=entry.get("issued", _dt.date.today().isoformat())))
        except (KeyError, TypeError):
            continue
    return out


class AuditLog:
    """Append-only JSONL audit trail for every gated action."""

    def __init__(self, path: str = DEFAULT_AUDIT_LOG):
        self.path = Path(path)

    def record(self, action: str, target: str, authz: Optional[Authorization],
               detail: str = "") -> None:
        entry = {
            "ts": _dt.datetime.now(_dt.timezone.utc).isoformat(),
            "action": action,
            "target": str(target),
            "authorization": authz.fingerprint() if authz else None,
            "organization": authz.organization if authz else None,
            "detail": detail,
        }
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")


def require_authorization(target: str, authz_file: str = DEFAULT_AUTHZ_FILE,
                          audit_log: str = DEFAULT_AUDIT_LOG) -> Authorization:
    """Return a valid Authorization covering `target`, or raise.

    Refuses (logs and raises) when no authorization file exists, none covers the
    target, or the covering one has expired. On success, records the grant.
    """
    log = AuditLog(audit_log)
    authorizations = load_authorizations(authz_file)
    if not authorizations:
        log.record("DENIED", target, None, "no authorization file")
        raise AuthorizationError(
            "Active testing refused: no authorization on file. Create "
            f"{authz_file} with an organisation, scope, authorizer, a reference to "
            "the signed written permission or video statement, and an expiry.")
    for authz in authorizations:
        if authz.covers(target) and authz.is_valid_today():
            log.record("AUTHORIZED", target, authz, "scope match")
            return authz
    # Distinguish expired vs out-of-scope for a clearer refusal.
    if any(a.covers(target) for a in authorizations):
        log.record("DENIED", target, None, "authorization expired")
        raise AuthorizationError("Active testing refused: authorization for this "
                                 "target has expired. Renew it before proceeding.")
    log.record("DENIED", target, None, "out of scope")
    raise AuthorizationError("Active testing refused: no authorization covers this "
                             "target. Active testing is only permitted within an "
                             "explicitly authorised scope you own.")
