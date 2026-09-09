from __future__ import annotations

import os
import requests


def main() -> None:
    token = os.getenv("NVIDIA_API_KEY") or os.getenv("NVIDIA_API_TOKEN")
    if not token:
        raise SystemExit("NVIDIA credential missing")

    r = requests.get(
        "https://integrate.api.nvidia.com/v1/models",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    r.raise_for_status()
    payload = r.json()
    models = sorted(item.get("id", "") for item in payload.get("data", []) if item.get("id"))

    print(f"MODEL_COUNT={len(models)}")
    for model_id in models:
        print(model_id)


if __name__ == "__main__":
    main()
