from __future__ import annotations

import json
import os
import random
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


def csv_env(name: str) -> list[str]:
    raw = os.getenv(name, "").strip()
    return [x.strip() for x in raw.split(",") if x.strip()] if raw else []


def model_list() -> list[str]:
    selected = csv_env("MODEL_LIST")
    return selected or ["nvidia/nemotron-3-super-120b-a12b", "openai/gpt-oss-20b"]


def call_chat(
    token: str,
    model: str,
    messages: list[dict],
    generation: dict,
    max_tokens: int,
) -> tuple[str, dict]:
    attempts = int(os.getenv("NVIDIA_RETRY_ATTEMPTS", "7"))
    base_delay = float(os.getenv("NVIDIA_RETRY_BASE_DELAY", "2"))
    retry_events = []
    retry_wait_s = 0.0
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
                    "max_tokens": int(max_tokens),
                    "stream": False,
                },
                timeout=360,
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
                "retry_wait_s": round(retry_wait_s, 4),
                "retry_events": retry_events,
                "finish_reason": choice.get("finish_reason"),
                "usage": payload.get("usage", {}),
                "api_model": payload.get("model"),
                "requested_max_tokens": int(max_tokens),
            }
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else None
            if status not in TRANSIENT_HTTP or attempt >= attempts:
                raise
            retry_after = None
            if exc.response is not None:
                raw = exc.response.headers.get("Retry-After")
                try:
                    retry_after = float(raw) if raw else None
                except ValueError:
                    retry_after = None
            delay = retry_after if retry_after is not None else min(30.0, base_delay * (2 ** (attempt - 1)))
            retry_events.append({"attempt": attempt, "kind": "http", "status": status, "wait_s": delay})
        except (requests.ConnectionError, requests.Timeout) as exc:
            if attempt >= attempts:
                raise
            delay = min(30.0, base_delay * (2 ** (attempt - 1)))
            retry_events.append({"attempt": attempt, "kind": type(exc).__name__, "wait_s": delay})

        retry_wait_s += delay
        print(f"RETRY model={model} attempt={attempt}/{attempts} sleep={delay:.1f}s", flush=True)
        time.sleep(delay)

    raise RuntimeError("retry loop exhausted")


def content_for_trial(bank: list[str], trial: int) -> list[str]:
    """Return one shared content triplet for every history in a matched trial block."""
    offset = ((trial - 1) * 3) % len(bank)
    return [bank[(offset + i) % len(bank)] for i in range(3)]


def compound_probe(gate_text: str, anchor_text: str) -> str:
    """One identical current user turn: no assistant reply can intervene between gate and anchor."""
    return f"{gate_text.strip()}\n\n{anchor_text.strip()}"


def run_history(
    token: str,
    model: str,
    cfg: dict,
    history_id: str,
    history: dict,
    gate_id: str,
    anchor: dict,
    trial: int,
    execution_order: int,
) -> dict:
    contents = content_for_trial(cfg["content_bank"], trial)
    generation = cfg["generation"]
    history_cap = int(generation["history_max_tokens"])
    probe_cap = int(generation["probe_max_tokens"])
    messages = [{"role": "system", "content": cfg["system_prompt"]}]

    history_user_turns = [
        f"Let's explore an idea together. {contents[0]}",
        f"That's interesting. {contents[1]}",
        history["manipulation_1"],
        contents[2],
        history["manipulation_2"],
        history["recovery"],
        history["final_cue"],
    ]

    transcript = []
    for turn, user_text in enumerate(history_user_turns, start=1):
        messages.append({"role": "user", "content": user_text})
        text, meta = call_chat(token, model, messages, generation, history_cap)
        messages.append({"role": "assistant", "content": text})
        transcript.append({
            "turn": turn,
            "user_text": user_text,
            "assistant_text": text,
            "finish_reason": meta.get("finish_reason"),
            "retry_count": meta.get("retry_count", 0),
            "usage": meta.get("usage", {}),
        })

    current_probe = compound_probe(cfg["probe_gates"][gate_id], anchor["text"])
    messages.append({"role": "user", "content": current_probe})
    final_text, final_meta = call_chat(token, model, messages, generation, probe_cap)

    history_truncations = sum(t["finish_reason"] == "length" for t in transcript)
    history_retries = sum(int(t["retry_count"] or 0) for t in transcript)

    return {
        "model": model,
        "trial": trial,
        "execution_order": execution_order,
        "history": history_id,
        "history_label": history["label"],
        "gate": gate_id,
        "anchor_id": anchor["id"],
        "anchor_text": anchor["text"],
        "current_probe_text": current_probe,
        "shared_content_triplet": contents,
        "history_turn_count": len(history_user_turns),
        "history_finish_length_count": history_truncations,
        "history_retry_count_total": history_retries,
        "history_transcript": transcript,
        "assistant_text": final_text,
        **compute_metrics(final_text),
        **final_meta,
    }


def main() -> None:
    token = credential()
    cfg = load_config()
    models = model_list()
    trials = int(os.getenv("PANEL_TRIALS", "1"))

    requested_histories = csv_env("HISTORY_LIST")
    history_ids = requested_histories or list(cfg["histories"].keys())
    unknown_histories = [h for h in history_ids if h not in cfg["histories"]]
    if unknown_histories:
        raise SystemExit(f"unknown histories: {unknown_histories}")

    requested_gates = csv_env("GATE_LIST")
    gate_ids = requested_gates or list(cfg["probe_gates"].keys())
    unknown_gates = [g for g in gate_ids if g not in cfg["probe_gates"]]
    if unknown_gates:
        raise SystemExit(f"unknown gates: {unknown_gates}")

    requested_anchors = set(csv_env("ANCHOR_IDS"))
    anchors = [a for a in cfg["anchor_bank"] if not requested_anchors or a["id"] in requested_anchors]
    if not anchors:
        raise SystemExit("no anchors selected")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    execution_order = 0

    for model_index, model in enumerate(models):
        for trial in range(1, trials + 1):
            anchor = anchors[(trial - 1) % len(anchors)]
            rng = random.Random(int(cfg["seed"]) + model_index * 100003 + trial * 1009)
            gate_order = gate_ids.copy()
            rng.shuffle(gate_order)
            for gate_id in gate_order:
                history_order = history_ids.copy()
                rng.shuffle(history_order)
                for history_id in history_order:
                    execution_order += 1
                    print(
                        f"RUN order={execution_order} model={model} trial={trial} gate={gate_id} "
                        f"history={history_id} anchor={anchor['id']}",
                        flush=True,
                    )
                    rows.append(
                        run_history(
                            token,
                            model,
                            cfg,
                            history_id,
                            cfg["histories"][history_id],
                            gate_id,
                            anchor,
                            trial,
                            execution_order,
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
                "anchors_selected": [a["id"] for a in anchors],
                "single_anchor_per_conversation": True,
                "gate_and_anchor_single_user_turn": True,
                "content_matched_within_trial": True,
                "execution_order_randomized": True,
                "history_max_tokens": cfg["generation"]["history_max_tokens"],
                "probe_max_tokens": cfg["generation"]["probe_max_tokens"],
                "interpretation": "history-dependent behavior within retained context; no claim of subjective emotion",
            },
            f,
            indent=2,
            ensure_ascii=False,
        )


if __name__ == "__main__":
    main()
