# Changelog

All notable changes to **TythanAI Community Edition** are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/); versions
follow [Semantic Versioning](https://semver.org/).

## [1.7.0]

### Added
- **AI security assistant** (`tythanai explain|ask|chat`) — explains findings,
  answers free-form questions, and holds a conversation, always grounded in an
  offline CWE knowledge base so answers are accurate with zero model involved.
  Optional local (Ollama) or cloud (Claude, opt-in) providers reason further on
  top of that grounding; offline stays the default (`community/ai/`).
- **MCP server** (`community/mcp_server.py`, `python -m community.mcp_server`)
  exposing `scan_path`, `explain_finding`, `suggest_fix` and `list_rules` as
  tools, so Claude Code, Cursor and VS Code can call TythanAI directly while
  editing. `.mcp.json` registration example in the README.
- **Anti-evasion scanner** (`scanners/evasion_scanner.py`, CWE-506) — decodes
  base64/hex/split-string-obfuscated payloads before matching and flags only
  when the *decoded* content is genuinely dangerous, closing a class of
  pattern-matching bypasses without adding false positives.
- **Authorization gate + non-destructive active validation**
  (`community/authz.py`, `community/active_validation.py`, `tythanai validate`)
  — turns a finding into a real exploitability assessment (static reachability
  + a written, non-destructive reproduction note), but only for an owner with
  a recorded, unexpired, in-scope authorization referencing signed written
  permission or a video statement. Destructive/offensive actions (DoS,
  brute-force, data wipes, weaponization…) are refused unconditionally in
  code, regardless of authorization. Every request — granted or refused — is
  appended to a tamper-evident audit log.

### Changed
- `ai` extra now installs `anthropic` (replacing a stale, unused `openai`
  pin); new `mcp` extra installs the MCP runtime. Both remain fully optional —
  the CLI and the offline AI assistant need neither.
- Test suite grown to **183 tests**; all green, ruff clean.

## [1.6.0]

### Added
- **XPath injection** (CWE-643) detection for Python, Java, PHP and C#, and
  **LDAP injection** (CWE-90) for Python (escape-aware — flags unescaped filters).
- Optional external engines, used only when installed: **Slither** (deep
  Solidity analysis, augments Web3) and **cargo-audit** (RustSec advisories,
  augments SCA). Absent tools are skipped silently.
- **Landing page** for GitHub Pages (`docs/index.html`) matching the product UI.

### Changed
- Corpus grown to 71 pairs across 10 languages and 13 CWE classes. Modelled
  recall 100% (68/68); overall **95.8%** (68/71); zero false positives.
- Engine now ships **58 built-in rules**.

## [1.5.0]

### Added
- Built-in SAST engine extended to **Kotlin, Rust and C/C++** (now 10 languages).
  New class: dangerous C functions — `strcpy`/`strcat`/`sprintf`/`gets` (CWE-676).
- **`--baseline` / `--update-baseline`** CLI flags: record accepted findings once,
  then fail CI only on genuinely *new* ones. Fingerprints are line-independent.
- **Docker image** (`Dockerfile`) — `docker run --rm -v "$PWD:/src" tythanai/community scan /src`.
- **CI workflow** (`.github/workflows/ci.yml`): ruff + tests + benchmark +
  rules-doc sync check on 3.10 and 3.12.
- Auto-generated rule reference **`docs/RULES.md`** (`python -m benchmarks.gen_rules_doc`),
  kept in sync by a test.

### Changed
- Benchmark corpus grown to 66 pairs across 10 languages and 11 CWE classes.
  Modelled recall 100% (63/63); overall **95.5%** (63/66); zero false positives.
- ruff config: keep correctness checks, silence stylistic rules that clash with
  the codebase's house style.

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
