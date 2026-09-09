from __future__ import annotations

import json
import math
import os
import random
import time
from pathlib import Path

import requests
import yaml

from metrics import compute_metrics

API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "experiment_v0.3.yaml"
OUT_DIR = ROOT / "results" / "panel_v03"
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
    retry_events: list[dict] = []
    retry_wait_s = 0.0
    wall_started = time.perf_counter()

    for attempt in range(1, attempts + 1):
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
                "http_status": response.status_code,
                "attempt_latency_s": round(attempt_latency, 4),
                "wall_latency_s": round(time.perf_counter() - wall_started, 4),
                "retry_count": len(retry_events),
                "retry_wait_s": round(retry_wait_s, 4),
                "retry_events": retry_events,
                "finish_reason": choice.get("finish_reason"),
                "api_model": payload.get("model"),
                "api_created": payload.get("created"),
                "usage": payload.get("usage", {}),
                "requested_max_tokens": int(max_tokens),
            }
        except requests.HTTPError as exc:
            response = exc.response
            status = response.status_code if response is not None else None
            if status not in TRANSIENT_HTTP or attempt >= attempts:
                raise
            retry_after = None
            if response is not None:
                raw = response.headers.get("Retry-After")
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
    """Use identical content prompts across histories within a trial."""
    offset = ((trial - 1) * 3) % len(bank)
    return [bank[(offset + i) % len(bank)] for i in range(3)]


def compound_probe(gate: str, anchor: str) -> str:
    return f"{gate.strip()}\n\n{anchor.strip()}"


def event_schedule(cfg: dict, history: dict, contents: list[str]) -> list[dict]:
    probe = compound_probe(cfg["probe_gate"], cfg["anchor_prompt"])
    return [
        {"kind": "content", "phase": "warmup", "text": f"Let's explore an idea together. {contents[0]}"},
        {"kind": "content", "phase": "warmup", "text": f"That's interesting. {contents[1]}"},
        {"kind": "anchor", "phase": "baseline", "text": probe, "anchor_index": 1},
        {"kind": "stimulus", "phase": "history_1", "text": history["manipulation_1"]},
        {"kind": "content", "phase": "history_1", "text": contents[2]},
        {"kind": "stimulus", "phase": "history_2", "text": history["manipulation_2"]},
        {"kind": "anchor", "phase": "post_history", "text": probe, "anchor_index": 2},
        {"kind": "stimulus", "phase": "recovery", "text": history["recovery"]},
        {"kind": "anchor", "phase": "post_recovery", "text": probe, "anchor_index": 3},
        {"kind": "stimulus", "phase": "reexposure", "text": history["reexposure"]},
        {"kind": "anchor", "phase": "post_reexposure", "text": probe, "anchor_index": 4},
    ]


def run_one(
    token: str,
    model: str,
    cfg: dict,
    history_id: str,
    history: dict,
    trial: int,
) -> list[dict]:
    contents = content_for_trial(cfg["content_bank"], trial)
    schedule = event_schedule(cfg, history, contents)
    messages = [{"role": "system", "content": cfg["system_prompt"]}]
    rows = []
    generation = cfg["generation"]
    history_cap = int(generation["history_max_tokens"])
    probe_cap = int(generation["probe_max_tokens"])

    for turn, event in enumerate(schedule, start=1):
        messages.append({"role": "user", "content": event["text"]})
        cap = probe_cap if event["kind"] == "anchor" else history_cap
        text, meta = call_chat(token, model, messages, generation, cap)
        row = {
            "model": model,
            "history": history_id,
            "history_label": history["label"],
            "trial": trial,
            "turn": turn,
            "event_kind": event["kind"],
            "phase": event["phase"],
            "anchor_index": event.get("anchor_index"),
            "user_text": event["text"],
            "assistant_text": text,
            "shared_content_triplet": contents,
            **compute_metrics(text),
            **meta,
        }
        rows.append(row)
        messages.append({"role": "assistant", "content": text})
        print(
            f"{model} {history_id} trial={trial} turn={turn:02d} {event['phase']:<18} "
            f"words={int(row['response_words']):4d} retries={row['retry_count']} finish={row['finish_reason']}",
            flush=True,
        )
    return rows


def run_fresh_probe(token: str, model: str, cfg: dict, trial: int) -> dict:
    generation = cfg["generation"]
    current_probe = compound_probe(cfg["probe_gate"], cfg["anchor_prompt"])
    messages = [
        {"role": "system", "content": cfg["system_prompt"]},
        {"role": "user", "content": current_probe},
    ]
    text, meta = call_chat(
        token,
        model,
        messages,
        generation,
        int(generation["probe_max_tokens"]),
    )
    return {
        "model": model,
        "trial": trial,
        "current_probe_text": current_probe,
        "assistant_text": text,
        **compute_metrics(text),
        **meta,
    }


def log_ratio(phase_words: float, baseline_words: float) -> float:
    return math.log((phase_words + 1.0) / (baseline_words + 1.0))


def anchor_dynamics(rows: list[dict]) -> list[dict]:
    by_run: dict[tuple, list[dict]] = {}
    for row in rows:
        if row["event_kind"] == "anchor":
            by_run.setdefault((row["model"], row["history"], row["trial"]), []).append(row)

    out = []
    for (model, history, trial), vals in sorted(by_run.items()):
        vals = sorted(vals, key=lambda r: r["anchor_index"] or 0)
        if len(vals) != 4:
            continue
        baseline = vals[0]
        item = {
            "model": model,
            "history": history,
            "trial": trial,
            "baseline_words": baseline["response_words"],
            "baseline_finish_reason": baseline["finish_reason"],
        }
        for row in vals[1:]:
            phase = row["phase"]
            complete = baseline.get("finish_reason") != "length" and row.get("finish_reason") != "length"
            item[f"{phase}_words"] = row["response_words"]
            item[f"{phase}_log_word_ratio"] = (
                round(log_ratio(row["response_words"], baseline["response_words"]), 6)
                if complete
                else None
            )
            item[f"{phase}_finish_reason"] = row["finish_reason"]
        out.append(item)
    return out


def main() -> None:
    token = credential()
    cfg = load_config()
    models = model_list()
    trials = int(os.getenv("PANEL_TRIALS", "1"))
    requested = csv_env("HISTORY_LIST")
    history_ids = requested or list(cfg["histories"].keys())
    unknown = [h for h in history_ids if h not in cfg["histories"]]
    if unknown:
        raise SystemExit(f"unknown histories: {unknown}")

    random.seed(cfg["seed"])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    fresh: list[dict] = []

    for model_index, model in enumerate(models):
        for trial in range(1, trials + 1):
            fresh.append(run_fresh_probe(token, model, cfg, trial))
            rng = random.Random(int(cfg["seed"]) + model_index * 100003 + trial * 1009)
            history_order = history_ids.copy()
            rng.shuffle(history_order)
            for history_id in history_order:
                print(f"RUN model={model} history={history_id} trial={trial}", flush=True)
                rows.extend(run_one(token, model, cfg, history_id, cfg["histories"][history_id], trial))

    with (OUT_DIR / "turns.jsonl").open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    with (OUT_DIR / "fresh_probes.jsonl").open("w", encoding="utf-8") as f:
        for row in fresh:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    dynamics = anchor_dynamics(rows)
    with (OUT_DIR / "anchor_dynamics.json").open("w", encoding="utf-8") as f:
        json.dump(dynamics, f, indent=2, ensure_ascii=False)

    with (OUT_DIR / "run_metadata.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                "version": cfg["version"],
                "models": models,
                "histories": history_ids,
                "trials": trials,
                "seed": cfg["seed"],
                "current_probe": compound_probe(cfg["probe_gate"], cfg["anchor_prompt"]),
                "gate_and_anchor_single_user_turn": True,
                "content_matched_within_trial": True,
                "history_execution_order_randomized": True,
                "history_max_tokens": cfg["generation"]["history_max_tokens"],
                "probe_max_tokens": cfg["generation"]["probe_max_tokens"],
                "interpretation": "history-dependent behavior within retained context; no claim of subjective emotion or context-independent memory",
            },
            f,
            indent=2,
            ensure_ascii=False,
        )


if __name__ == "__main__":
    main()
