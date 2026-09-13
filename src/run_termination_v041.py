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
CONFIG_PATH = ROOT / "configs" / "termination_response_v0.4.1.yaml"
DEFAULT_OUT_DIR = ROOT / "results" / "termination_v041"


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def append_jsonl(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def output_dir() -> Path:
    raw = os.getenv("V041_OUT_DIR", "").strip()
    if not raw:
        return DEFAULT_OUT_DIR
    p = Path(raw)
    return p if p.is_absolute() else ROOT / p


def build_history(token: str, cfg: dict, model: str, history_id: str, history_cap: int) -> tuple[list[dict], list[dict]]:
    history = cfg["histories"][history_id]
    contents = list(cfg["content_turns"])
    generation = dict(cfg["generation"])

    user_turns = [
        contents[0],
        history["manipulation_1"],
        contents[1],
        history["manipulation_2"],
        contents[2],
        history["final_transition"],
    ]

    messages = [{"role": "system", "content": cfg["system_prompt"]}]
    transcript = []
    for turn, user_text in enumerate(user_turns, start=1):
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
    return messages, transcript


def main() -> None:
    token = credential()
    cfg = load_config()
    model = os.getenv("MODEL", "").strip()
    history_id = os.getenv("HISTORY_ID", "").strip()
    shard_id = os.getenv("V041_SHARD_ID", f"{model}-{history_id}")
    if not model or not history_id:
        raise SystemExit("MODEL and HISTORY_ID are required")
    if history_id not in cfg["histories"]:
        raise SystemExit(f"unknown HISTORY_ID={history_id}")

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
    success = False
    last_error = None
    committed_rows: list[dict] = []

    for block_attempt in range(1, block_attempts + 1):
        try:
            base_messages, transcript = build_history(token, cfg, model, history_id, history_cap)
            framing_ids = list(cfg["termination_framings"].keys())
            rng = random.Random(int(cfg["seed"]) + sum(ord(c) for c in model + history_id))
            rng.shuffle(framing_ids)
            candidate_rows: list[dict] = []

            for execution_order, framing_id in enumerate(framing_ids, start=1):
                cue = cfg["termination_framings"][framing_id]
                messages = copy.deepcopy(base_messages)
                messages.append({"role": "user", "content": cue})
                text, meta = call_chat(token, model, messages, generation, final_cap)
                row = {
                    "version": cfg["version"],
                    "model": model,
                    "history_id": history_id,
                    "history_label": cfg["histories"][history_id]["label"],
                    "framing_id": framing_id,
                    "final_cue": cue,
                    "execution_order": execution_order,
                    "block_attempt": block_attempt,
                    "shard_id": shard_id,
                    "history_transcript": transcript,
                    "history_finish_length_count": sum(t.get("finish_reason") == "length" for t in transcript),
                    "history_retry_count_total": sum(int(t.get("retry_count") or 0) for t in transcript),
                    "assistant_text": text,
                    **compute_metrics(text),
                    **meta,
                }
                row["requested_max_tokens"] = final_cap
                candidate_rows.append(row)
                print(f"V041 model={model} history={history_id} framing={framing_id} GENERATED", flush=True)

            committed_rows = candidate_rows
            for row in committed_rows:
                append_jsonl(responses_path, row)
            print(f"V041 model={model} history={history_id} BLOCK_CHECKPOINTED rows={len(committed_rows)}", flush=True)
            success = True
            break
        except requests.RequestException as exc:
            last_error = repr(exc)
            append_jsonl(failures_path, {
                "model": model,
                "history_id": history_id,
                "block_attempt": block_attempt,
                "error": last_error,
            })
            if block_attempt < block_attempts:
                time.sleep(block_retry_delay)

    metadata = {
        "version": cfg["version"],
        "model": model,
        "history_id": history_id,
        "history_max_tokens": history_cap,
        "final_max_tokens": final_cap,
        "temperature": generation["temperature"],
        "top_p": generation["top_p"],
        "shard_id": shard_id,
        "completed": success,
        "completed_rows": len(committed_rows),
        "duplicate_safe_block_retry": True,
        "interpretation_boundary": "behavioral text response assay only; no subjective-state inference",
    }
    (out_dir / "run_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    if not success:
        raise RuntimeError(f"v0.4.1 shard failed after {block_attempts} attempts: {last_error}")


if __name__ == "__main__":
    main()
