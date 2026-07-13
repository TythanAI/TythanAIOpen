# Changelog

All notable changes to **TythanAI Community Edition** are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/); versions
follow [Semantic Versioning](https://semver.org/).

## [1.4.0]

### Added
- Built-in offline SAST engine extended to **PHP, Ruby and C#** (now 7
  languages: Python, JS/TS, Go, Java, PHP, Ruby, C#).
- Intra-module taint: dynamic SQL passed into a query-helper function is now
  detected (`TYT-P015`, CWE-89), closing the previous cross-function gap.
- SARIF output now emits a full rule catalogue with CWE tags and a
  `security-severity` score, so GitHub Code Scanning ranks alerts correctly.

### Changed
- Benchmark corpus grown to 56 vulnerable/secure pairs across 7 languages.
  Modelled recall 100% (53/53); overall incl. out-of-model taint classes
  **94.6%** (53/56); still **zero false positives**.
- Honest remaining blind spots: SSRF, second-order (stored) SQL, open redirect.

## [1.3.0]

### Added
- Built-in SAST engine extended to **Go and Java**.
- New Python detectors: insecure randomness (CWE-330), XXE (CWE-611),
  user-controlled path into `open()` (CWE-22), and a local def-use pass that
  catches SQL assembled into a variable before execution (CWE-89).

### Changed
- Overall benchmark recall raised from 83.3% to 92.7% by detecting more
  classes (not by changing the measure). Zero false positives maintained.

## [1.2.0]

### Added
- **Built-in, offline SAST rule engine** (`scanners/code_weakness_scanner.py`):
  weak crypto, unsafe deserialization, disabled TLS verification, `eval`/`exec`,
  command injection and dynamic SQL — runs with no external tools or network, so
  `tythanai scan` always produces SAST results even without Semgrep.
- Reproducible benchmark harness (`benchmarks/`, `python -m benchmarks.measure`)
  with a labelled corpus and an honest coverage map.

### Changed
- README "Transparency" section now reports reproducible community-corpus
  numbers instead of the platform taint-engine figures.

## [1.1.0]

### Added
- Animated SVG banner and live scan-terminal for the README, matching the
  product UI.
- Community vs Pro comparison ($39/dev/mo) and comparisons against incumbents
  (Semgrep, CodeQL, Snyk, Veracode) and open-source peers.

### Fixed
- Web3 findings from the contract auditor were mislabelled `web3:ton`; Solidity
  findings are now labelled `web3:evm` by rule prefix.

### Removed
- Fabricated vulnerability-disclosure writeup (fake payout ranges, fake
  "100% precision/recall" benchmark, non-existent CLI commands).
- Inflated claims ("60+ secret patterns" corrected to the real 40+/27 providers).

### Changed
- Premium gating aligned to the real Pro feature set; contact domain unified to
  `tythanai.io`.

## [1.0.x]

- Initial public Community Edition (superseded).
