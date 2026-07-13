<!-- Banner -->
<p align="center">
  <a href="https://tythanai.io">
    <img src="./.github/assets/banner.svg" alt="TythanAI Community Edition — enterprise-grade code security, now open" width="100%">
  </a>
</p>

<h1 align="center">TythanAI — Community Edition</h1>

<p align="center">
  <strong>An open, Web3-native security scanner.</strong><br>
  SAST · SCA · Secrets · IaC — plus first-class auditing for <strong>TON, Solidity/EVM, Solana &amp; CosmWasm</strong>.<br>
  One CLI. No account. No telemetry. Nothing leaves your machine.
</p>

<p align="center">
  <a href="LICENSE"><img alt="License: BSL 1.1" src="https://img.shields.io/badge/license-BSL%201.1-0b0b0c.svg"></a>
  <a href="https://www.python.org/"><img alt="Python 3.10+" src="https://img.shields.io/badge/python-3.10%2B-3776ab.svg"></a>
  <img alt="Engines" src="https://img.shields.io/badge/engines-SAST%20%C2%B7%20SCA%20%C2%B7%20Secrets%20%C2%B7%20IaC%20%C2%B7%20Web3-41d18a.svg">
  <img alt="Privacy" src="https://img.shields.io/badge/telemetry-none-2ea043.svg">
  <a href="CONTRIBUTING.md"><img alt="PRs welcome" src="https://img.shields.io/badge/PRs-welcome-8250df.svg"></a>
</p>

<p align="center">
  <a href="#quick-start">Quick start</a> ·
  <a href="#whats-in-the-community-edition">What's included</a> ·
  <a href="#community-vs-pro">Community vs Pro</a> ·
  <a href="#how-it-compares">How it compares</a> ·
  <a href="#transparency--benchmarks">Transparency</a>
</p>

---

## Quick start

```bash
# From PyPI
pip install tythanai-community
tythanai scan ./your-project
```

```bash
# …or from source (always current)
git clone https://github.com/TythanAI/TythanAIOpen.git
cd TythanAIOpen
pip install -e .
tythanai scan ./your-project
```

That's it. No sign-up, no API key, no data leaves your machine. The scanner
exits non-zero when it finds something, so it drops straight into CI.

---

## See it in action

Point it at a folder and it streams findings from every engine — secrets,
dependencies, IaC, and native Web3 — with a file:line and the engine that
caught it:

<p align="center">
  <img src="./.github/assets/scan-demo.svg" alt="tythanai scan streaming real findings" width="90%">
</p>

```text
  FINDINGS

    1  CRITICAL  AWS access key exposed in source code
          app.py:2                       SEC-AWS_ACCESS_KEY   [secrets]

    2  CRITICAL  Potential reentrancy: state written after external call
          Vault.sol:5                    SC-SOL-001           [web3:evm]

    3  HIGH      Unchecked low-level .call() return value — silent failure
          Vault.sol:5                    SOL005               [solidity]

    4  HIGH      No sender-address validation (gas-drain risk)
          main.fc:1                      SC-TON-001           [web3:ton]

    5  HIGH      S3 bucket missing server-side encryption
          main.tf                        IAC-TF-001           [iac]

    6  MEDIUM    requests 2.19.0 — sensitive headers leaked on redirect
          requirements.txt               CVE-2023-32681       [sca]

  SCAN SUMMARY
  Risk      : CRITICAL (100/100)
  Findings  : 12   (CRITICAL 3 · HIGH 6 · MEDIUM 3)
```

---

## What's in the Community Edition

Everything below runs **locally, free, with no account**:

| Engine | What it does |
|--------|--------------|
| 🪙 **Web3 audit** | Native static checks for **TON (FunC/Tolk)**, **Solidity/EVM**, **Solana/Anchor** and **CosmWasm** — reentrancy, unchecked low-level calls, missing sender validation, gas-drain, weak randomness, `tx.origin` auth, unprotected `selfdestruct`, hardcoded keys, and more. |
| 🔍 **SAST** | A **built-in, offline rule engine** for **Python, JS/TS, Go and Java** flags weak crypto, unsafe deserialization, disabled TLS, `eval`/`exec`, command injection, dynamic SQL, insecure randomness, XXE and user-controlled file paths — no external tools, no network. Add [Semgrep](https://semgrep.dev) for extra breadth (Rust, PHP, Ruby, C/C++…), normalised into the same finding format. |
| 📦 **SCA** | Dependency CVEs from **[OSV.dev](https://osv.dev)** with EPSS exploit-probability ranking, and an offline known-CVE fallback so you still get results with no network. |
| 🔑 **Secrets** | **40+ secret patterns across 27 providers** (AWS, GCP, GitHub, Stripe, Slack, database URIs, private keys, crypto wallets…) plus entropy analysis. |
| ☁️ **IaC** | Terraform, Kubernetes and CloudFormation misconfiguration checks (public buckets, open security groups, missing encryption…). |
| 📄 **Reports** | **SARIF 2.1.0** (for GitHub Code Scanning), plus **JSON** and a self-contained **HTML** report. |
| 🔒 **Private by design** | Fully local. No account, no phone-home, no telemetry. |

> The Community Edition is a fast, practical scanner that catches the most common,
> highest-impact issues. Deeper analysis — inter-procedural taint, symbolic/formal
> Web3 checks, AI triage, and auto-fix PRs — lives in **Pro**. See the table below.

---

## Usage

```bash
# Scan everything
tythanai scan ./myproject

# Run only the engines you want (skip the rest)
tythanai scan ./myproject --no-sast --no-sca      # e.g. secrets + IaC + Web3 only

# Machine-readable output
tythanai scan ./myproject --sarif results.sarif   # upload to GitHub Code Scanning
tythanai scan ./myproject --json  report.json
tythanai scan ./myproject --html  report.html

# Quiet mode — findings + summary only, no banner
tythanai scan ./myproject --quiet
```

**Exit codes** map to risk, so CI fails on real problems:
`0` clean · `1` low · `2` medium · `3` high/critical.

### GitHub Actions

```yaml
name: Security Scan
on: [push, pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install tythanai-community
      - run: tythanai scan . --sarif results.sarif
      - uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: results.sarif
```

---

## Community vs Pro

The Community Edition is genuinely useful on its own. Teams shipping production
smart contracts — and audit firms — upgrade to **Pro** for depth, automation and
support.

<table>
<tr>
  <th align="left">Capability</th>
  <th align="center">Community<br><sub>free · BSL 1.1</sub></th>
  <th align="center">Pro<br><sub><strong>$39</strong> / dev / mo</sub></th>
</tr>
<tr><td>Local CLI — SAST · SCA · Secrets · IaC · Web3</td><td align="center">✅</td><td align="center">✅</td></tr>
<tr><td>Repositories</td><td align="center">Unlimited (local)</td><td align="center">Unlimited (managed)</td></tr>
<tr><td>Web3 rule packs (TON · Solidity · Solana · CosmWasm)</td><td align="center">Core checks</td><td align="center">Full set + deep analysis</td></tr>
<tr><td>Reports</td><td align="center">SARIF · JSON · HTML</td><td align="center">+ SBOM · compliance</td></tr>
<tr><td>GitHub Actions (SARIF upload)</td><td align="center">✅ self-hosted</td><td align="center">✅</td></tr>
<tr><td>CI/CD gates on every pull request</td><td align="center">—</td><td align="center">✅</td></tr>
<tr><td>AI triage &amp; fix suggestions</td><td align="center">—</td><td align="center">✅</td></tr>
<tr><td>Auto-fix pull requests (AutoPR)</td><td align="center">—</td><td align="center">✅</td></tr>
<tr><td>Dependency reachability analysis</td><td align="center">—</td><td align="center">✅</td></tr>
<tr><td>Inter-procedural CPG taint (Go · Java · Rust)</td><td align="center">—</td><td align="center">✅</td></tr>
<tr><td>DAST — active web scanning</td><td align="center">—</td><td align="center">✅</td></tr>
<tr><td>Slack &amp; Jira integration</td><td align="center">—</td><td align="center">✅</td></tr>
<tr><td>SaaS dashboard, webhooks, team roles</td><td align="center">—</td><td align="center">✅</td></tr>
<tr><td>Support</td><td align="center">Community (issues)</td><td align="center">Priority + SLA</td></tr>
</table>

<p align="center"><strong>Pro is $39 / developer / month.</strong> Start a free trial or book a demo at <a href="https://tythanai.io/pricing">tythanai.io/pricing</a>.</p>

---

## How it compares

### Against open-source scanners

Most teams reach for a different tool per language and per concern. TythanAI CE
is one scanner that covers all of them — and it's the only free tool that audits
TON, Solana and CosmWasm alongside Solidity.

| | **TythanAI CE** | Semgrep OSS | Slither | Gitleaks | Trivy |
|---|:--:|:--:|:--:|:--:|:--:|
| SAST | ✅ | ✅ | — | — | — |
| SCA (OSV.dev + EPSS) | ✅ | — | — | — | ✅ |
| Secrets | ✅ | ◐ | — | ✅ | ✅ |
| IaC | ✅ | ◐ | — | — | ✅ |
| Solidity / EVM | ✅ | — | ✅ | — | — |
| **TON (FunC / Tolk)** | ✅ | — | — | — | — |
| **Solana / Anchor** | ✅ | — | — | — | — |
| **CosmWasm** | ✅ | — | — | — | — |
| SARIF output | ✅ | ✅ | ◐ | ✅ | ✅ |
| One tool, all of the above | ✅ | — | — | — | ◐ |
| No account · no telemetry | ✅ | ✅ | ✅ | ✅ | ✅ |

<sub>✅ built-in · ◐ partial / add-on · — not covered</sub>

### The full platform, against the incumbents

The same engine that powers the Community Edition scales into the commercial
platform. Here's how TythanAI stands against the tools it's most often compared
to — with the rows that ship **free in Community** marked.

| Capability | **TythanAI** | Semgrep | CodeQL | Snyk | Veracode |
|------------|:--:|:--:|:--:|:--:|:--:|
| Multi-chain Web3 audit (TON/Solana/CosmWasm/EVM) | ✅ <sub>core free</sub> | — | — | — | — |
| Inter-procedural taint (CPG) | ✅ <sub>Pro</sub> | ◐ | ✅ | — | ◐ |
| SCA — OSV.dev + EPSS | ✅ <sub>free</sub> | — | — | ✅ | ◐ |
| Secrets detection | ✅ <sub>free</sub> | ◐ | — | ✅ | — |
| IaC misconfiguration | ✅ <sub>free</sub> | ◐ | — | ✅ | ✅ |
| AI triage &amp; fix | ✅ <sub>Pro</sub> | — | — | ◐ | — |
| Autonomous fix PRs | ✅ <sub>Pro</sub> | — | — | ◐ | — |
| DAST correlation | ✅ <sub>Pro</sub> | — | — | — | ✅ |
| SARIF / GitHub Code Scanning | ✅ <sub>free</sub> | ◐ | ✅ | ◐ | ◐ |
| Self-hosted, no account | ✅ <sub>free</sub> | ✅ | ✅ | — | — |
| No telemetry (fully local) | ✅ <sub>free</sub> | ✅ | ◐ | — | — |

<sub>Comparison reflects each tool's core/default offering; every vendor has add-ons. Trademarks belong to their respective owners and are used for identification only.</sub>

---

## Transparency &amp; benchmarks

We'd rather show you an honest coverage map than a marketing number. The
built-in SAST engine ships with a labelled corpus of vulnerable/secure pairs
([`benchmarks/community_corpus.py`](benchmarks/community_corpus.py)) so the
numbers below are **reproducible from source**:

```bash
python -m benchmarks.measure
```

| Scope | Recall (TPR) | False positives |
|-------|:---:|:---:|
| **Modelled weakness classes** — weak crypto, insecure deserialization, TLS-off, `eval`/`exec`, command injection, dynamic SQL, XSS/SSTI, insecure randomness, XXE, path traversal (**10 CWE classes** across Python · JS/TS · Go · Java) | **100%** (38/38) | **0%** |
| **Overall, incl. out-of-model taint classes** | **92.7%** (38/41) | **0%** |

Two things we do on purpose:

- **Zero false positives across the whole corpus** — a finding you act on, not
  noise you triage.
- **We name our blind spots.** SSRF, SQL tainted across a function boundary and
  open redirect need inter-procedural data-flow (taint) tracking — that's the
  **Pro** CPG engine. The rule engine honestly scores 0% on those rather than
  guessing.

> The corpus is maintained in-repo alongside the rules — authoring is disclosed,
> not hidden. The Community Edition also carries a full unit-test suite:
> `pytest tests/ -v` (**105 tests**).

---

## Requirements

- **Python 3.10+** — the built-in SAST engine, secrets, IaC and Web3 auditors
  run with **no other dependencies and no network**.
- Optional: [Semgrep](https://semgrep.dev) (installed with the package) widens
  SAST language coverage; [OSV.dev](https://osv.dev) is queried for live CVEs
  when online, with a bundled offline CVE set as fallback.

---

## Contributing

New rules, chain auditors and false-positive fixes are very welcome — see
[CONTRIBUTING.md](CONTRIBUTING.md). Found a security bug? See [SECURITY.md](SECURITY.md).

The Web3 auditors live in [`blockchain/`](blockchain) and
[`scanners/`](scanners); the scan pipeline and feature gates are in
[`community/`](community).

If TythanAI saved you from shipping a vulnerability, a ⭐ helps other people find it.

---

## License

[Business Source License 1.1](LICENSE) — source-available; free for
non-production, evaluation and personal use, and for organisations with three or
fewer developers. Converts to **Apache 2.0 on 2029-06-01**. For commercial terms,
see [tythanai.io/pricing](https://tythanai.io/pricing).

<p align="center"><sub>© 2026 TythanAI Labs · <a href="https://tythanai.io">tythanai.io</a></sub></p>
