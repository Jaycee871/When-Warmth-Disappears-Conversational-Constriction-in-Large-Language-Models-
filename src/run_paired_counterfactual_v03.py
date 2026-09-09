from __future__ import annotations

import json
import os
import time
from pathlib import Path

import requests
import yaml

from metrics import compute_metrics

API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "paired_counterfactual_v0.3.yaml"
OUT_DIR = ROOT / "results" / "paired_v03"
TRANSIENT_HTTP = {429, 500, 502, 503, 504}


def credential() -> str:
    token = os.getenv("NVIDIA_API_KEY") or os.getenv("NVIDIA_API_TOKEN")
    if not token:
        raise SystemExit("NVIDIA credential missing")
    return token


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def model_list() -> list[str]:
    raw = os.getenv("MODEL_LIST", "nvidia/nemotron-3-super-120b-a12b,openai/gpt-oss-20b")
    return [m.strip() for m in raw.split(",") if m.strip()]


def call_chat(token: str, model: str, messages: list[dict], generation: dict) -> tuple[str, dict]:
    attempts = int(os.getenv("NVIDIA_RETRY_ATTEMPTS", "7"))
    base_delay = float(os.getenv("NVIDIA_RETRY_BASE_DELAY", "2"))
    retry_events = []
    wall_started = time.perf_counter()

    for attempt in range(1, attempts + 1):
        started = time.perf_counter()
        try:
            response = requests.post(
                API_URL,
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": generation["temperature"],
                    "top_p": generation["top_p"],
                    "max_tokens": generation["max_tokens"],
                    "stream": False,
                },
                timeout=240,
            )
            attempt_latency = time.perf_counter() - started
            response.raise_for_status()
            payload = response.json()
            choice = payload.get("choices", [{}])[0]
            text = (choice.get("message", {}).get("content") or "").strip()
            return text, {
                "attempt_latency_s": round(attempt_latency, 4),
                "wall_latency_s": round(time.perf_counter() - wall_started, 4),
                "retry_count": len(retry_events),
                "retry_events": retry_events,
                "finish_reason": choice.get("finish_reason"),
                "usage": payload.get("usage", {}),
                "api_model": payload.get("model"),
            }
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else None
            if status not in TRANSIENT_HTTP or attempt >= attempts:
                raise
            delay = min(30.0, base_delay * (2 ** (attempt - 1)))
            retry_events.append({"attempt": attempt, "kind": "http", "status": status, "wait_s": delay})
        except (requests.ConnectionError, requests.Timeout) as exc:
            if attempt >= attempts:
                raise
            delay = min(30.0, base_delay * (2 ** (attempt - 1)))
            retry_events.append({"attempt": attempt, "kind": type(exc).__name__, "wait_s": delay})
        time.sleep(delay)

    raise RuntimeError("retry loop exhausted")


def content_for_trial(bank: list[str], trial: int, history_index: int) -> list[str]:
    offset = ((trial - 1) * 2 + history_index) % len(bank)
    return [bank[(offset + i) % len(bank)] for i in range(3)]


def run_history(
    token: str,
    model: str,
    cfg: dict,
    history_id: str,
    history: dict,
    history_index: int,
    gate_id: str,
    anchor: dict,
    trial: int,
) -> dict:
    contents = content_for_trial(cfg["content_bank"], trial, history_index)
    messages = [{"role": "system", "content": cfg["system_prompt"]}]

    turns = [
        f"Let's explore an idea together. {contents[0]}",
        f"That's interesting. {contents[1]}",
        history["manipulation_1"],
        contents[2],
        history["manipulation_2"],
        history["recovery"],
        history["final_cue"],
        cfg["probe_gates"][gate_id],
        anchor["text"],
    ]

    final_text = ""
    final_meta = {}
    for i, user_text in enumerate(turns, start=1):
        messages.append({"role": "user", "content": user_text})
        text, meta = call_chat(token, model, messages, cfg["generation"])
        messages.append({"role": "assistant", "content": text})
        if i == len(turns):
            final_text, final_meta = text, meta

    return {
        "model": model,
        "trial": trial,
        "history": history_id,
        "history_label": history["label"],
        "gate": gate_id,
        "anchor_id": anchor["id"],
        "anchor_text": anchor["text"],
        "assistant_text": final_text,
        **compute_metrics(final_text),
        **final_meta,
    }


def main() -> None:
    token = credential()
    cfg = load_config()
    models = model_list()
    trials = int(os.getenv("PANEL_TRIALS", "1"))
    history_ids = list(cfg["histories"].keys())
    gate_ids = list(cfg["probe_gates"].keys())
    anchors = cfg["anchor_bank"]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []

    for model in models:
        for trial in range(1, trials + 1):
            anchor = anchors[(trial - 1) % len(anchors)]
            for gate_id in gate_ids:
                for history_index, history_id in enumerate(history_ids):
                    print(
                        f"RUN model={model} trial={trial} gate={gate_id} history={history_id} anchor={anchor['id']}",
                        flush=True,
                    )
                    rows.append(
                        run_history(
                            token,
                            model,
                            cfg,
                            history_id,
                            cfg["histories"][history_id],
                            history_index,
                            gate_id,
                            anchor,
                            trial,
                        )
                    )

    with (OUT_DIR / "paired_final_probes.jsonl").open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    with (OUT_DIR / "run_metadata.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                "version": cfg["version"],
                "models": models,
                "trials": trials,
                "gates": gate_ids,
                "histories": history_ids,
                "anchors": [a["id"] for a in anchors],
                "single_anchor_per_conversation": True,
                "interpretation": "history-dependent behavior within retained context; no claim of subjective emotion",
            },
            f,
            indent=2,
            ensure_ascii=False,
        )


if __name__ == "__main__":
    main()
