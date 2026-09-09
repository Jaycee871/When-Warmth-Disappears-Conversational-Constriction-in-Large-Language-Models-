from __future__ import annotations

import os
import time

import requests

import run_panel_v02 as base

TRANSIENT_HTTP = {429, 500, 502, 503, 504}
_ORIGINAL_CALL_CHAT = base.call_chat


def resilient_call_chat(token: str, model: str, messages: list[dict], generation: dict):
    """Retry transient NVIDIA endpoint failures without changing the prompt state."""
    attempts = int(os.getenv("NVIDIA_RETRY_ATTEMPTS", "7"))
    base_delay = float(os.getenv("NVIDIA_RETRY_BASE_DELAY", "2"))

    for attempt in range(1, attempts + 1):
        try:
            return _ORIGINAL_CALL_CHAT(token, model, messages, generation)
        except requests.HTTPError as exc:
            response = exc.response
            status = response.status_code if response is not None else None
            if status not in TRANSIENT_HTTP or attempt >= attempts:
                raise

            retry_after = None
            if response is not None:
                raw = response.headers.get("Retry-After")
                if raw:
                    try:
                        retry_after = float(raw)
                    except ValueError:
                        retry_after = None

            delay = retry_after if retry_after is not None else min(30.0, base_delay * (2 ** (attempt - 1)))
            print(
                f"RETRY model={model} status={status} attempt={attempt}/{attempts} "
                f"sleep={delay:.1f}s",
                flush=True,
            )
            time.sleep(delay)
        except (requests.ConnectionError, requests.Timeout) as exc:
            if attempt >= attempts:
                raise
            delay = min(30.0, base_delay * (2 ** (attempt - 1)))
            print(
                f"RETRY model={model} error={type(exc).__name__} attempt={attempt}/{attempts} "
                f"sleep={delay:.1f}s",
                flush=True,
            )
            time.sleep(delay)

    raise RuntimeError("retry loop exhausted unexpectedly")


base.call_chat = resilient_call_chat


if __name__ == "__main__":
    base.main()
