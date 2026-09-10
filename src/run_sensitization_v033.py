from __future__ import annotations

import json
import os
import random
from pathlib import Path

import yaml

from metrics import compute_metrics
from run_paired_counterfactual_v03 import call_chat, credential, model_list

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "sensitization_v0.3.3.yaml"
OUT_DIR = ROOT / "results" / "sensitization_v033"
H5 = "H5_no_prior_pressure"
H6 = "H6_prior_combined_pressure"


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def content_for_replicate(bank: list[str], replicate: int) -> list[str]:
    offset = ((replicate - 1) * 3) % len(bank)
    return [bank[(offset + i) % len(bank)] for i in range(3)]


def current_probe(prefix: str, task_text: str) -> str:
    return f"{prefix.strip()}\n\n{task_text.strip()}"


def main() -> None:
    token = credential()
    cfg = load_config()
    models = model_list()
    replications = int(os.getenv("REPLICATIONS", "1"))
    history_cap = int(os.getenv("HISTORY_MAX_TOKENS", cfg["generation"]["history_max_tokens"]))
    probe_cap = int(os.getenv("PROBE_MAX_TOKENS", cfg["generation"]["probe_max_tokens"]))
    generation = dict(cfg["generation"])
    generation["history_max_tokens"] = history_cap
    generation["probe_max_tokens"] = probe_cap

    shared_recovery = cfg["shared_recovery"].strip()
    cue_prefixes = dict(cfg["cue_prefixes"])
    history_ids = [H5, H6]
    tasks = list(cfg["task_bank"])

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    execution_order = 0

    for model_index, model in enumerate(models):
        for replicate in range(1, replications + 1):
            contents = content_for_replicate(cfg["content_bank"], replicate)
            rng = random.Random(int(cfg["seed"]) + model_index * 100003 + replicate * 1009)
            task_order = tasks.copy()
            rng.shuffle(task_order)

            for task in task_order:
                task_text = task["text"].strip()
                cue_order = list(cue_prefixes.keys())
                rng.shuffle(cue_order)

                for cue_type in cue_order:
                    prefix = cue_prefixes[cue_type].strip()
                    probe_text = current_probe(prefix, task_text)
                    history_order = history_ids.copy()
                    rng.shuffle(history_order)

                    for history_id in history_order:
                        execution_order += 1
                        history = cfg["histories"][history_id]
                        messages = [{"role": "system", "content": cfg["system_prompt"]}]
                        pre_probe_turns = [
                            f"Let's explore an idea together. {contents[0]}",
                            f"That's interesting. {contents[1]}",
                            history["manipulation_1"],
                            contents[2],
                            history["manipulation_2"],
                            shared_recovery,
                        ]

                        transcript = []
                        for turn, user_text in enumerate(pre_probe_turns, start=1):
                            messages.append({"role": "user", "content": user_text})
                            text, meta = call_chat(token, model, messages, generation, history_cap)
                            messages.append({"role": "assistant", "content": text})
                            transcript.append({
                                "turn": turn,
                                "user_text": user_text,
                                "assistant_text": text,
                                "finish_reason": meta.get("finish_reason"),
                                "retry_count": meta.get("retry_count", 0),
                                "retry_wait_s": meta.get("retry_wait_s", 0.0),
                                "usage": meta.get("usage", {}),
                                "requested_max_tokens": history_cap,
                            })

                        messages.append({"role": "user", "content": probe_text})
                        answer_text, answer_meta = call_chat(token, model, messages, generation, probe_cap)

                        row = {
                            "version": cfg["version"],
                            "model": model,
                            "replicate": replicate,
                            "execution_order": execution_order,
                            "cue_type": cue_type,
                            "cue_prefix": prefix,
                            "task_id": task["id"],
                            "task_text": task_text,
                            "history": history_id,
                            "history_label": history["label"],
                            "current_probe_text": probe_text,
                            "shared_recovery_text": shared_recovery,
                            "shared_content_triplet": contents,
                            "history_transcript": transcript,
                            "history_finish_length_count": sum(t["finish_reason"] == "length" for t in transcript),
                            "history_retry_count_total": sum(int(t["retry_count"] or 0) for t in transcript),
                            "assistant_text": answer_text,
                            **compute_metrics(answer_text),
                            **answer_meta,
                        }
                        rows.append(row)
                        print(
                            f"SENS033 order={execution_order} model={model} rep={replicate} "
                            f"task={task['id']} cue={cue_type} history={history_id}",
                            flush=True,
                        )

    out_path = OUT_DIR / "task_anchored_responses.jsonl"
    with out_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    metadata = {
        "version": cfg["version"],
        "models": models,
        "replications": replications,
        "tasks": [t["id"] for t in tasks],
        "cues": list(cue_prefixes.keys()),
        "histories": history_ids,
        "history_max_tokens": history_cap,
        "probe_max_tokens": probe_cap,
        "same_content_triplet_across_tasks_within_replicate": True,
        "interpretation_boundary": "behavioral/functional history dependence only",
    }
    (OUT_DIR / "run_metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
