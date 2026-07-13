# Roadmap

This is a directional roadmap for **TythanAI Community Edition**, not a commitment.
Priorities may shift based on user feedback.

## Now (Community Edition)

- Built-in **offline SAST engine** for **10 languages** (Python, JS/TS, Go, Java, PHP, Ruby, C#, Kotlin, Rust, C/C++): weak crypto, insecure deserialization, TLS-off, eval/exec, command injection, dynamic SQL incl. cross-function, insecure randomness, XXE, path traversal, dangerous C functions — no external tools or network
- Injection coverage incl. SQL, command, XPath (CWE-643) and LDAP (CWE-90)
- Optional external engines when installed: Slither (Solidity), cargo-audit (Rust)
- CI baseline (`--baseline`) to gate on new findings only; Docker image; SARIF with CWE tags; GitHub Pages site
- Optional Semgrep integration for extra language/rule breadth
- SCA via OSV.dev + EPSS enrichment, with an offline fallback
- Secrets detection in source
- IaC scanner (Terraform, CloudFormation, Kubernetes)
- Web3 auditing — core checks for TON FunC/Tolk, Solidity, Solana/Anchor, CosmWasm
- GitHub Actions integration
- SARIF 2.1.0, JSON and HTML reports
- **Anti-evasion detection** — decodes base64/hex/split-string/char-code obfuscation
  before matching (CWE-506)
- **AI security assistant** (`explain` / `ask` / `chat`) — offline by default
  (CWE knowledge base), optional local Ollama or opt-in Claude for deeper
  reasoning
- **MCP server** for Claude Code / Cursor / VS Code — `scan_path`,
  `explain_finding`, `suggest_fix`, `list_rules` as agent tools
- **Authorization-gated, non-destructive active validation** (`tythanai
  validate`) — exploitability assessment for owners with written/video
  permission on file; destructive actions refused unconditionally, all
  requests audit-logged

## Next (within 3 months)

- Expanded built-in SAST rules and Web3 rule coverage
- Grow the reproducible benchmark corpus (`benchmarks/`) toward Juliet/OWASP breadth
- More example CI integrations
- Streaming responses and multi-turn memory for `tythanai chat`
- More MCP tools (`propose_baseline_update`, `explain_diff`)

## Pro ($39/dev/mo) & Enterprise

Advanced capabilities are available in the commercial editions (for teams and audit firms):

- Full rule library and deep Web3 analysis (symbolic execution, formal checks)
- Inter-procedural CPG taint analysis (Go / Java / Rust)
- Whole-repo AI triage & ranking, AutoPR auto-generated fix pull requests
  (Community ships the AI assistant itself — explain/ask/chat/suggest-fix,
  offline by default; Pro adds repo-wide context and opens the PR for you)
- Dependency reachability analysis, managed CI/CD gates on every PR
- Sandboxed DAST PoC execution against your own authorized environment
  (Community ships the authorization gate and non-destructive assessment;
  Pro adds actual sandboxed exploitation, still authorization-gated)
- SBOM & compliance reports (SPDX / CycloneDX)
- SaaS dashboard, webhooks, Slack & Jira integration
- Priority support & SLA

See the comparison table in the [README](README.md#community-vs-pro).

## Not planned

- Offensive tooling of any kind — no weaponized exploits, no DoS/DDoS, no
  destructive payloads, ever, with or without authorization
- Active testing against systems without a recorded, in-scope, unexpired
  authorization
- Features that require persistent code upload without explicit user opt-in
