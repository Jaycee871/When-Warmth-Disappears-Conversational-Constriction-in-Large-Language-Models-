from __future__ import annotations

import os
import time
from dataclasses import dataclass

import requests


@dataclass
class Check:
    name: str
    status: str  # PASS | WARN | FAIL
    detail: str


def request_check(
    name,
    method,
    url,
    *,
    headers=None,
    params=None,
    timeout=20,
    retries=3,
    auth_required=False,
    soft_non2xx=False,
):
    """Probe a third-party endpoint without turning transient outages into false CI failures.

    Rules:
    - 2xx -> PASS
    - 401/403 on authenticated endpoints -> FAIL (credential/auth problem)
    - transport errors, 429, and 5xx -> retry, then WARN
    - other non-2xx -> WARN for optional/public endpoints, otherwise FAIL
    """

    transient_http = {429, 500, 502, 503, 504}
    last_detail = None

    for attempt in range(1, retries + 1):
        try:
            r = requests.request(method, url, headers=headers, params=params, timeout=timeout)
        except requests.RequestException as exc:
            last_detail = exc.__class__.__name__
            if attempt < retries:
                time.sleep(min(2 ** (attempt - 1), 4))
                continue
            return Check(name, "WARN", f"{last_detail} after {retries} attempts")

        if 200 <= r.status_code < 300:
            return Check(name, "PASS", f"HTTP {r.status_code}")

        if auth_required and r.status_code in {401, 403}:
            return Check(name, "FAIL", f"HTTP {r.status_code} authentication rejected")

        if r.status_code in transient_http:
            last_detail = f"HTTP {r.status_code}"
            if attempt < retries:
                time.sleep(min(2 ** (attempt - 1), 4))
                continue
            return Check(name, "WARN", f"{last_detail} after {retries} attempts")

        return Check(name, "WARN" if soft_non2xx else "FAIL", f"HTTP {r.status_code}")

    return Check(name, "WARN", last_detail or "unknown connectivity result")


def secret(name: str):
    value = os.getenv(name)
    return value.strip() if value else None


def main() -> int:
    checks: list[Check] = []

    hf = secret("HF_TOKEN1")
    if hf:
        checks.append(
            request_check(
                "Hugging Face authentication",
                "GET",
                "https://huggingface.co/api/whoami-v2",
                headers={"Authorization": f"Bearer {hf}"},
                auth_required=True,
            )
        )
    else:
        checks.append(Check("Hugging Face authentication", "FAIL", "HF_TOKEN1 missing"))

    nvidia = secret("NVIDIA_API_TOKEN") or secret("NVIDIA_API_KEY")
    if nvidia:
        checks.append(
            request_check(
                "NVIDIA API",
                "GET",
                "https://integrate.api.nvidia.com/v1/models",
                headers={"Authorization": f"Bearer {nvidia}"},
                auth_required=True,
            )
        )
    else:
        checks.append(Check("NVIDIA API", "FAIL", "NVIDIA_API_TOKEN/NVIDIA_API_KEY missing"))

    meta = secret("META_API_KEY")
    if meta:
        checks.append(
            request_check(
                "Springer Nature Meta API",
                "GET",
                "https://api.springernature.com/meta/v2/json",
                params={"q": "keyword:artificial intelligence", "p": 1, "api_key": meta},
                soft_non2xx=True,
            )
        )
    else:
        checks.append(Check("Springer Nature Meta API", "WARN", "META_API_KEY missing"))

    oa = secret("OPEN_ACCESS_API")
    if oa:
        checks.append(
            request_check(
                "Springer Nature Open Access API",
                "GET",
                "https://api.springernature.com/openaccess/json",
                params={"q": "keyword:artificial intelligence", "p": 1, "api_key": oa},
                soft_non2xx=True,
            )
        )
    else:
        checks.append(Check("Springer Nature Open Access API", "WARN", "OPEN_ACCESS_API missing"))

    # Public OAI-PMH endpoint. Hosted CI IP ranges can receive 403 even when the
    # service is reachable interactively, so this is intentionally non-blocking.
    checks.append(
        request_check(
            "PhilPapers OAI-PMH",
            "GET",
            "https://api.philpapers.org/oai.pl",
            params={"verb": "Identify"},
            headers={
                "User-Agent": "When-Warmth-Disappears/0.1 academic-research",
                "Accept": "application/xml,text/xml;q=0.9,*/*;q=0.8",
            },
            soft_non2xx=True,
            retries=1,
        )
    )

    # KAGGLE_TOKEN is used by the GPU execution/publishing path. Presence is the
    # only safe bootstrap check here; we do not print or transmit the credential.
    kaggle = secret("KAGGLE_TOKEN")
    checks.append(
        Check(
            "Kaggle GPU credential present",
            "PASS" if kaggle else "FAIL",
            "configured" if kaggle else "KAGGLE_TOKEN missing",
        )
    )

    width = max(len(c.name) for c in checks)
    for c in checks:
        print(f"{c.status:4}  {c.name:<{width}}  {c.detail}")

    # Only definite credential/configuration failures block bootstrap CI.
    # Third-party transport failures and provider outages are WARN after retries.
    core_names = {
        "Hugging Face authentication",
        "NVIDIA API",
        "Kaggle GPU credential present",
    }
    core = [c for c in checks if c.name in core_names]
    return 1 if any(c.status == "FAIL" for c in core) else 0


if __name__ == "__main__":
    raise SystemExit(main())
