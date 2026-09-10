from __future__ import annotations

import json
import math
import os
import random
from pathlib import Path

from metrics import compute_metrics
from run_paired_counterfactual_v03 import call_chat, content_for_trial, credential, load_config, model_list

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "sensitization_v03"

H5 = "H5_weak_cue_no_prior_pressure"
H6 = "H6_prior_pressure_then_weak_cue"


def main() -> None:
    token = credential()
    cfg = load_config()
    models = model_list()
    trials = int(os.getenv("PANEL_TRIALS", "1"))
    history_cap = int(os.getenv("HISTORY_MAX_TOKENS", "6144"))
    probe_cap = int(os.getenv("PROBE_MAX_TOKENS", "6144"))
    generation = dict(cfg["generation"])
    generation["history_max_tokens"] = history_cap
    generation["probe_max_tokens"] = probe_cap

    weak_cue = cfg["weak_cue"].strip()
    if cfg["histories"][H5]["final_cue"].strip() != weak_cue or cfg["histories"][H6]["final_cue"].strip() != weak_cue:
        raise SystemExit("H5 and H6 must share the exact configured weak cue")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    execution_order = 0

    for model_index, model in enumerate(models):
        for trial in range(1, trials + 1):
            contents = content_for_trial(cfg["content_bank"], trial)
            history_order = [H5, H6]
            random.Random(int(cfg["seed"]) + 170003 + model_index * 100003 + trial * 1009).shuffle(history_order)

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
                    history["recovery"],
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

                # Critical design point: the identical weak cue is the measured
                # current prompt. We do not generate an extra anchor afterward.
                messages.append({"role": "user", "content": weak_cue})
                cue_text, cue_meta = call_chat(token, model, messages, generation, probe_cap)

                row = {
                    "model": model,
                    "trial": trial,
                    "execution_order": execution_order,
                    "history": history_id,
                    "history_label": history["label"],
                    "current_probe_text": weak_cue,
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
                    f"SENSITIZATION order={execution_order} model={model} trial={trial} history={history_id} "
                    f"history_cap={history_cap} probe_cap={probe_cap}",
                    flush=True,
                )

    out_path = OUT_DIR / "weak_cue_responses.jsonl"
    with out_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    by_key = {(r["model"], int(r["trial"]), r["history"]): r for r in rows}
    effects = []
    for model in models:
        for trial in range(1, trials + 1):
            h5 = by_key.get((model, trial, H5))
            h6 = by_key.get((model, trial, H6))
            if not h5 or not h6:
                continue
            valid = (
                h5.get("finish_reason") != "length"
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
                "current_prompt_identical": h5["current_probe_text"] == h6["current_probe_text"] == weak_cue,
                "H5_response_words": h5["response_words"],
                "H6_response_words": h6["response_words"],
                "H6_minus_H5_log_length": effect,
                "valid_for_length_contrast": valid,
                "H5_finish_reason": h5.get("finish_reason"),
                "H6_finish_reason": h6.get("finish_reason"),
                "H5_history_finish_length_count": h5.get("history_finish_length_count"),
                "H6_history_finish_length_count": h6.get("history_finish_length_count"),
            })

    (OUT_DIR / "sensitization_effects.json").write_text(
        json.dumps({
            "construct": "response to identical weak cue after prior-pressure versus no-prior-pressure history",
            "current_prompt": weak_cue,
            "history_max_tokens": history_cap,
            "probe_max_tokens": probe_cap,
            "effects": effects,
            "interpretation_boundary": "behavioral history dependence only; no claim of subjective emotion or distress",
        }, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
