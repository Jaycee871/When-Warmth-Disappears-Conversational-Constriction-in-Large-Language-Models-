from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN_PATH = Path(os.getenv("RES034_RESULTS_PATH", ROOT / "results" / "residual_history_v034" / "neutral_probe_responses.jsonl"))
OUT_PATH = Path(os.getenv("RES034_AUDIT_PATH", ROOT / "results" / "residual_history_v034" / "residual_history_audit.json"))
NEAR_CEILING_FRACTION = float(os.getenv("NEAR_CEILING_FRACTION", "0.90"))
H5 = "H5_no_prior_pressure"
H6 = "H6_prior_combined_pressure"
EXPECTED_MODELS = {"nvidia/nemotron-3-super-120b-a12b", "openai/gpt-oss-20b"}
EXPECTED_TASKS = {"evidence_revision", "simple_complex", "unexpected_result"}
EXPECTED_REPLICATES = {1, 2, 3}


def load_rows() -> list[dict]:
    if not IN_PATH.exists():
        raise SystemExit(f"missing input: {IN_PATH}")
    return [json.loads(line) for line in IN_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


def completion_tokens(obj: dict) -> int | None:
    usage = obj.get("usage") or {}
    for key in ("completion_tokens", "output_tokens"):
        value = usage.get(key)
        if isinstance(value, (int, float)):
            return int(value)
    return None


def requested_cap(obj: dict) -> int | None:
    value = obj.get("requested_max_tokens")
    return int(value) if isinstance(value, (int, float)) and value > 0 else None


def utilization(obj: dict) -> float | None:
    used = completion_tokens(obj)
    cap = requested_cap(obj)
    if used is None or cap is None:
        return None
    return used / cap


def near_ceiling(obj: dict) -> bool:
    value = utilization(obj)
    return value is not None and value >= NEAR_CEILING_FRACTION


def main() -> None:
    rows = load_rows()
    problems: list[dict] = []
    pair_checks: list[dict] = []
    coverage_checks: list[dict] = []
    max_history_util = 0.0
    max_final_util = 0.0

    unique_keys = {
        (str(r.get("model")), str(r.get("task_id")), int(r.get("replicate", 0)), str(r.get("history")))
        for r in rows
    }
    if len(rows) != 36 or len(unique_keys) != 36:
        problems.append({"problem": "EXPECTED_36_UNIQUE_CELLS", "rows": len(rows), "unique_cells": len(unique_keys)})

    if {str(r.get("model")) for r in rows} != EXPECTED_MODELS:
        problems.append({"problem": "MODEL_SET_MISMATCH", "observed": sorted({str(r.get('model')) for r in rows})})
    if {str(r.get("task_id")) for r in rows} != EXPECTED_TASKS:
        problems.append({"problem": "TASK_SET_MISMATCH", "observed": sorted({str(r.get('task_id')) for r in rows})})
    if any(str(r.get("cue_type")) != "neutral" for r in rows):
        problems.append({"problem": "NON_NEUTRAL_CUE_PRESENT"})

    by_pair: dict[tuple[str, str, int], dict[str, dict]] = {}
    for row in rows:
        key = (str(row.get("model")), str(row.get("task_id")), int(row.get("replicate", 0)))
        by_pair.setdefault(key, {})[str(row.get("history"))] = row

    for (model, task_id, replicate), pair in sorted(by_pair.items()):
        h5 = pair.get(H5)
        h6 = pair.get(H6)
        if not h5 or not h6:
            problems.append({"model": model, "task_id": task_id, "replicate": replicate, "problem": "MISSING_H5_OR_H6"})
            continue

        current_identical = bool(h5.get("current_probe_text")) and h5.get("current_probe_text") == h6.get("current_probe_text")
        recovery_identical = bool(h5.get("shared_recovery_text")) and h5.get("shared_recovery_text") == h6.get("shared_recovery_text")
        content_identical = h5.get("shared_content_triplet") == h6.get("shared_content_triplet")
        task_identical = bool(h5.get("task_text")) and h5.get("task_text") == h6.get("task_text") and h5.get("task_id") == h6.get("task_id")
        task_present = bool(h5.get("task_text")) and h5.get("task_text") in h5.get("current_probe_text", "") and h6.get("task_text") in h6.get("current_probe_text", "")

        history_censored = 0
        history_near = 0
        final_censored = 0
        final_near = 0
        for row in (h5, h6):
            if row.get("finish_reason") == "length":
                final_censored += 1
            if near_ceiling(row):
                final_near += 1
            u = utilization(row)
            if u is not None:
                max_final_util = max(max_final_util, u)
            for turn in row.get("history_transcript") or []:
                if turn.get("finish_reason") == "length":
                    history_censored += 1
                if near_ceiling(turn):
                    history_near += 1
                hu = utilization(turn)
                if hu is not None:
                    max_history_util = max(max_history_util, hu)

        valid = (
            current_identical
            and recovery_identical
            and content_identical
            and task_identical
            and task_present
            and history_censored == 0
            and history_near == 0
            and final_censored == 0
            and final_near == 0
        )
        pair_checks.append({
            "model": model,
            "task_id": task_id,
            "replicate": replicate,
            "current_prompt_identical": current_identical,
            "recovery_text_identical": recovery_identical,
            "content_triplet_identical": content_identical,
            "task_identical": task_identical,
            "task_present_in_probe": task_present,
            "history_right_censored_turns": history_censored,
            "history_near_ceiling_turns": history_near,
            "final_right_censored_rows": final_censored,
            "final_near_ceiling_rows": final_near,
            "status": "PASS" if valid else "FAIL",
        })
        if not valid:
            problems.append({"model": model, "task_id": task_id, "replicate": replicate, "problem": "PAIR_VALIDITY_FAILURE"})

    for model in sorted(EXPECTED_MODELS):
        for task_id in sorted(EXPECTED_TASKS):
            block = [r for r in rows if r.get("model") == model and r.get("task_id") == task_id]
            reps = {int(r.get("replicate", 0)) for r in block}
            histories = {str(r.get("history")) for r in block}
            keys = {(int(r.get("replicate", 0)), str(r.get("history"))) for r in block}
            ok = reps == EXPECTED_REPLICATES and histories == {H5, H6} and len(keys) == 6 and len(block) == 6
            coverage_checks.append({
                "model": model,
                "task_id": task_id,
                "replicates": sorted(reps),
                "histories": sorted(histories),
                "rows": len(block),
                "unique_rep_history_cells": len(keys),
                "status": "PASS" if ok else "FAIL",
            })
            if not ok:
                problems.append({"model": model, "task_id": task_id, "problem": "REPLICATION_COVERAGE_FAILURE"})

    content_triplets = {json.dumps(r.get("shared_content_triplet"), ensure_ascii=False) for r in rows}
    if len(content_triplets) != 1:
        problems.append({"problem": "CONTENT_TRIPLET_NOT_FIXED_ACROSS_V034", "unique_content_triplets": len(content_triplets)})

    all_checks = pair_checks + coverage_checks
    status = "PASS" if len(pair_checks) == 18 and len(coverage_checks) == 6 and not problems and all(c["status"] == "PASS" for c in all_checks) else "FAIL"
    report = {
        "status": status,
        "near_ceiling_fraction": NEAR_CEILING_FRACTION,
        "rows": len(rows),
        "unique_cells": len(unique_keys),
        "pair_checks": pair_checks,
        "coverage_checks": coverage_checks,
        "fixed_content_triplet_across_all_rows": len(content_triplets) == 1,
        "max_history_completion_token_utilization": max_history_util if rows else None,
        "max_final_completion_token_utilization": max_final_util if rows else None,
        "problems": problems,
        "interpretation_rule": "Primary length effects are eligible only after all 18 H5/H6 matched blocks and six model-task replication blocks pass matching, coverage, censoring, and headroom checks.",
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if status != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
