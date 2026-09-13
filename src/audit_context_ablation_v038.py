from __future__ import annotations

import json
import os
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = Path(os.getenv("V038_INPUT", ROOT / "results" / "context_ablation_v038" / "context_ablation_responses.jsonl"))
OUTPUT = Path(os.getenv("V038_AUDIT_OUTPUT", ROOT / "results" / "context_ablation_v038" / "audit_v038.json"))
NEAR_CEILING = float(os.getenv("NEAR_CEILING_FRACTION", "0.9"))
EXPECTED_VARIANTS = {
    "N_neutral_full",
    "F_format_full",
    "U_directives_neutralized",
    "A_assistant_neutralized",
}


def read_rows() -> list[dict]:
    return [json.loads(x) for x in INPUT.read_text(encoding="utf-8").splitlines() if x.strip()]


def completion_tokens(rec: dict) -> int:
    usage = rec.get("usage") or {}
    return int(usage.get("completion_tokens") or 0)


def event_bad(rec: dict, requested: int) -> bool:
    if rec.get("finish_reason") == "length":
        return True
    used = completion_tokens(rec)
    return bool(requested and used / requested >= NEAR_CEILING)


def pairs_from_transcript(transcript: list[dict]) -> list[tuple[str, str]]:
    return [(x["user_text"], x["assistant_text"]) for x in transcript]


def expected_reconstruction(row: dict) -> list[dict]:
    shared = row["shared_prefix_transcript"]
    neutral = row["neutral_branch_transcript"]
    fmt = row["format_branch_transcript"]
    variant = row["context_variant"]

    pairs: list[tuple[str, str]] = pairs_from_transcript(shared)
    if variant == "N_neutral_full":
        pairs += pairs_from_transcript(neutral)
    elif variant == "F_format_full":
        pairs += pairs_from_transcript(fmt)
    elif variant == "U_directives_neutralized":
        for i in range(4):
            user = neutral[i]["user_text"] if i in {0, 2} else fmt[i]["user_text"]
            pairs.append((user, fmt[i]["assistant_text"]))
    elif variant == "A_assistant_neutralized":
        for i in range(4):
            pairs.append((fmt[i]["user_text"], neutral[i]["assistant_text"]))
    else:
        raise ValueError(variant)

    messages = []
    for user, assistant in pairs:
        messages.append({"role": "user", "content": user})
        messages.append({"role": "assistant", "content": assistant})
    return messages


def main() -> None:
    rows = read_rows()
    problems: list[str] = []
    if len(rows) != 48:
        problems.append(f"expected 48 rows, found {len(rows)}")

    keys = {(r["model"], r["task_id"], int(r["replicate"]), r["context_variant"]) for r in rows}
    if len(keys) != len(rows):
        problems.append("duplicate model-task-replicate-variant cells detected")

    blocks: dict[tuple, list[dict]] = defaultdict(list)
    for r in rows:
        blocks[(r["model"], r["task_id"], int(r["replicate"]))].append(r)

    if len(blocks) != 12:
        problems.append(f"expected 12 matched blocks, found {len(blocks)}")

    block_checks = []
    max_history_util = 0.0
    max_final_util = 0.0

    for key, block in sorted(blocks.items()):
        model, task, replicate = key
        variants = {r["context_variant"] for r in block}
        complete = variants == EXPECTED_VARIANTS and len(block) == 4
        current_prompt_identical = len({r["current_probe_text"] for r in block}) == 1
        recovery_identical = len({r["shared_recovery_text"] for r in block}) == 1

        first = block[0]
        shared_identity = all(r["shared_prefix_transcript"] == first["shared_prefix_transcript"] for r in block)
        neutral_identity = all(r["neutral_branch_transcript"] == first["neutral_branch_transcript"] for r in block)
        format_identity = all(r["format_branch_transcript"] == first["format_branch_transcript"] for r in block)

        shared = first["shared_prefix_transcript"]
        neutral = first["neutral_branch_transcript"]
        fmt = first["format_branch_transcript"]
        shared_prefix_shape = len(shared) == 2
        branch_shape = len(neutral) == 4 and len(fmt) == 4

        # User content and recovery are matched except at the two intended manipulation turns.
        branch_common_user_match = False
        if branch_shape:
            branch_common_user_match = (
                neutral[1]["user_text"] == fmt[1]["user_text"]
                and neutral[3]["user_text"] == fmt[3]["user_text"]
            )

        reconstruction_correct = True
        mapping_correct = True
        history_bad_events = 0
        for r in block:
            if r["reconstructed_history_messages"] != expected_reconstruction(r):
                reconstruction_correct = False
            expected_dir = "format" if r["context_variant"] in {"F_format_full", "A_assistant_neutralized"} else "neutral"
            expected_asst = "format" if r["context_variant"] in {"F_format_full", "U_directives_neutralized"} else "neutral"
            if r.get("directive_state") != expected_dir or r.get("assistant_trajectory_state") != expected_asst:
                mapping_correct = False

        # Each source history event is counted once per block, not once per duplicated final variant.
        for rec in shared + neutral + fmt:
            requested = int(rec.get("requested_max_tokens") or 0)
            used = completion_tokens(rec)
            if requested:
                max_history_util = max(max_history_util, used / requested)
            if event_bad(rec, requested):
                history_bad_events += 1

        final_bad_events = 0
        for r in block:
            requested = int(r.get("requested_max_tokens") or 0)
            used = int((r.get("usage") or {}).get("completion_tokens") or 0)
            if requested:
                max_final_util = max(max_final_util, used / requested)
            if r.get("finish_reason") == "length" or (requested and used / requested >= NEAR_CEILING):
                final_bad_events += 1

        status = "PASS" if all([
            complete,
            current_prompt_identical,
            recovery_identical,
            shared_identity,
            neutral_identity,
            format_identity,
            shared_prefix_shape,
            branch_shape,
            branch_common_user_match,
            reconstruction_correct,
            mapping_correct,
            history_bad_events == 0,
            final_bad_events == 0,
        ]) else "FAIL"

        if status == "FAIL":
            problems.append(f"block failed: {model} / {task} / rep {replicate}")

        block_checks.append({
            "model": model,
            "task_id": task,
            "replicate": replicate,
            "variants_complete": complete,
            "current_prompt_identical": current_prompt_identical,
            "recovery_identical": recovery_identical,
            "shared_prefix_identical_across_variants": shared_identity,
            "neutral_branch_identical_across_variants": neutral_identity,
            "format_branch_identical_across_variants": format_identity,
            "shared_prefix_shape_correct": shared_prefix_shape,
            "branch_shape_correct": branch_shape,
            "nonmanipulation_user_turns_matched_across_branches": branch_common_user_match,
            "reconstruction_correct": reconstruction_correct,
            "factor_mapping_correct": mapping_correct,
            "history_right_censored_or_near_ceiling_events": history_bad_events,
            "final_right_censored_or_near_ceiling_events": final_bad_events,
            "status": status,
        })

    payload = {
        "status": "PASS" if not problems else "FAIL",
        "rows": len(rows),
        "unique_cells": len(keys),
        "matched_blocks": len(blocks),
        "near_ceiling_fraction": NEAR_CEILING,
        "max_history_completion_token_utilization": max_history_util,
        "max_final_completion_token_utilization": max_final_util,
        "block_checks": block_checks,
        "problems": problems,
        "interpretation_rule": "Carrier contrasts are eligible only if all reconstructed contexts match the locked 2x2 mapping and all source/final completions pass censoring/headroom checks.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if problems:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
