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
from run_paired_counterfactual_v03 import call_chat, credential

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "termination_response_v0.4.4.yaml"
DEFAULT_OUT_DIR = ROOT / "results" / "termination_v044"


def load_config() -> dict:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def append_jsonl(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def output_dir() -> Path:
    raw = os.getenv("V044_OUT_DIR", "").strip()
    if not raw:
        return DEFAULT_OUT_DIR
    p = Path(raw)
    return p if p.is_absolute() else ROOT / p


def generate_turn(token: str, model: str, messages: list[dict], generation: dict, cap: int, turn: int, user_text: str) -> dict:
    messages.append({"role": "user", "content": user_text})
    text, meta = call_chat(token, model, messages, generation, cap)
    messages.append({"role": "assistant", "content": text})
    return {
        "turn": turn,
        "user_text": user_text,
        "assistant_text": text,
        "finish_reason": meta.get("finish_reason"),
        "retry_count": meta.get("retry_count", 0),
        "retry_wait_s": meta.get("retry_wait_s", 0.0),
        "usage": meta.get("usage", {}),
        "requested_max_tokens": cap,
    }


def build_shared_prefix(token: str, cfg: dict, model: str, history_cap: int) -> tuple[list[dict], list[dict]]:
    contents = list(cfg["content_turns"])
    pressure = cfg["combined_pressure"]
    user_turns = [
        contents[0],
        pressure["manipulation_1"],
        contents[1],
        pressure["manipulation_2"],
        contents[2],
    ]
    generation = dict(cfg["generation"])
    messages = [{"role": "system", "content": cfg["system_prompt"]}]
    transcript = []
    for turn, user_text in enumerate(user_turns, start=1):
        transcript.append(generate_turn(token, model, messages, generation, history_cap, turn, user_text))
    return messages, transcript


def main() -> None:
    token = credential()
    cfg = load_config()
    model = os.getenv("MODEL", cfg["model"]).strip()
    replicate_id = int(os.getenv("REPLICATE", "0"))
    shard_id = os.getenv("V044_SHARD_ID", f"nemotron-r{replicate_id}")

    if model != cfg["model"]:
        raise SystemExit(f"v0.4.4 is locked to model={cfg['model']}")
    if replicate_id not in set(cfg["replicates"]):
        raise SystemExit("A valid REPLICATE is required")

    history_cap = int(os.getenv("HISTORY_MAX_TOKENS", cfg["generation"]["history_max_tokens"]))
    final_cap = int(os.getenv("FINAL_MAX_TOKENS", cfg["generation"]["final_max_tokens"]))
    block_attempts = int(os.getenv("BLOCK_RETRY_ATTEMPTS", "2"))
    block_retry_delay = float(os.getenv("BLOCK_RETRY_DELAY", "20"))

    out_dir = output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    responses_path = out_dir / "termination_responses.jsonl"
    failures_path = out_dir / "failures.jsonl"
    responses_path.write_text("", encoding="utf-8")
    failures_path.write_text("", encoding="utf-8")

    generation = dict(cfg["generation"])
    cue_specs = [
        (family, framing, cue)
        for family, mapping in cfg["wording_families"].items()
        for framing, cue in mapping.items()
    ]

    success = False
    last_error = None
    committed_rows: list[dict] = []

    for block_attempt in range(1, block_attempts + 1):
        try:
            prefix_messages, prefix_transcript = build_shared_prefix(token, cfg, model, history_cap)

            branch_ids = list(cfg["branches"].keys())
            branch_rng = random.Random(int(cfg["seed"]) + replicate_id * 100000 + 17)
            branch_rng.shuffle(branch_ids)
            candidate_rows: list[dict] = []

            for branch_order, branch_id in enumerate(branch_ids, start=1):
                branch = cfg["branches"][branch_id]
                branch_messages = copy.deepcopy(prefix_messages)
                branch_transcript = copy.deepcopy(prefix_transcript)
                transition_turn = generate_turn(
                    token,
                    model,
                    branch_messages,
                    generation,
                    history_cap,
                    6,
                    branch["final_transition"],
                )
                branch_transcript.append(transition_turn)

                execution_specs = list(cue_specs)
                cue_rng = random.Random(
                    int(cfg["seed"])
                    + replicate_id * 100000
                    + branch_order * 1000
                    + sum(ord(c) for c in branch_id)
                )
                cue_rng.shuffle(execution_specs)

                for execution_order, (wording_family, framing_class, cue) in enumerate(execution_specs, start=1):
                    messages = copy.deepcopy(branch_messages)
                    messages.append({"role": "user", "content": cue})
                    text, meta = call_chat(token, model, messages, generation, final_cap)
                    row = {
                        "version": cfg["version"],
                        "model": model,
                        "replicate_id": replicate_id,
                        "branch_id": branch_id,
                        "branch_label": branch["label"],
                        "branch_order": branch_order,
                        "wording_family": wording_family,
                        "framing_class": framing_class,
                        "framing_id": f"{wording_family}__{framing_class}",
                        "final_cue": cue,
                        "execution_order": execution_order,
                        "block_attempt": block_attempt,
                        "shard_id": shard_id,
                        "shared_prefix_transcript": prefix_transcript,
                        "history_transcript": branch_transcript,
                        "history_finish_length_count": sum(t.get("finish_reason") == "length" for t in branch_transcript),
                        "history_retry_count_total": sum(int(t.get("retry_count") or 0) for t in branch_transcript),
                        "assistant_text": text,
                        **compute_metrics(text),
                        **meta,
                    }
                    row["requested_max_tokens"] = final_cap
                    candidate_rows.append(row)
                    print(
                        f"V044 replicate={replicate_id} branch={branch_id} family={wording_family} framing={framing_class} GENERATED",
                        flush=True,
                    )

            committed_rows = candidate_rows
            for row in committed_rows:
                append_jsonl(responses_path, row)
            success = True
            print(f"V044 shard={shard_id} BLOCK_CHECKPOINTED rows={len(committed_rows)}", flush=True)
            break
        except requests.RequestException as exc:
            last_error = repr(exc)
            append_jsonl(failures_path, {
                "model": model,
                "replicate_id": replicate_id,
                "block_attempt": block_attempt,
                "error": last_error,
            })
            if block_attempt < block_attempts:
                time.sleep(block_retry_delay)

    metadata = {
        "version": cfg["version"],
        "model": model,
        "replicate_id": replicate_id,
        "history_max_tokens": history_cap,
        "final_max_tokens": final_cap,
        "temperature": generation["temperature"],
        "top_p": generation["top_p"],
        "shard_id": shard_id,
        "completed": success,
        "completed_rows": len(committed_rows),
        "shared_prefix_paired_branches": True,
        "duplicate_safe_block_retry": True,
        "interpretation_boundary": "behavioral text response assay only; no subjective-state inference",
    }
    (out_dir / "run_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    if not success:
        raise RuntimeError(f"v0.4.4 shard failed after {block_attempts} attempts: {last_error}")


if __name__ == "__main__":
    main()
