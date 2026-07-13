# TythanAI Security Platform — Community Edition
# Copyright (c) 2026 TythanAI Labs
# Licensed under the Business Source License 1.1 (see LICENSE).

"""Tests for the optional external-tool integrations (graceful when absent)."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scanners.external_tools import (                 # noqa: E402
    CargoAuditScanner,
    SlitherScanner,
    _cvss_to_severity,
    _safe_json,
    _slither_location,
)


# ── Graceful behaviour when the tool / target is absent ───────────────────────

def test_slither_available_is_bool():
    assert isinstance(SlitherScanner().available(), bool)


def test_cargo_available_is_bool():
    assert isinstance(CargoAuditScanner().available(), bool)


def test_slither_no_sol_files_returns_empty(tmp_path):
    (tmp_path / "app.py").write_text("x = 1\n")
    assert SlitherScanner().scan_directory(str(tmp_path)) == []


def test_cargo_no_lockfile_returns_empty(tmp_path):
    (tmp_path / "main.rs").write_text("fn main() {}\n")
    assert CargoAuditScanner().scan_directory(str(tmp_path)) == []


# ── Pure parsing/normalisation (no external process needed) ───────────────────

def test_safe_json_handles_garbage():
    assert _safe_json("not json") == {}
    assert _safe_json("") == {}
    assert _safe_json('{"a": 1}') == {"a": 1}
    assert _safe_json("[1,2]") == {}          # top-level must be an object


def test_cvss_to_severity_buckets():
    assert _cvss_to_severity(9.8) == "CRITICAL"
    assert _cvss_to_severity(7.5) == "HIGH"
    assert _cvss_to_severity(5.0) == "MEDIUM"
    assert _cvss_to_severity(2.0) == "LOW"
    assert _cvss_to_severity(None) == "HIGH"   # listed but unscored → HIGH


def test_slither_location_extracts_file_and_line():
    det = {"elements": [{"source_mapping": {
        "filename_relative": "contracts/Vault.sol", "lines": [42, 43]}}]}
    assert _slither_location(det) == ("contracts/Vault.sol", 42)


def test_slither_location_missing_is_none():
    assert _slither_location({"elements": []}) == (None, None)
