## 2023-10-24 - Information Leakage in API Error Response
**Vulnerability:** The `/predict` endpoint in `main.py` was returning internal Python stack trace or exception string directly to the client via a 500 HTTPException.
**Learning:** Returning `str(e)` directly inside FastAPI exceptions inadvertently exposed potentially sensitive information regarding server configuration and internal application structure when requests fail.
**Prevention:** Instead of directly returning `str(e)` to the client, applications should securely log the error trace server-side and respond to the client with generic error messages (e.g. "Internal server error") to limit information exposure.
## 2024-05-15 - Server-Side Request Forgery (SSRF) / Local File Inclusion in URL Loader
**Vulnerability:** The `load_recipients` function in `job-outreach/send_applications.py` accepted an arbitrary URL via command-line or environment variable and fetched it using `urllib.request.urlopen()`. Because `urllib` natively supports `file://` schemes, this could be exploited to read sensitive local files (like `/etc/passwd`).
**Learning:** `urllib.request.urlopen` is a highly powerful and risky function because it supports various protocol schemas automatically without filtering, unlike simpler HTTP-only request libraries. Unvalidated user input (like a CLI argument or environment variable that could be poisoned) passed to this function poses a severe SSRF and LFI risk.
**Prevention:** Always validate and restrict the protocol schemas (e.g., to only `http://` and `https://`) before passing unverified URLs to `urllib.request.urlopen`. Alternatively, prefer safer libraries like `requests` for fetching remote data.

## 2025-02-18 - [CRITICAL] Fix DoS Risk in FastAPI ML Endpoint
**Vulnerability:** The `/predict` endpoint in FastAPI accepted an unbounded list of floats (`List[float]`) which were immediately allocated into a NumPy array. An attacker could send a massive payload, leading to rapid resource exhaustion, memory out-of-bounds, and a Denial of Service.
**Learning:** Pydantic models in FastAPI endpoints do not enforce default length limits on array/list types. It is a common oversight to leave these unbounded.
**Prevention:** Always use `pydantic.Field` with a `max_length` constraint for array or list inputs in API endpoints to bound resource allocation.

## 2026-08-16 - Replace Weak Hash Function (SHA-1)
**Vulnerability:** The automation scripts (`run.py` and `run_repo.py`) used `hashlib.sha1()` to generate deduplication keys, which triggered Bandit High-Severity issue B324. SHA-1 is cryptographically weak and prone to collision attacks.
**Learning:** Even for non-cryptographic deduplication, it is best practice to use stronger hashes like SHA-256 to avoid security scanning warnings and reduce the risk of accidental collisions.
**Prevention:** Upgraded `hashlib.sha1` to `hashlib.sha256` in all relevant files.

## 2026-08-27 - [MEDIUM] Missing Timeout in Network Requests
**Vulnerability:** The `test.py` script was calling `requests.get` and `requests.post` without specifying a `timeout` argument.
**Learning:** If the target server becomes unresponsive, network operations without timeouts can hang indefinitely. This leads to unbounded resource consumption (like lingering connections and stalled threads) and is flagged by security scanners (e.g., Bandit B113).
**Prevention:** Always specify a `timeout` parameter (e.g., `timeout=10`) when using the `requests` library or performing any external network operations.
