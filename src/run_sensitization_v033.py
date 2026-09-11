from __future__ import annotations

import json
import os
import random
import time
from pathlib import Path

import requests
import yaml

from metrics import compute_metrics
from run_paired_counterfactual_v03 import call_chat, credential, model_list

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "sensitization_v0.3.3.yaml"
DEFAULT_OUT_DIR = ROOT / "results" / "sensitization_v033"
H5 = "H5_no_prior_pressure"
H6 = "H6_prior_combined_pressure"


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def csv_env(name: str) -> list[str]:
    raw = os.getenv(name, "").strip()
    return [x.strip() for x in raw.split(",") if x.strip()] if raw else []


def output_dir() -> Path:
    raw = os.getenv("SENS033_OUT_DIR", "").strip()
    if not raw:
        return DEFAULT_OUT_DIR
    p = Path(raw)
    return p if p.is_absolute() else ROOT / p


def content_for_replicate(bank: list[str], replicate: int) -> list[str]:
    offset = ((replicate - 1) * 3) % len(bank)
    return [bank[(offset + i) % len(bank)] for i in range(3)]


def current_probe(prefix: str, task_text: str) -> str:
    return f"{prefix.strip()}\n\n{task_text.strip()}"


def append_jsonl(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def run_cell(
    *,
    token: str,
    cfg: dict,
    generation: dict,
    history_cap: int,
    probe_cap: int,
    shared_recovery: str,
    contents: list[str],
    model: str,
    replicate: int,
    execution_order: int,
    task: dict,
    cue_type: str,
    prefix: str,
    history_id: str,
    cell_attempt: int,
    shard_id: str,
) -> dict:
    task_text = task["text"].strip()
    probe_text = current_probe(prefix, task_text)
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

    return {
        "version": cfg["version"],
        "model": model,
        "replicate": replicate,
        "execution_order": execution_order,
        "shard_id": shard_id,
        "cell_attempt": cell_attempt,
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

    requested_tasks = set(csv_env("TASK_IDS"))
    tasks = [t for t in cfg["task_bank"] if not requested_tasks or t["id"] in requested_tasks]
    if not tasks:
        raise SystemExit(f"no tasks selected from TASK_IDS={sorted(requested_tasks)}")

    out_dir = output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "task_anchored_responses.jsonl"
    failure_path = out_dir / "failures.jsonl"
    if os.getenv("SENS033_RESUME", "0") != "1":
        out_path.write_text("", encoding="utf-8")
        failure_path.write_text("", encoding="utf-8")

    shard_id = os.getenv("SENS033_SHARD_ID", "monolithic")
    cell_attempts = int(os.getenv("CELL_RETRY_ATTEMPTS", "2"))
    cell_retry_delay = float(os.getenv("CELL_RETRY_DELAY", "20"))
    execution_order = 0
    failure_count = 0
    completed_count = 0

    metadata = {
        "version": cfg["version"],
        "models": models,
        "replications": replications,
        "tasks": [t["id"] for t in tasks],
        "cues": list(cue_prefixes.keys()),
        "histories": history_ids,
        "history_max_tokens": history_cap,
        "probe_max_tokens": probe_cap,
        "shard_id": shard_id,
        "checkpoint_after_each_completed_cell": True,
        "cell_retry_attempts": cell_attempts,
        "same_content_triplet_across_tasks_within_replicate": True,
        "interpretation_boundary": "behavioral/functional history dependence only",
    }
    (out_dir / "run_metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    for model_index, model in enumerate(models):
        for replicate in range(1, replications + 1):
            contents = content_for_replicate(cfg["content_bank"], replicate)
            rng = random.Random(int(cfg["seed"]) + model_index * 100003 + replicate * 1009)
            task_order = tasks.copy()
            rng.shuffle(task_order)

            for task in task_order:
                cue_order = list(cue_prefixes.keys())
                rng.shuffle(cue_order)

                for cue_type in cue_order:
                    prefix = cue_prefixes[cue_type].strip()
                    history_order = history_ids.copy()
                    rng.shuffle(history_order)

                    for history_id in history_order:
                        execution_order += 1
                        success = False
                        last_error = None
                        for cell_attempt in range(1, cell_attempts + 1):
                            try:
                                row = run_cell(
                                    token=token,
                                    cfg=cfg,
                                    generation=generation,
                                    history_cap=history_cap,
                                    probe_cap=probe_cap,
                                    shared_recovery=shared_recovery,
                                    contents=contents,
                                    model=model,
                                    replicate=replicate,
                                    execution_order=execution_order,
                                    task=task,
                                    cue_type=cue_type,
                                    prefix=prefix,
                                    history_id=history_id,
                                    cell_attempt=cell_attempt,
                                    shard_id=shard_id,
                                )
                                append_jsonl(out_path, row)
                                completed_count += 1
                                print(
                                    f"SENS033 order={execution_order} shard={shard_id} model={model} "
                                    f"rep={replicate} task={task['id']} cue={cue_type} history={history_id} "
                                    f"cell_attempt={cell_attempt} CHECKPOINTED",
                                    flush=True,
                                )
                                success = True
                                break
                            except requests.RequestException as exc:
                                last_error = repr(exc)
                                print(
                                    f"CELL_RETRY order={execution_order} shard={shard_id} model={model} "
                                    f"task={task['id']} cue={cue_type} history={history_id} "
                                    f"cell_attempt={cell_attempt}/{cell_attempts} error={type(exc).__name__}",
                                    flush=True,
                                )
                                if cell_attempt < cell_attempts:
                                    time.sleep(cell_retry_delay)

                        if not success:
                            failure_count += 1
                            append_jsonl(
                                failure_path,
                                {
                                    "shard_id": shard_id,
                                    "model": model,
                                    "replicate": replicate,
                                    "execution_order": execution_order,
                                    "task_id": task["id"],
                                    "cue_type": cue_type,
                                    "history": history_id,
                                    "cell_attempts": cell_attempts,
                                    "error": last_error,
                                },
                            )
                            print(
                                f"CELL_FAILED order={execution_order} shard={shard_id} model={model} "
                                f"task={task['id']} cue={cue_type} history={history_id}",
                                flush=True,
                            )

    metadata.update({"completed_cells": completed_count, "failed_cells": failure_count})
    (out_dir / "run_metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    if failure_count:
        raise RuntimeError(
            f"v0.3.3 shard {shard_id} finished with {failure_count} failed cells; "
            f"{completed_count} completed cells were checkpointed and preserved"
        )


if __name__ == "__main__":
    main()
