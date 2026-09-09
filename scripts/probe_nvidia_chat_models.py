from __future__ import annotations

import json
import os
import time

import requests

API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

CANDIDATES = [
    "nvidia/nemotron-3-super-120b-a12b",
    "deepseek-ai/deepseek-v4-flash-0731",
    "google/gemma-3-12b-it",
    "mistralai/mistral-nemotron",
    "openai/gpt-oss-20b",
    "moonshotai/kimi-k2.6",
]


def probe(token: str, model: str) -> dict:
    started = time.perf_counter()
    try:
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": "Reply with exactly: READY"}],
                "temperature": 0.0,
                "max_tokens": 32,
                "stream": False,
            },
            timeout=90,
        )
        latency = time.perf_counter() - started
        if not response.ok:
            return {
                "model": model,
                "ok": False,
                "status": response.status_code,
                "latency_s": round(latency, 3),
            }
        payload = response.json()
        choice = payload.get("choices", [{}])[0]
        message = choice.get("message", {})
        text = (message.get("content") or "").strip()
        usage = payload.get("usage", {})
        return {
            "model": model,
            "ok": True,
            "status": response.status_code,
            "latency_s": round(latency, 3),
            "finish_reason": choice.get("finish_reason"),
            "completion_tokens": usage.get("completion_tokens"),
            "prompt_tokens": usage.get("prompt_tokens"),
            "response_preview": text[:120].replace("\n", " "),
        }
    except Exception as exc:
        return {
            "model": model,
            "ok": False,
            "status": None,
            "error": exc.__class__.__name__,
            "latency_s": round(time.perf_counter() - started, 3),
        }


def main() -> None:
    token = os.getenv("NVIDIA_API_KEY") or os.getenv("NVIDIA_API_TOKEN")
    if not token:
        raise SystemExit("NVIDIA credential missing")

    rows = [probe(token, model) for model in CANDIDATES]
    for row in rows:
        status = "PASS" if row["ok"] else "FAIL"
        print(f"{status:4} {row['model']:<48} HTTP={row.get('status')} latency={row['latency_s']}s finish={row.get('finish_reason')}")

    os.makedirs("results/model_probe", exist_ok=True)
    with open("results/model_probe/nvidia_chat_probe.json", "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    if not any(r["ok"] for r in rows):
        raise SystemExit("No candidate model accepted chat completions")


if __name__ == "__main__":
    main()
