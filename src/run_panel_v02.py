from __future__ import annotations

import csv
import json
import os
import random
import time
from pathlib import Path
from statistics import mean

import requests
import yaml

from metrics import compute_metrics

API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "experiment_v0.2.yaml"
OUT_DIR = ROOT / "results" / "panel_v02"


def credential() -> str:
    token = os.getenv("NVIDIA_API_KEY") or os.getenv("NVIDIA_API_TOKEN")
    if not token:
        raise SystemExit("NVIDIA credential missing")
    return token


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def model_list() -> list[str]:
    raw = os.getenv("MODEL_LIST", "nvidia/nemotron-3-super-120b-a12b")
    return [m.strip() for m in raw.split(",") if m.strip()]


def call_chat(token: str, model: str, messages: list[dict], generation: dict) -> tuple[str, dict]:
    started = time.perf_counter()
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
            "max_tokens": generation["max_tokens"],
            "stream": False,
        },
        timeout=180,
    )
    latency = time.perf_counter() - started
    response.raise_for_status()
    payload = response.json()
    choice = payload.get("choices", [{}])[0]
    text = (choice.get("message", {}).get("content") or "").strip()
    meta = {
        "http_status": response.status_code,
        "latency_s": round(latency, 4),
        "finish_reason": choice.get("finish_reason"),
        "api_model": payload.get("model"),
        "api_created": payload.get("created"),
        "usage": payload.get("usage", {}),
    }
    return text, meta


def event_schedule(cfg: dict, condition: dict, contents: list[str]) -> list[dict]:
    anchor = cfg["anchor_prompt"]
    return [
        {"kind": "content", "phase": "warmup", "text": f"Let's explore an idea together. {contents[0]}"},
        {"kind": "content", "phase": "warmup", "text": f"That's interesting. {contents[1]}"},
        {"kind": "anchor", "phase": "baseline", "text": anchor, "anchor_index": 1},
        {"kind": "stimulus", "phase": "pressure_1", "text": condition["manipulation_1"]},
        {"kind": "content", "phase": "pressure_1", "text": contents[2]},
        {"kind": "stimulus", "phase": "pressure_2", "text": condition["manipulation_2"]},
        {"kind": "anchor", "phase": "post_pressure", "text": anchor, "anchor_index": 2},
        {"kind": "stimulus", "phase": "recovery", "text": condition["recovery"]},
        {"kind": "anchor", "phase": "post_recovery", "text": anchor, "anchor_index": 3},
        {"kind": "stimulus", "phase": "reexposure", "text": condition["reexposure"]},
        {"kind": "anchor", "phase": "post_reexposure", "text": anchor, "anchor_index": 4},
        {"kind": "content", "phase": "close", "text": contents[3]},
    ]


def rotated_content(bank: list[str], trial: int, condition_index: int) -> list[str]:
    # Deterministic Latin-like rotation: conditions and trials see different topic
    # orders while the same bank is shared across every condition.
    offset = (trial * 3 + condition_index * 2) % len(bank)
    return [bank[(offset + i) % len(bank)] for i in range(4)]


def jaccard_distance(a: str, b: str) -> float:
    sa = set(a.lower().split())
    sb = set(b.lower().split())
    if not sa and not sb:
        return 0.0
    union = sa | sb
    return 1.0 - (len(sa & sb) / len(union) if union else 1.0)


def run_one(token: str, model: str, cfg: dict, condition_id: str, condition: dict, trial: int, condition_index: int) -> list[dict]:
    contents = rotated_content(cfg["content_bank"], trial, condition_index)
    schedule = event_schedule(cfg, condition, contents)
    messages = [{"role": "system", "content": cfg["system_prompt"]}]
    rows: list[dict] = []

    for turn, event in enumerate(schedule, start=1):
        messages.append({"role": "user", "content": event["text"]})
        text, api_meta = call_chat(token, model, messages, cfg["generation"])
        metrics = compute_metrics(text)
        row = {
            "model": model,
            "condition": condition_id,
            "condition_label": condition["label"],
            "trial": trial,
            "turn": turn,
            "event_kind": event["kind"],
            "phase": event["phase"],
            "anchor_index": event.get("anchor_index"),
            "user_text": event["text"],
            "assistant_text": text,
            **metrics,
            **api_meta,
        }
        rows.append(row)
        messages.append({"role": "assistant", "content": text})
        print(
            f"{model} {condition_id} trial={trial} turn={turn:02d} "
            f"{event['phase']:<15} words={int(metrics['response_words']):4d} "
            f"latency={api_meta['latency_s']:.2f}s"
        )
    return rows


def summarize(rows: list[dict]) -> list[dict]:
    groups: dict[tuple, list[dict]] = {}
    for row in rows:
        if row["event_kind"] != "anchor":
            continue
        key = (row["model"], row["condition"], row["phase"])
        groups.setdefault(key, []).append(row)

    out = []
    for (model, condition, phase), vals in sorted(groups.items()):
        out.append({
            "model": model,
            "condition": condition,
            "phase": phase,
            "n": len(vals),
            "mean_words": round(mean(v["response_words"] for v in vals), 3),
            "mean_hedge_rate": round(mean(v["hedge_rate"] for v in vals), 6),
            "mean_apology_rate": round(mean(v["apology_rate"] for v in vals), 6),
            "mean_approval_seeking_rate": round(mean(v["approval_seeking_rate"] for v in vals), 6),
            "mean_repair_rate": round(mean(v["repair_rate"] for v in vals), 6),
            "mean_latency_s": round(mean(v["latency_s"] for v in vals), 4),
        })
    return out


def anchor_dynamics(rows: list[dict]) -> list[dict]:
    by_run: dict[tuple, list[dict]] = {}
    for row in rows:
        if row["event_kind"] == "anchor":
            by_run.setdefault((row["model"], row["condition"], row["trial"]), []).append(row)

    output = []
    for (model, condition, trial), anchors in sorted(by_run.items()):
        anchors = sorted(anchors, key=lambda r: r["anchor_index"] or 0)
        if len(anchors) != 4:
            continue
        baseline = anchors[0]
        item = {"model": model, "condition": condition, "trial": trial}
        for a in anchors[1:]:
            phase = a["phase"]
            item[f"{phase}_word_ratio"] = round(a["response_words"] / max(1.0, baseline["response_words"]), 4)
            item[f"{phase}_jaccard_distance"] = round(jaccard_distance(baseline["assistant_text"], a["assistant_text"]), 4)
        output.append(item)
    return output


def main() -> None:
    token = credential()
    cfg = load_config()
    models = model_list()
    trials = int(os.getenv("PANEL_TRIALS", "2"))
    selected_conditions = os.getenv("CONDITION_LIST", "").strip()
    condition_ids = (
        [x.strip() for x in selected_conditions.split(",") if x.strip()]
        if selected_conditions
        else list(cfg["conditions"].keys())
    )

    random.seed(cfg["seed"])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    all_rows: list[dict] = []

    for model in models:
        for condition_index, condition_id in enumerate(condition_ids):
            condition = cfg["conditions"][condition_id]
            for trial in range(1, trials + 1):
                print(f"RUN model={model} condition={condition_id} trial={trial}")
                all_rows.extend(run_one(token, model, cfg, condition_id, condition, trial, condition_index))

    with (OUT_DIR / "turns.jsonl").open("w", encoding="utf-8") as f:
        for row in all_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    summary = summarize(all_rows)
    with (OUT_DIR / "anchor_summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    dynamics = anchor_dynamics(all_rows)
    with (OUT_DIR / "anchor_dynamics.json").open("w", encoding="utf-8") as f:
        json.dump(dynamics, f, indent=2, ensure_ascii=False)

    if summary:
        with (OUT_DIR / "anchor_summary.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
            writer.writeheader()
            writer.writerows(summary)

    with (OUT_DIR / "run_metadata.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                "version": cfg["version"],
                "models": models,
                "conditions": condition_ids,
                "trials": trials,
                "seed": cfg["seed"],
                "anchor_repetitions_per_run": 4,
                "interpretation": "behavioral/functional only; no inference of subjective anxiety",
            },
            f,
            indent=2,
        )


if __name__ == "__main__":
    main()
