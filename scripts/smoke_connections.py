from __future__ import annotations

import os
from dataclasses import dataclass

import requests


@dataclass
class Check:
    name: str
    ok: bool
    detail: str


def request_check(name, method, url, *, headers=None, params=None, timeout=20):
    try:
        r = requests.request(method, url, headers=headers, params=params, timeout=timeout)
        ok = 200 <= r.status_code < 300
        return Check(name, ok, f"HTTP {r.status_code}")
    except Exception as exc:
        return Check(name, False, exc.__class__.__name__)


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
            )
        )
    else:
        checks.append(Check("Hugging Face authentication", False, "HF_TOKEN1 missing"))

    nvidia = secret("NVIDIA_API_TOKEN") or secret("NVIDIA_API_KEY")
    if nvidia:
        checks.append(
            request_check(
                "NVIDIA API",
                "GET",
                "https://integrate.api.nvidia.com/v1/models",
                headers={"Authorization": f"Bearer {nvidia}"},
            )
        )
    else:
        checks.append(Check("NVIDIA API", False, "NVIDIA_API_TOKEN/NVIDIA_API_KEY missing"))

    meta = secret("META_API_KEY")
    if meta:
        checks.append(
            request_check(
                "Springer Nature Meta API",
                "GET",
                "https://api.springernature.com/meta/v2/json",
                params={"q": "keyword:artificial intelligence", "p": 1, "api_key": meta},
            )
        )
    else:
        checks.append(Check("Springer Nature Meta API", False, "META_API_KEY missing"))

    oa = secret("OPEN_ACCESS_API")
    if oa:
        checks.append(
            request_check(
                "Springer Nature Open Access API",
                "GET",
                "https://api.springernature.com/openaccess/json",
                params={"q": "keyword:artificial intelligence", "p": 1, "api_key": oa},
            )
        )
    else:
        checks.append(Check("Springer Nature Open Access API", False, "OPEN_ACCESS_API missing"))

    # Public OAI-PMH endpoint. Some hosted CI IP ranges may receive 403 even
    # though the endpoint is reachable interactively, so this remains a soft check.
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
        )
    )

    # KAGGLE_TOKEN is primarily used by the GPU execution/publishing path. We avoid
    # pretending that an anonymous-readable endpoint validates account auth.
    kaggle = secret("KAGGLE_TOKEN")
    checks.append(Check("Kaggle GPU credential present", bool(kaggle), "configured" if kaggle else "KAGGLE_TOKEN missing"))

    width = max(len(c.name) for c in checks)
    for c in checks:
        status = "PASS" if c.ok else "FAIL"
        print(f"{status:4}  {c.name:<{width}}  {c.detail}")

    # Only model-execution credentials gate the bootstrap CI. Literature APIs are
    # reported but do not block the experiment when a provider is temporarily unavailable.
    core = [c for c in checks if c.name in {"Hugging Face authentication", "NVIDIA API", "Kaggle GPU credential present"}]
    return 0 if all(c.ok for c in core) else 1


if __name__ == "__main__":
    raise SystemExit(main())
