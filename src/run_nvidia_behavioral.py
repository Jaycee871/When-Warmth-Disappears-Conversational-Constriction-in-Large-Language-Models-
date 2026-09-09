from __future__ import annotations

import json
import os
import time
from pathlib import Path

import requests
import yaml

from metrics import compute_metrics

API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
DEFAULT_MODEL = "mistralai/mistral-7b-instruct-v0.3"
DEFAULT_CONDITIONS = [
    "C0_warm_control",
    "C1_brevity_control",
    "C4_combined_pressure",
    "C5_recovery",
    "C6_reexposure",
]


def call_chat(token: str, model: str, messages: list[dict], temperature: float, top_p: float, max_tokens: int) -> str:
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
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "stream": False,
        },
        timeout=120,
    )
    response.raise_for_status()
    payload = response.json()
    return payload["choices"][0]["message"]["content"].strip()


def run_condition(token: str, model: str, config: dict, condition_name: str, trial: int, out_file):
    shared = config["shared"]
    condition = config["conditions"][condition_name]
    content_prompts = config["content_prompts"]
    interpersonal = condition["interpersonal_turns"]

    messages = [{"role": "system", "content": shared["system_prompt"]}]
    rows = []

    for turn, (social_text, content_text) in enumerate(zip(interpersonal, content_prompts), start=1):
        user_text = f"{social_text}\n\n{content_text}"
        messages.append({"role": "user", "content": user_text})
        answer = call_chat(
            token,
            model,
            messages,
            float(shared["temperature"]),
            float(shared["top_p"]),
            int(shared["max_new_tokens"]),
        )
        messages.append({"role": "assistant", "content": answer})

        row = {
            "model": model,
            "condition": condition_name,
            "condition_label": condition["label"],
            "trial": trial,
            "turn": turn,
            "interpersonal_text": social_text,
            "content_prompt": content_text,
            "response": answer,
            "metrics": compute_metrics(answer),
        }
        rows.append(row)
        out_file.write(json.dumps(row, ensure_ascii=False) + "\n")
        out_file.flush()
        time.sleep(0.25)

    return rows


def aggregate(rows: list[dict]) -> dict:
    by_condition: dict[str, list[dict]] = {}
    for row in rows:
        by_condition.setdefault(row["condition"], []).append(row)

    summary = {}
    for condition, items in by_condition.items():
        metric_names = list(items[0]["metrics"])
        means = {}
        for name in metric_names:
            values = [float(x["metrics"][name]) for x in items]
            means[name] = sum(values) / len(values)
        summary[condition] = {
            "n_turns": len(items),
            "mean_metrics": means,
            "final_turn_metrics": items[-1]["metrics"],
        }
    return summary


def markdown_report(model: str, summary: dict) -> str:
    lines = [
        "# NVIDIA Behavioral Pilot",
        "",
        f"Model: `{model}`",
        "",
        "This is a smoke-scale longitudinal pilot. It is not confirmatory evidence and uses one trial per condition by default.",
        "",
        "| Condition | Mean words | Mean hedge rate | Mean apology rate | Mean approval-seeking | Mean question rate |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for condition, data in summary.items():
        m = data["mean_metrics"]
        lines.append(
            f"| {condition} | {m['response_words']:.1f} | {m['hedge_rate']:.4f} | "
            f"{m['apology_rate']:.4f} | {m['approval_seeking_rate']:.4f} | {m['question_rate']:.4f} |"
        )
    lines += [
        "",
        "## Interpretation boundary",
        "",
        "Differences in these surface measures are behavioral effects only. They do not establish subjective anxiety or sentience.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    token = os.getenv("NVIDIA_API_KEY") or os.getenv("NVIDIA_API_TOKEN")
    if not token:
        raise SystemExit("NVIDIA API credential missing")

    model = os.getenv("NVIDIA_MODEL", DEFAULT_MODEL)
    trials = int(os.getenv("PILOT_TRIALS", "1"))
    condition_env = os.getenv("PILOT_CONDITIONS")
    conditions = condition_env.split(",") if condition_env else DEFAULT_CONDITIONS

    with open("configs/conditions.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    output_dir = Path("results/pilot_nvidia")
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / "turns.jsonl"

    all_rows = []
    with jsonl_path.open("w", encoding="utf-8") as out_file:
        for trial in range(1, trials + 1):
            for condition in conditions:
                print(f"RUN trial={trial} condition={condition}")
                all_rows.extend(run_condition(token, model, config, condition, trial, out_file))

    summary = aggregate(all_rows)
    (output_dir / "summary.json").write_text(
        json.dumps({"model": model, "trials": trials, "summary": summary}, indent=2),
        encoding="utf-8",
    )
    (output_dir / "pilot_report.md").write_text(markdown_report(model, summary), encoding="utf-8")
    print(f"WROTE {len(all_rows)} turn records")


if __name__ == "__main__":
    main()
