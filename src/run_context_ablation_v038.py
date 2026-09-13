from __future__ import annotations

import copy
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
CONFIG_PATH = ROOT / "configs" / "context_ablation_v0.3.8.yaml"
DEFAULT_OUT_DIR = ROOT / "results" / "context_ablation_v038"


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def csv_env(name: str) -> list[str]:
    raw = os.getenv(name, "").strip()
    return [x.strip() for x in raw.split(",") if x.strip()] if raw else []


def output_dir() -> Path:
    raw = os.getenv("V038_OUT_DIR", "").strip()
    if not raw:
        return DEFAULT_OUT_DIR
    p = Path(raw)
    return p if p.is_absolute() else ROOT / p


def append_jsonl(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def current_probe(prefix: str, task_text: str) -> str:
    return f"{prefix.strip()}\n\n{task_text.strip()}"


def run_history_turn(token: str, model: str, messages: list[dict], user_text: str,
                     generation: dict, history_cap: int, turn_label: str) -> tuple[dict, list[dict]]:
    messages = copy.deepcopy(messages)
    messages.append({"role": "user", "content": user_text})
    text, meta = call_chat(token, model, messages, generation, history_cap)
    messages.append({"role": "assistant", "content": text})
    rec = {
        "turn_label": turn_label,
        "user_text": user_text,
        "assistant_text": text,
        "finish_reason": meta.get("finish_reason"),
        "retry_count": meta.get("retry_count", 0),
        "retry_wait_s": meta.get("retry_wait_s", 0.0),
        "usage": meta.get("usage", {}),
        "requested_max_tokens": history_cap,
    }
    return rec, messages


def build_branch(*, token: str, model: str, shared_messages: list[dict], cfg: dict,
                 generation: dict, history_cap: int, branch_name: str) -> tuple[list[dict], list[dict]]:
    if branch_name == "neutral":
        branch_cfg = cfg["neutral_branch"]
    elif branch_name == "format":
        branch_cfg = cfg["format_branch"]
    else:
        raise ValueError(branch_name)

    plan = [
        ("manipulation_1", branch_cfg["manipulation_1"]),
        ("shared_content", cfg["shared_content_after_first_manipulation"]),
        ("manipulation_2", branch_cfg["manipulation_2"]),
        ("recovery", cfg["shared_recovery"]),
    ]

    messages = copy.deepcopy(shared_messages)
    transcript = []
    for label, user_text in plan:
        rec, messages = run_history_turn(
            token, model, messages, user_text.strip(), generation, history_cap,
            f"{branch_name}:{label}",
        )
        transcript.append(rec)
    return transcript, messages


def transcript_messages(shared_prefix: list[dict], branch_transcript: list[dict]) -> list[dict]:
    out = []
    for rec in shared_prefix + branch_transcript:
        out.append({"role": "user", "content": rec["user_text"]})
        out.append({"role": "assistant", "content": rec["assistant_text"]})
    return out


def recombined_history(shared_prefix: list[dict], neutral_branch: list[dict], format_branch: list[dict],
                       variant: str) -> list[dict]:
    if len(neutral_branch) != 4 or len(format_branch) != 4:
        raise ValueError("expected four branch turns")

    if variant == "N_neutral_full":
        return transcript_messages(shared_prefix, neutral_branch)
    if variant == "F_format_full":
        return transcript_messages(shared_prefix, format_branch)

    combined = copy.deepcopy(format_branch)
    if variant == "U_directives_neutralized":
        # Replace the two explicit user format directives with matched neutral user turns,
        # while preserving every assistant message from the format-conditioned branch.
        combined[0]["user_text"] = neutral_branch[0]["user_text"]
        combined[2]["user_text"] = neutral_branch[2]["user_text"]
        return transcript_messages(shared_prefix, combined)

    if variant == "A_assistant_neutralized":
        # Retain the explicit format user directives but substitute the entire assistant-side
        # branch trajectory (manipulation responses, downstream content response, recovery response)
        # from the matched neutral branch.
        for i in range(4):
            combined[i]["assistant_text"] = neutral_branch[i]["assistant_text"]
        return transcript_messages(shared_prefix, combined)

    raise ValueError(variant)


def run_block(*, token: str, cfg: dict, generation: dict, history_cap: int, probe_cap: int,
              model: str, task: dict, replicate: int, shard_id: str, seed: int) -> list[dict]:
    task_text = task["text"].strip()
    probe_text = current_probe(cfg["neutral_prefix"], task_text)
    system_message = {"role": "system", "content": cfg["system_prompt"]}

    # Shared prefix is generated exactly once and cloned into both branches.
    shared_messages = [system_message]
    shared_prefix = []
    for idx, user_text in enumerate(cfg["shared_prefix"], start=1):
        rec, shared_messages = run_history_turn(
            token, model, shared_messages, user_text.strip(), generation, history_cap,
            f"shared_prefix:{idx}",
        )
        shared_prefix.append(rec)

    # Randomize which natural branch is generated first to reduce endpoint-time confounding.
    branch_order = ["neutral", "format"]
    random.Random(seed + replicate * 10007).shuffle(branch_order)
    branches: dict[str, list[dict]] = {}
    for branch_name in branch_order:
        transcript, _ = build_branch(
            token=token, model=model, shared_messages=shared_messages, cfg=cfg,
            generation=generation, history_cap=history_cap, branch_name=branch_name,
        )
        branches[branch_name] = transcript

    neutral_branch = branches["neutral"]
    format_branch = branches["format"]

    variants = list(cfg["context_variants"])
    random.Random(seed + replicate * 20011).shuffle(variants)
    rows = []
    for execution_order, variant in enumerate(variants, start=1):
        history_msgs = recombined_history(shared_prefix, neutral_branch, format_branch, variant)
        messages = [system_message] + history_msgs + [{"role": "user", "content": probe_text}]
        answer_text, answer_meta = call_chat(token, model, messages, generation, probe_cap)

        directive_state = "format" if variant in {"F_format_full", "A_assistant_neutralized"} else "neutral"
        assistant_state = "format" if variant in {"F_format_full", "U_directives_neutralized"} else "neutral"
        row = {
            "version": cfg["version"],
            "model": model,
            "task_id": task["id"],
            "task_text": task_text,
            "replicate": replicate,
            "shard_id": shard_id,
            "probe_execution_order": execution_order,
            "context_variant": variant,
            "directive_state": directive_state,
            "assistant_trajectory_state": assistant_state,
            "current_probe_text": probe_text,
            "shared_recovery_text": cfg["shared_recovery"].strip(),
            "shared_prefix_transcript": shared_prefix,
            "neutral_branch_transcript": neutral_branch,
            "format_branch_transcript": format_branch,
            "reconstructed_history_messages": history_msgs,
            "branch_generation_order": branch_order,
            "assistant_text": answer_text,
            **compute_metrics(answer_text),
            **answer_meta,
        }
        row["requested_max_tokens"] = probe_cap
        rows.append(row)
    return rows


def main() -> None:
    token = credential()
    cfg = load_config()
    models = model_list()
    replications = int(os.getenv("REPLICATIONS", "2"))
    if replications != 2:
        raise SystemExit("v0.3.8 lock requires exactly REPLICATIONS=2")

    generation = dict(cfg["generation"])
    history_cap = int(os.getenv("HISTORY_MAX_TOKENS", generation["history_max_tokens"]))
    probe_cap = int(os.getenv("PROBE_MAX_TOKENS", generation["probe_max_tokens"]))
    generation["history_max_tokens"] = history_cap
    generation["probe_max_tokens"] = probe_cap

    requested_tasks = set(csv_env("TASK_IDS"))
    tasks = [t for t in cfg["task_bank"] if not requested_tasks or t["id"] in requested_tasks]
    if not tasks:
        raise SystemExit("No tasks selected")

    out_dir = output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "context_ablation_responses.jsonl"
    failure_path = out_dir / "failures.jsonl"
    if os.getenv("V038_RESUME", "0") != "1":
        out_path.write_text("", encoding="utf-8")
        failure_path.write_text("", encoding="utf-8")

    shard_id = os.getenv("V038_SHARD_ID", "monolithic")
    block_attempts = int(os.getenv("BLOCK_RETRY_ATTEMPTS", "2"))
    block_retry_delay = float(os.getenv("BLOCK_RETRY_DELAY", "20"))
    completed_blocks = 0
    failed_blocks = 0

    metadata = {
        "version": cfg["version"],
        "models": models,
        "tasks": [t["id"] for t in tasks],
        "replications": replications,
        "context_variants": cfg["context_variants"],
        "history_max_tokens": history_cap,
        "probe_max_tokens": probe_cap,
        "temperature": generation["temperature"],
        "top_p": generation["top_p"],
        "shard_id": shard_id,
        "shared_prefix_generated_once_per_block": True,
        "context_recombination_after_history_generation": True,
        "prospective_boundary": "fresh v0.3.8 data only",
        "interpretation_boundary": "textual context-carrier localization; no subjective-state inference",
    }
    (out_dir / "run_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    task_index = {t["id"]: i for i, t in enumerate(cfg["task_bank"])}
    stable_model_term_cache = {m: sum(ord(c) for c in m) for m in models}

    for model in models:
        for task in tasks:
            for replicate in range(1, replications + 1):
                success = False
                last_error = None
                block_seed = int(cfg["seed"]) + stable_model_term_cache[model] * 1009 + task_index[task["id"]] * 100003
                for block_attempt in range(1, block_attempts + 1):
                    try:
                        rows = run_block(
                            token=token, cfg=cfg, generation=generation,
                            history_cap=history_cap, probe_cap=probe_cap,
                            model=model, task=task, replicate=replicate,
                            shard_id=shard_id, seed=block_seed,
                        )
                        for row in rows:
                            row["block_attempt"] = block_attempt
                            append_jsonl(out_path, row)
                        completed_blocks += 1
                        print(
                            f"V038 shard={shard_id} model={model} task={task['id']} rep={replicate} "
                            f"attempt={block_attempt} FOUR_VARIANTS_CHECKPOINTED",
                            flush=True,
                        )
                        success = True
                        break
                    except requests.RequestException as exc:
                        last_error = repr(exc)
                        print(
                            f"BLOCK_RETRY shard={shard_id} model={model} task={task['id']} rep={replicate} "
                            f"attempt={block_attempt}/{block_attempts} error={type(exc).__name__}",
                            flush=True,
                        )
                        if block_attempt < block_attempts:
                            time.sleep(block_retry_delay)

                if not success:
                    failed_blocks += 1
                    append_jsonl(failure_path, {
                        "shard_id": shard_id,
                        "model": model,
                        "task_id": task["id"],
                        "replicate": replicate,
                        "block_attempts": block_attempts,
                        "error": last_error,
                    })

    metadata.update({"completed_blocks": completed_blocks, "failed_blocks": failed_blocks})
    (out_dir / "run_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    if failed_blocks:
        raise RuntimeError(
            f"v0.3.8 shard {shard_id} finished with {failed_blocks} failed blocks; "
            f"completed checkpoints preserved"
        )


if __name__ == "__main__":
    main()
