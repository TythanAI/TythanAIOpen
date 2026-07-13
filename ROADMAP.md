# Roadmap

This is a directional roadmap for **TythanAI Community Edition**, not a commitment.
Priorities may shift based on user feedback.

## Now (Community Edition)

- Built-in **offline SAST engine** for **Python, JS/TS, Go, Java, PHP, Ruby and C#** (weak crypto, insecure deserialization, TLS-off, eval/exec, command injection, dynamic SQL incl. cross-function, insecure randomness, XXE, path traversal) — no external tools or network
- Optional Semgrep integration for extra language/rule breadth
- SCA via OSV.dev + EPSS enrichment, with an offline fallback
- Secrets detection in source
- IaC scanner (Terraform, CloudFormation, Kubernetes)
- Web3 auditing — core checks for TON FunC/Tolk, Solidity, Solana/Anchor, CosmWasm
- GitHub Actions integration
- SARIF 2.1.0, JSON and HTML reports

## Next (within 3 months)

- Expanded built-in SAST rules and Web3 rule coverage
- Grow the reproducible benchmark corpus (`benchmarks/`) toward Juliet/OWASP breadth
- Docker image published
- More example CI integrations

## Pro ($39/dev/mo) & Enterprise

Advanced capabilities are available in the commercial editions (for teams and audit firms):

- Full rule library and deep Web3 analysis (symbolic execution, formal checks)
- Inter-procedural CPG taint analysis (Go / Java / Rust)
- AI triage & fix suggestions, AutoPR auto-generated fix pull requests
- Dependency reachability analysis, managed CI/CD gates on every PR
- DAST, SBOM & compliance reports (SPDX / CycloneDX)
- SaaS dashboard, webhooks, Slack & Jira integration
- Priority support & SLA

See the comparison table in the [README](README.md#community-vs-pro).

## Not planned

- Offensive tooling of any kind
- Features that require persistent code upload without explicit user opt-in
