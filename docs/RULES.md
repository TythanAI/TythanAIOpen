# Built-in SAST rules

> Auto-generated from `scanners/code_weakness_scanner.py` by `python -m benchmarks.gen_rules_doc`. Do not edit by hand.

The offline engine ships **53 rules** across **10 languages** and **11 CWE classes** (CWE-22, CWE-295, CWE-327, CWE-330, CWE-502, CWE-611, CWE-676, CWE-78, CWE-79, CWE-89, CWE-95). Every rule runs with no external tools and no network, and each is exercised by the benchmark corpus (`python -m benchmarks.measure`).

## Python

| Rule | CWE | Severity | Detects |
|------|-----|----------|---------|
| `TYT-P001` | CWE-327 | MEDIUM | Weak hash algorithm (MD5/SHA-1) |
| `TYT-P002` | CWE-327 | HIGH | Broken/weak cipher (DES/RC4/RC2/Blowfish) |
| `TYT-P003` | CWE-327 | MEDIUM | Insecure ECB cipher mode |
| `TYT-P004` | CWE-295 | HIGH | TLS certificate verification disabled |
| `TYT-P005` | CWE-502 | HIGH | Unsafe deserialization (pickle/marshal) |
| `TYT-P006` | CWE-502 | HIGH | Unsafe YAML load (arbitrary object construction) |
| `TYT-P007` | CWE-95 | HIGH | Code injection via eval()/exec() |
| `TYT-P008` | CWE-78 | HIGH | OS command execution (os.system/os.popen) |
| `TYT-P009` | CWE-78 | HIGH | subprocess with shell=True |
| `TYT-P010` | CWE-89 | HIGH | SQL built from dynamic string (injection) |
| `TYT-P011` | CWE-79 | MEDIUM | Template/markup rendered from dynamic input (XSS/SSTI) |
| `TYT-P012` | CWE-330 | MEDIUM | Insecure randomness for a security value |
| `TYT-P013` | CWE-611 | MEDIUM | XML parsed without external-entity protection (XXE) |
| `TYT-P014` | CWE-22 | HIGH | User-controlled path passed to open() (traversal) |
| `TYT-P015` | CWE-89 | HIGH | Dynamic SQL passed to a query helper (injection) |

## JavaScript / TypeScript

| Rule | CWE | Severity | Detects |
|------|-----|----------|---------|
| `TYT-J001` | CWE-95 | HIGH | Code injection via eval() |
| `TYT-J002` | CWE-78 | HIGH | Command execution with interpolated input |
| `TYT-J003` | CWE-79 | MEDIUM | innerHTML assigned dynamic content (DOM XSS) |
| `TYT-J004` | CWE-327 | MEDIUM | Weak hash algorithm (MD5/SHA-1) |
| `TYT-J005` | CWE-295 | HIGH | TLS certificate validation disabled |

## Go

| Rule | CWE | Severity | Detects |
|------|-----|----------|---------|
| `TYT-G001` | CWE-327 | MEDIUM | Weak hash/cipher (MD5/SHA-1/DES/RC4) |
| `TYT-G002` | CWE-295 | HIGH | TLS verification disabled (InsecureSkipVerify) |
| `TYT-G003` | CWE-78 | HIGH | Command execution with concatenated input |
| `TYT-G004` | CWE-89 | HIGH | SQL built from dynamic string (injection) |

## Java

| Rule | CWE | Severity | Detects |
|------|-----|----------|---------|
| `TYT-A001` | CWE-327 | MEDIUM | Weak hash/cipher (MD5/SHA-1/DES/ECB) |
| `TYT-A002` | CWE-78 | HIGH | Command execution with concatenated input |
| `TYT-A003` | CWE-89 | HIGH | SQL built from string concatenation (injection) |
| `TYT-A004` | CWE-502 | HIGH | Unsafe Java deserialization (ObjectInputStream) |
| `TYT-A005` | CWE-330 | MEDIUM | Insecure randomness for a security value (use SecureRandom) |

## PHP

| Rule | CWE | Severity | Detects |
|------|-----|----------|---------|
| `TYT-H001` | CWE-327 | MEDIUM | Weak hash (md5/sha1) |
| `TYT-H002` | CWE-78 | HIGH | Command execution with variable input |
| `TYT-H003` | CWE-89 | HIGH | SQL built from interpolated/concatenated string |
| `TYT-H004` | CWE-502 | HIGH | Unsafe deserialization (unserialize) |
| `TYT-H005` | CWE-95 | HIGH | Code injection via eval() |

## Ruby

| Rule | CWE | Severity | Detects |
|------|-----|----------|---------|
| `TYT-R001` | CWE-327 | MEDIUM | Weak hash (Digest::MD5/SHA1) |
| `TYT-R002` | CWE-78 | HIGH | Command execution with interpolation |
| `TYT-R003` | CWE-89 | HIGH | SQL built from string interpolation |
| `TYT-R004` | CWE-502 | HIGH | Unsafe deserialization (Marshal/YAML.load) |
| `TYT-R005` | CWE-95 | HIGH | Code injection via eval() |

## C#

| Rule | CWE | Severity | Detects |
|------|-----|----------|---------|
| `TYT-C001` | CWE-327 | MEDIUM | Weak hash/cipher (MD5/SHA-1/DES) |
| `TYT-C002` | CWE-78 | HIGH | Command execution with concatenated input |
| `TYT-C003` | CWE-89 | HIGH | SQL built from concatenation/interpolation |
| `TYT-C004` | CWE-502 | HIGH | Unsafe deserialization (BinaryFormatter) |

## Kotlin

| Rule | CWE | Severity | Detects |
|------|-----|----------|---------|
| `TYT-K001` | CWE-327 | MEDIUM | Weak hash/cipher (MD5/SHA-1/DES/ECB) |
| `TYT-K002` | CWE-78 | HIGH | Command execution with concatenated/interpolated input |
| `TYT-K003` | CWE-89 | HIGH | SQL built from concatenation/interpolation |
| `TYT-K004` | CWE-502 | HIGH | Unsafe deserialization (ObjectInputStream) |

## Rust

| Rule | CWE | Severity | Detects |
|------|-----|----------|---------|
| `TYT-U001` | CWE-327 | MEDIUM | Weak hash (MD5/SHA-1) |
| `TYT-U002` | CWE-78 | HIGH | Command built with format!() |
| `TYT-U003` | CWE-89 | HIGH | SQL built with format!() (injection) |

## C / C++

| Rule | CWE | Severity | Detects |
|------|-----|----------|---------|
| `TYT-X001` | CWE-676 | HIGH | Dangerous unbounded function (strcpy/strcat/sprintf/gets) |
| `TYT-X002` | CWE-78 | HIGH | Command execution via system() with dynamic input |
| `TYT-X003` | CWE-327 | MEDIUM | Weak hash primitive (MD5/SHA-1) |
