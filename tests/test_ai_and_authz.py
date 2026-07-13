# TythanAI Security Platform — Community Edition
# Copyright (c) 2026 TythanAI Labs
# Licensed under the Business Source License 1.1 (see LICENSE).

"""Tests for evasion detection, the AI assistant (offline), MCP tools, authz gate."""
from __future__ import annotations

import base64
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from community import active_validation, authz            # noqa: E402
from community.ai.assistant import SecurityAssistant       # noqa: E402
from community.ai.knowledge import offline_explanation, lookup  # noqa: E402
from community.ai.providers import OfflineProvider, select_provider  # noqa: E402
from community.mcp_server import (                          # noqa: E402
    explain_finding_impl,
    list_rules_impl,
    scan_path_impl,
)
from scanners.evasion_scanner import EvasionScanner         # noqa: E402
import tythanai_community_cli as cli                         # noqa: E402


# ── Anti-evasion ──────────────────────────────────────────────────────────────

def test_evasion_detects_base64_payload():
    blob = base64.b64encode(b"os.system(cmd)").decode()
    findings = EvasionScanner().scan_text(f'p = "{blob}"')
    assert any(f["rule_id"] == "TYT-E001" for f in findings)


def test_evasion_detects_split_string():
    findings = EvasionScanner().scan_text('fn = "ev" + "al"')
    assert any(f["cwe"] == "CWE-506" for f in findings)


def test_evasion_no_false_positive_on_benign():
    benign = base64.b64encode(b"just a normal caption string here").decode()
    assert EvasionScanner().scan_text(f'caption = "{benign}"') == []
    assert EvasionScanner().scan_text("def add(a, b):\n    return a + b") == []


def test_evasion_detects_charcode_python():
    chain = "+".join(f"chr({ord(c)})" for c in "eval")
    findings = EvasionScanner().scan_text(f"fn = {chain}")
    assert any(f["rule_id"] == "TYT-E001" and "eval" in f["evidence"] for f in findings)


def test_evasion_detects_charcode_js():
    findings = EvasionScanner().scan_text("var fn = String.fromCharCode(101,118,97,108);")
    assert any(f["cwe"] == "CWE-506" for f in findings)


def test_evasion_no_false_positive_on_short_charcode():
    assert EvasionScanner().scan_text("var c = String.fromCharCode(65);") == []


# ── AI knowledge base / assistant (offline) ───────────────────────────────────

def test_knowledge_base_covers_scanner_cwes():
    for cwe in ("CWE-327", "CWE-89", "CWE-78", "CWE-502", "CWE-95", "CWE-643", "CWE-90"):
        assert lookup(cwe), f"missing KB entry for {cwe}"


def test_offline_explanation_is_actionable():
    f = {"title": "SQL injection", "cwe": "CWE-89", "severity": "HIGH",
         "file": "app.py", "line": 5}
    text = offline_explanation(f)
    assert "parameter" in text.lower() and "CWE-89" in text and "app.py:5" in text


def test_assistant_offline_by_default():
    a = SecurityAssistant(provider=OfflineProvider())
    assert a.provider_name() == "offline"
    out = a.explain({"cwe": "CWE-327", "title": "Weak hash", "severity": "MEDIUM"})
    assert "SHA-256" in out


def test_select_provider_defaults_offline(monkeypatch):
    monkeypatch.delenv("TYTHANAI_AI", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert select_provider().name == "offline"


def test_ask_offline_summarises(tmp_path):
    a = SecurityAssistant(provider=OfflineProvider())
    findings = [{"severity": "HIGH", "cwe": "CWE-89"}, {"severity": "LOW", "cwe": "CWE-327"}]
    out = a.ask("what's worst?", findings)
    assert "2 findings" in out


# ── MCP tool implementations ──────────────────────────────────────────────────

def test_mcp_scan_path(tmp_path):
    (tmp_path / "a.py").write_text("import os\nos.system(x)\n")
    result = scan_path_impl(str(tmp_path))
    assert result["total"] >= 1
    assert "risk_level" in result and "findings" in result


def test_mcp_scan_path_missing():
    assert "error" in scan_path_impl("/no/such/path")


def test_mcp_list_rules_filter():
    all_rules = list_rules_impl()
    py = list_rules_impl("python")
    assert all_rules["count"] > py["count"] > 0
    assert all(r.startswith("TYT-P") for r in py["rules"])


def test_mcp_explain_finding():
    out = explain_finding_impl(json.dumps({"cwe": "CWE-89", "title": "SQLi", "severity": "HIGH"}))
    assert "CWE-89" in out


# ── Authorization gate ────────────────────────────────────────────────────────

def _write_authz(tmp_path, scope, expires):
    p = tmp_path / "authz.json"
    p.write_text(json.dumps({"authorizations": [{
        "organization": "Acme Corp", "scope": scope, "authorized_by": "CISO",
        "permission_ref": "https://acme/letter.pdf", "expires": expires,
    }]}))
    return str(p)


def test_authz_refuses_without_file(tmp_path):
    with pytest.raises(authz.AuthorizationError):
        authz.require_authorization(str(tmp_path / "x"),
                                    authz_file=str(tmp_path / "none.json"),
                                    audit_log=str(tmp_path / "audit.log"))


def test_authz_grants_in_scope(tmp_path):
    af = _write_authz(tmp_path, [f"{tmp_path}/*"], "2999-01-01")
    a = authz.require_authorization(str(tmp_path / "app"), authz_file=af,
                                    audit_log=str(tmp_path / "audit.log"))
    assert a.organization == "Acme Corp"


def test_authz_refuses_out_of_scope(tmp_path):
    af = _write_authz(tmp_path, ["/only/this/*"], "2999-01-01")
    with pytest.raises(authz.AuthorizationError):
        authz.require_authorization("/somewhere/else", authz_file=af,
                                    audit_log=str(tmp_path / "audit.log"))


def test_authz_refuses_expired(tmp_path):
    af = _write_authz(tmp_path, [f"{tmp_path}/*"], "2000-01-01")
    with pytest.raises(authz.AuthorizationError):
        authz.require_authorization(str(tmp_path / "app"), authz_file=af,
                                    audit_log=str(tmp_path / "audit.log"))


def test_authz_writes_audit_log(tmp_path):
    af = _write_authz(tmp_path, [f"{tmp_path}/*"], "2999-01-01")
    log = str(tmp_path / "audit.log")
    authz.require_authorization(str(tmp_path / "app"), authz_file=af, audit_log=log)
    assert "AUTHORIZED" in open(log).read()


# ── Non-destructive active validation ─────────────────────────────────────────

def test_validator_refuses_destructive(tmp_path):
    af = _write_authz(tmp_path, [f"{tmp_path}/*"], "2999-01-01")
    v = active_validation.ActiveValidator(authz_file=af, audit_log=str(tmp_path / "a.log"))
    with pytest.raises(authz.AuthorizationError):
        v.validate({"cwe": "CWE-89"}, str(tmp_path / "app"), action="dos")


def test_validator_requires_authorization(tmp_path):
    v = active_validation.ActiveValidator(authz_file=str(tmp_path / "none.json"),
                                          audit_log=str(tmp_path / "a.log"))
    with pytest.raises(authz.AuthorizationError):
        v.validate({"cwe": "CWE-89"}, str(tmp_path / "app"))


def test_validator_assessment_is_non_destructive(tmp_path):
    af = _write_authz(tmp_path, [f"{tmp_path}/*"], "2999-01-01")
    v = active_validation.ActiveValidator(authz_file=af, audit_log=str(tmp_path / "a.log"))
    out = v.validate({"cwe": "CWE-89", "file": "app.py", "line": 5, "rule_id": "TYT-P010"},
                     str(tmp_path / "app"))
    assert out["non_destructive"] is True
    assert out["live_exploitation_performed"] is False
    assert out["statically_reachable"] is True


# ── `tythanai validate` CLI wiring ─────────────────────────────────────────────

def test_cli_validate_refuses_without_authorization(tmp_path, capsys):
    target = tmp_path / "app"
    target.mkdir()
    (target / "a.py").write_text("import os\nos.system(x)\n")
    parser = cli._build_parser()
    args = parser.parse_args(["validate", str(target),
                              "--authz-file", str(tmp_path / "none.json"),
                              "--audit-log", str(tmp_path / "a.log")])
    assert cli.cmd_validate(args) == 1
    out = capsys.readouterr().out
    assert "refused" in out.lower()
    assert "organization" in out  # prints a template authz file to unblock the user


def test_cli_validate_succeeds_with_authorization(tmp_path, capsys):
    target = tmp_path / "app"
    target.mkdir()
    (target / "a.py").write_text("import os\nos.system(x)\n")
    authz_file = _write_authz(tmp_path, [f"{tmp_path}/*"], "2999-01-01")
    parser = cli._build_parser()
    args = parser.parse_args(["validate", str(target),
                              "--authz-file", authz_file,
                              "--audit-log", str(tmp_path / "a.log")])
    assert cli.cmd_validate(args) == 0
    out = capsys.readouterr().out
    assert "Acme Corp" in out
    assert "Audit log" in out
