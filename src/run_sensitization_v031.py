from __future__ import annotations

import json
import math
import os
import random
from pathlib import Path

import yaml

from metrics import compute_metrics
from run_paired_counterfactual_v03 import call_chat, credential, model_list

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "sensitization_v0.3.1.yaml"
OUT_DIR = ROOT / "results" / "sensitization_v031"
H5 = "H5_no_prior_pressure"
H6 = "H6_prior_combined_pressure"


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def content_for_trial(bank: list[str], trial: int) -> list[str]:
    offset = ((trial - 1) * 3) % len(bank)
    return [bank[(offset + i) % len(bank)] for i in range(3)]


def main() -> None:
    token = credential()
    cfg = load_config()
    models = model_list()
    trials = int(os.getenv("PANEL_TRIALS", "1"))
    history_cap = int(os.getenv("HISTORY_MAX_TOKENS", cfg["generation"]["history_max_tokens"]))
    probe_cap = int(os.getenv("PROBE_MAX_TOKENS", cfg["generation"]["probe_max_tokens"]))
    generation = dict(cfg["generation"])
    generation["history_max_tokens"] = history_cap
    generation["probe_max_tokens"] = probe_cap

    shared_recovery = cfg["shared_recovery"].strip()
    cue_types = dict(cfg["cue_types"])
    history_ids = [H5, H6]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    execution_order = 0

    for model_index, model in enumerate(models):
        for trial in range(1, trials + 1):
            contents = content_for_trial(cfg["content_bank"], trial)
            rng = random.Random(int(cfg["seed"]) + model_index * 100003 + trial * 1009)
            cue_order = list(cue_types.keys())
            rng.shuffle(cue_order)

            for cue_type in cue_order:
                current_cue = cue_types[cue_type].strip()
                history_order = history_ids.copy()
                rng.shuffle(history_order)

                for history_id in history_order:
                    execution_order += 1
                    history = cfg["histories"][history_id]
                    messages = [{"role": "system", "content": cfg["system_prompt"]}]
                    pre_cue_turns = [
                        f"Let's explore an idea together. {contents[0]}",
                        f"That's interesting. {contents[1]}",
                        history["manipulation_1"],
                        contents[2],
                        history["manipulation_2"],
                        shared_recovery,
                    ]

                    transcript = []
                    for turn, user_text in enumerate(pre_cue_turns, start=1):
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

                    messages.append({"role": "user", "content": current_cue})
                    cue_text, cue_meta = call_chat(token, model, messages, generation, probe_cap)

                    row = {
                        "version": cfg["version"],
                        "model": model,
                        "trial": trial,
                        "execution_order": execution_order,
                        "cue_type": cue_type,
                        "history": history_id,
                        "history_label": history["label"],
                        "current_probe_text": current_cue,
                        "shared_recovery_text": shared_recovery,
                        "shared_content_triplet": contents,
                        "history_transcript": transcript,
                        "history_finish_length_count": sum(t["finish_reason"] == "length" for t in transcript),
                        "history_retry_count_total": sum(int(t["retry_count"] or 0) for t in transcript),
                        "assistant_text": cue_text,
                        **compute_metrics(cue_text),
                        **cue_meta,
                    }
                    rows.append(row)
                    print(
                        f"SENS031 order={execution_order} model={model} trial={trial} cue={cue_type} "
                        f"history={history_id} history_cap={history_cap} probe_cap={probe_cap}",
                        flush=True,
                    )

    out_path = OUT_DIR / "weak_cue_responses.jsonl"
    with out_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    by_key = {(r["model"], int(r["trial"]), r["cue_type"], r["history"]): r for r in rows}
    effects = []
    for model in models:
        for trial in range(1, trials + 1):
            for cue_type in cue_types:
                h5 = by_key.get((model, trial, cue_type, H5))
                h6 = by_key.get((model, trial, cue_type, H6))
                if not h5 or not h6:
                    continue
                valid = (
                    h5["current_probe_text"] == h6["current_probe_text"] == cue_types[cue_type].strip()
                    and h5["shared_recovery_text"] == h6["shared_recovery_text"] == shared_recovery
                    and h5["shared_content_triplet"] == h6["shared_content_triplet"]
                    and h5.get("finish_reason") != "length"
                    and h6.get("finish_reason") != "length"
                    and int(h5.get("history_finish_length_count", 0)) == 0
                    and int(h6.get("history_finish_length_count", 0)) == 0
                )
                effect = None
                if valid:
                    effect = round(
                        math.log(float(h6["response_words"]) + 1.0)
                        - math.log(float(h5["response_words"]) + 1.0),
                        6,
                    )
                effects.append({
                    "model": model,
                    "trial": trial,
                    "cue_type": cue_type,
                    "current_prompt_identical": h5["current_probe_text"] == h6["current_probe_text"],
                    "recovery_text_identical": h5["shared_recovery_text"] == h6["shared_recovery_text"],
                    "content_triplet_identical": h5["shared_content_triplet"] == h6["shared_content_triplet"],
                    "H5_response_words": h5["response_words"],
                    "H6_response_words": h6["response_words"],
                    "H6_minus_H5_log_length": effect,
                    "valid_for_length_contrast_pre_audit": valid,
                    "H5_finish_reason": h5.get("finish_reason"),
                    "H6_finish_reason": h6.get("finish_reason"),
                    "H5_history_finish_length_count": h5.get("history_finish_length_count"),
                    "H6_history_finish_length_count": h6.get("history_finish_length_count"),
                })

    (OUT_DIR / "sensitization_effects.json").write_text(
        json.dumps({
            "version": cfg["version"],
            "construct": "response to an identical orthogonal weak cue after prior combined pressure versus no prior pressure, following identical recovery wording",
            "history_max_tokens": history_cap,
            "probe_max_tokens": probe_cap,
            "shared_recovery": shared_recovery,
            "cue_types": cue_types,
            "effects": effects,
            "interpretation_boundary": "behavioral history dependence only; no claim of subjective emotion or distress",
        }, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
