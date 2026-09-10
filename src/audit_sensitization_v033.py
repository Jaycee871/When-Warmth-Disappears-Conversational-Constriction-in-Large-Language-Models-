from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN_PATH = Path(os.getenv("SENS033_RESULTS_PATH", ROOT / "results" / "sensitization_v033" / "task_anchored_responses.jsonl"))
OUT_PATH = Path(os.getenv("SENS033_AUDIT_PATH", ROOT / "results" / "sensitization_v033" / "sensitization_audit.json"))
NEAR_CEILING_FRACTION = float(os.getenv("NEAR_CEILING_FRACTION", "0.90"))
H5 = "H5_no_prior_pressure"
H6 = "H6_prior_combined_pressure"
EXPECTED_CUES = {"neutral", "format_only", "evaluation_only"}
EXPECTED_TASKS = {"evidence_revision", "simple_complex", "unexpected_result"}


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
    u = utilization(obj)
    return u is not None and u >= NEAR_CEILING_FRACTION


def main() -> None:
    rows = load_rows()
    problems: list[dict] = []
    pair_checks: list[dict] = []
    cross_cue_checks: list[dict] = []
    cross_task_checks: list[dict] = []
    max_history_util = 0.0
    max_final_util = 0.0

    by_pair: dict[tuple[str, int, str, str], dict[str, dict]] = {}
    for row in rows:
        key = (
            str(row.get("model")),
            int(row.get("replicate", 0)),
            str(row.get("task_id")),
            str(row.get("cue_type")),
        )
        by_pair.setdefault(key, {})[str(row.get("history"))] = row

    for (model, replicate, task_id, cue_type), pair in sorted(by_pair.items()):
        h5 = pair.get(H5)
        h6 = pair.get(H6)
        if not h5 or not h6:
            problems.append({"model": model, "replicate": replicate, "task_id": task_id, "cue_type": cue_type, "problem": "MISSING_H5_OR_H6"})
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
            current_identical and recovery_identical and content_identical and task_identical and task_present
            and history_censored == 0 and history_near == 0 and final_censored == 0 and final_near == 0
        )
        pair_checks.append({
            "model": model,
            "replicate": replicate,
            "task_id": task_id,
            "cue_type": cue_type,
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
            problems.append({"model": model, "replicate": replicate, "task_id": task_id, "cue_type": cue_type, "problem": "PAIR_VALIDITY_FAILURE"})

    blocks: dict[tuple[str, int, str], list[dict]] = {}
    for row in rows:
        blocks.setdefault((str(row.get("model")), int(row.get("replicate", 0)), str(row.get("task_id"))), []).append(row)
    for (model, replicate, task_id), block in sorted(blocks.items()):
        cues = {str(r.get("cue_type")) for r in block}
        histories = {str(r.get("history")) for r in block}
        task_texts = {str(r.get("task_text")) for r in block}
        ok = cues == EXPECTED_CUES and histories == {H5, H6} and len(task_texts) == 1
        cross_cue_checks.append({
            "model": model,
            "replicate": replicate,
            "task_id": task_id,
            "observed_cues": sorted(cues),
            "observed_histories": sorted(histories),
            "unique_task_text_count": len(task_texts),
            "status": "PASS" if ok else "FAIL",
        })
        if not ok:
            problems.append({"model": model, "replicate": replicate, "task_id": task_id, "problem": "CROSS_CUE_CELL_MISMATCH"})

    repl_blocks: dict[tuple[str, int], list[dict]] = {}
    for row in rows:
        repl_blocks.setdefault((str(row.get("model")), int(row.get("replicate", 0))), []).append(row)
    for (model, replicate), block in sorted(repl_blocks.items()):
        tasks = {str(r.get("task_id")) for r in block}
        content_triplets = {json.dumps(r.get("shared_content_triplet"), sort_keys=True) for r in block}
        ok = tasks == EXPECTED_TASKS and len(content_triplets) == 1
        cross_task_checks.append({
            "model": model,
            "replicate": replicate,
            "observed_tasks": sorted(tasks),
            "unique_content_triplet_count": len(content_triplets),
            "status": "PASS" if ok else "FAIL",
        })
        if not ok:
            problems.append({"model": model, "replicate": replicate, "problem": "CROSS_TASK_CONTENT_OR_TASK_MISMATCH"})

    all_checks = pair_checks + cross_cue_checks + cross_task_checks
    status = "PASS" if all_checks and not problems and all(c["status"] == "PASS" for c in all_checks) else "FAIL"
    report = {
        "status": status,
        "near_ceiling_fraction": NEAR_CEILING_FRACTION,
        "rows": len(rows),
        "pair_checks": pair_checks,
        "cross_cue_checks": cross_cue_checks,
        "cross_task_checks": cross_task_checks,
        "max_history_completion_token_utilization": max_history_util if rows else None,
        "max_final_completion_token_utilization": max_final_util if rows else None,
        "problems": problems,
        "interpretation_rule": "Cross-task interactions are estimable only after matched H5/H6 prompts, matched recovery/content/task, complete cue/task cells, and censoring/headroom checks pass.",
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if status != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
