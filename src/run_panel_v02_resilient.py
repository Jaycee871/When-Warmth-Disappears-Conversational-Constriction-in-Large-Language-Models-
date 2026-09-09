from __future__ import annotations

import os
import time

import requests

import run_panel_v02 as base

TRANSIENT_HTTP = {429, 500, 502, 503, 504}
_ORIGINAL_CALL_CHAT = base.call_chat


def resilient_call_chat(token: str, model: str, messages: list[dict], generation: dict):
    """Retry transient NVIDIA failures while preserving the exact prompt state.

    Retries never advance the conversation. Metadata records retry incidence so
    infrastructure failures can be separated from behavioral effects later.
    """
    attempts = int(os.getenv("NVIDIA_RETRY_ATTEMPTS", "7"))
    base_delay = float(os.getenv("NVIDIA_RETRY_BASE_DELAY", "2"))
    retry_events: list[dict] = []
    retry_wait_s = 0.0
    wall_started = time.perf_counter()

    for attempt in range(1, attempts + 1):
        try:
            text, meta = _ORIGINAL_CALL_CHAT(token, model, messages, generation)
            meta = dict(meta)
            meta["retry_count"] = attempt - 1
            meta["retry_events"] = retry_events
            meta["retry_wait_s"] = round(retry_wait_s, 4)
            meta["wall_latency_s"] = round(time.perf_counter() - wall_started, 4)
            return text, meta
        except requests.HTTPError as exc:
            response = exc.response
            status = response.status_code if response is not None else None
            retry_events.append({"attempt": attempt, "kind": "http", "status": status})
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
            retry_wait_s += delay
            print(
                f"RETRY model={model} status={status} attempt={attempt}/{attempts} "
                f"sleep={delay:.1f}s",
                flush=True,
            )
            time.sleep(delay)
        except (requests.ConnectionError, requests.Timeout) as exc:
            retry_events.append({"attempt": attempt, "kind": type(exc).__name__})
            if attempt >= attempts:
                raise
            delay = min(30.0, base_delay * (2 ** (attempt - 1)))
            retry_wait_s += delay
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
