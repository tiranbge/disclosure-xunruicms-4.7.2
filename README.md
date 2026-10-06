# XunRuiCMS 4.7.2 — vulnerability disclosure reports

Vendor: **dayrui** · Product: **XunRuiCMS** (XunRuiPHP) · Version: **4.7.2**
Tested on: PHP 7.4.33 · Apache 2.4 (Debian) · MySQL 8.0.46 · also verified with SQLite3 / MySQLi drivers

| # | Report | Type | CWE | Privilege |
|---|---|---|---|---|
| 1 | Anonymous-trigger RCE via site name + notification-template compilation | Code Injection | CWE-94 / CWE-1336 | write: back-end session / **trigger: anonymous** |
| 2 | Anonymous-reachable RCE via mobile-site directory name (code injection into the generated entry file) | Code Injection | CWE-94 | write: back-end session / **execution: anonymous** |
| 3 | Unauthenticated blind SQL injection (credential theft) | SQL Injection | CWE-89 | **none** |

## Layout

- `reports/` — full reports (EN + 中文): root cause with file/line, payload constraints, request samples, verified output, PoC listing, impact, mitigation, references
- `images/` — screenshots referenced by the reports, stored inside the repository so they render without depending on an external host
- `poc/1.py` — report 1 PoC; the write phase needs a back-end session cookie and the random entry file name (e.g. `admin82b8542a912e.php`), the execution trigger it issues is anonymous
- `poc/2.py` — report 2 PoC; same write-phase requirements, the dropped entry file is then anonymously reachable
- `poc/3.py` — report 3 PoC, unauthenticated; auto-detects the DB driver and picks a working boolean oracle (length / UNION-error / CASE-error)

## Usage

```
python poc/3.py http://<target>
python poc/1.py http://<target> "<cookie>" <entry>.php
python poc/2.py http://<target> "<cookie>" <entry>.php
```

`poc/3.py` is read-only. `poc/1.py` and `poc/2.py` change the site name / the mobile-site configuration and **restore the original values at the end**; the dropped web shell is intentionally left in place. Run them only against systems you are authorized to test.

## Notes

- Every `http://<target>` placeholder replaces the private test lab used during the research.
- Reproduction was performed on an authorized self-hosted lab environment.
- These reports are published for vulnerability disclosure and remediation purposes. If the vendor has not fixed the issues yet, coordinate with the vendor first.
- Report text: CC BY 4.0 · PoC scripts: MIT
