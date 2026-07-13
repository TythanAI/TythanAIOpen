# TythanAI Security Platform — Community Edition
# Copyright (c) 2026 TythanAI Labs
# Licensed under the Business Source License 1.1 (see LICENSE).

"""
benchmarks/measure.py — reproducible recall/precision for the built-in engine.

Runs `CodeWeaknessScanner` over every labelled pair in `community_corpus.py`
and reports:

  * recall (TPR) — the vulnerable snippet is flagged with the declared CWE
  * false-positive rate (FPR) — the secure snippet is flagged with anything
                                (a finding on correct code is a false positive)

Run:  python -m benchmarks.measure
Exit 0 iff FPR == 0 and recall >= 0.90.
"""
from __future__ import annotations

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmarks.community_corpus import CASES, COVERAGE_GAPS   # noqa: E402
from scanners.code_weakness_scanner import CodeWeaknessScanner  # noqa: E402

_EXT = {"python": ".py", "javascript": ".js", "go": ".go", "java": ".java",
        "php": ".php", "ruby": ".rb", "csharp": ".cs"}


def _flags(scanner: CodeWeaknessScanner, code: str, lang: str) -> list:
    fd, path = tempfile.mkstemp(suffix=_EXT[lang])
    try:
        with os.fdopen(fd, "w") as fh:
            fh.write(code)
        return scanner.scan_file(path)
    finally:
        os.unlink(path)


def _score(scanner, cases):
    """Return (tp, fp, missed, false_pos) for a group of labelled cases."""
    tp = fp = 0
    missed, false_pos = [], []
    for cid, lang, cwe, vuln, secure in cases:
        if any(f["cwe"] == cwe for f in _flags(scanner, vuln, lang)):
            tp += 1
        else:
            missed.append(cid)
        secure_findings = _flags(scanner, secure, lang)
        if secure_findings:
            fp += 1
            false_pos.append((cid, secure_findings[0]["rule_id"]))
    return tp, fp, missed, false_pos


def main() -> int:
    scanner = CodeWeaknessScanner()

    m_tp, m_fp, m_missed, m_falsepos = _score(scanner, CASES)
    g_tp, g_fp, g_missed, g_falsepos = _score(scanner, COVERAGE_GAPS)

    m_n = len(CASES)
    all_n = len(CASES) + len(COVERAGE_GAPS)
    all_tp = m_tp + g_tp
    all_fp = m_fp + g_fp

    m_recall = m_tp / m_n if m_n else 0.0
    all_recall = all_tp / all_n if all_n else 0.0
    all_fpr = all_fp / all_n if all_n else 0.0
    precision = all_tp / (all_tp + all_fp) if (all_tp + all_fp) else 1.0
    m_classes = sorted({c[2] for c in CASES})
    gap_classes = sorted({c[2] for c in COVERAGE_GAPS})

    print("=" * 68)
    print("TythanAI Community — built-in offline SAST engine scorecard")
    print("=" * 68)
    print(f"Corpus       : {all_n} vulnerable/secure pairs "
          f"({m_n} modelled + {len(COVERAGE_GAPS)} out-of-model)")
    print("-" * 68)
    print(f"Modelled classes ({len(m_classes)}): {', '.join(m_classes)}")
    print(f"  recall (TPR)      : {m_recall*100:5.1f}%   ({m_tp}/{m_n})")
    print(f"Overall, incl. out-of-model taint classes "
          f"({', '.join(gap_classes)}):")
    print(f"  recall (TPR)      : {all_recall*100:5.1f}%   ({all_tp}/{all_n})")
    print(f"  false-positive    : {all_fpr*100:5.1f}%   ({all_fp}/{all_n})")
    print(f"  precision         : {precision*100:5.1f}%")
    print("-" * 68)
    if g_missed:
        print("Out-of-model (rule engine does not flow-track; Pro CPG taint does):")
        print("  " + ", ".join(g_missed))
    if m_missed:
        print("MISSED in modelled set:", ", ".join(m_missed))
    if m_falsepos or g_falsepos:
        print("FALSE POSITIVES:",
              ", ".join(f"{c}:{r}" for c, r in (m_falsepos + g_falsepos)))
    else:
        print("Zero false positives across the whole corpus.")
    print("=" * 68)

    ok = all_fp == 0 and m_recall >= 0.90
    print(f"RESULT {'PASS' if ok else 'FAIL'} "
          f"(target: 0 false positives AND modelled recall >= 90%)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
