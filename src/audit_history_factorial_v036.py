from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN_PATH = Path(os.getenv("V036_RESULTS_PATH", ROOT / "results" / "history_factorial_v036" / "factorial_responses.jsonl"))
OUT_PATH = Path(os.getenv("V036_AUDIT_PATH", ROOT / "results" / "history_factorial_v036" / "factorial_audit.json"))
NEAR = float(os.getenv("NEAR_CEILING_FRACTION", "0.90"))
EXPECTED_MODELS = {"nvidia/nemotron-3-super-120b-a12b", "openai/gpt-oss-20b"}
EXPECTED_TASKS = {"evidence_revision", "simple_complex", "unexpected_result"}
EXPECTED_REPLICATES = {1, 2, 3}
EXPECTED_HISTORIES = {"H00_neutral", "H10_format_only", "H01_evaluation_only", "H11_combined"}
EXPECTED_FACTORS = {
    "H00_neutral": (0, 0),
    "H10_format_only": (1, 0),
    "H01_evaluation_only": (0, 1),
    "H11_combined": (1, 1),
}


def load_rows() -> list[dict]:
    if not IN_PATH.exists():
        raise SystemExit(f"missing input: {IN_PATH}")
    return [json.loads(x) for x in IN_PATH.read_text(encoding="utf-8").splitlines() if x.strip()]


def completion_tokens(obj: dict) -> int | None:
    usage = obj.get("usage") or {}
    for k in ("completion_tokens", "output_tokens"):
        if isinstance(usage.get(k), (int, float)):
            return int(usage[k])
    return None


def utilization(obj: dict) -> float | None:
    used = completion_tokens(obj)
    cap = obj.get("requested_max_tokens")
    if used is None or not isinstance(cap, (int, float)) or cap <= 0:
        return None
    return used / cap


def main() -> None:
    data = load_rows()
    problems = []
    checks = []
    keys = {(r.get("model"), r.get("task_id"), int(r.get("replicate", 0)), r.get("history")) for r in data}

    if len(data) != 72 or len(keys) != 72:
        problems.append({"problem": "EXPECTED_72_UNIQUE_CELLS", "rows": len(data), "unique": len(keys)})
    if {r.get("model") for r in data} != EXPECTED_MODELS:
        problems.append({"problem": "MODEL_SET_MISMATCH"})
    if {r.get("task_id") for r in data} != EXPECTED_TASKS:
        problems.append({"problem": "TASK_SET_MISMATCH"})
    if {int(r.get("replicate", 0)) for r in data} != EXPECTED_REPLICATES:
        problems.append({"problem": "REPLICATE_SET_MISMATCH"})

    max_hist = 0.0
    max_final = 0.0
    for model in sorted(EXPECTED_MODELS):
        for task in sorted(EXPECTED_TASKS):
            for replicate in sorted(EXPECTED_REPLICATES):
                block = [r for r in data if r.get("model") == model and r.get("task_id") == task and int(r.get("replicate", 0)) == replicate]
                by_h = {r.get("history"): r for r in block}
                histories_ok = set(by_h) == EXPECTED_HISTORIES and len(block) == 4
                prompts = {r.get("current_probe_text") for r in block}
                recoveries = {r.get("shared_recovery_text") for r in block}
                contents = {json.dumps(r.get("shared_content_triplet"), ensure_ascii=False) for r in block}
                task_texts = {r.get("task_text") for r in block}
                factors_ok = all(
                    (int(r.get("format_factor", -1)), int(r.get("evaluation_factor", -1))) == EXPECTED_FACTORS.get(r.get("history"))
                    for r in block
                )
                censored = 0
                near_count = 0
                task_present = True
                for r in block:
                    task_present = task_present and bool(r.get("task_text")) and r.get("task_text") in (r.get("current_probe_text") or "")
                    if r.get("finish_reason") == "length":
                        censored += 1
                    u = utilization(r)
                    if u is not None:
                        max_final = max(max_final, u)
                        if u >= NEAR:
                            near_count += 1
                    for t in r.get("history_transcript") or []:
                        if t.get("finish_reason") == "length":
                            censored += 1
                        hu = utilization(t)
                        if hu is not None:
                            max_hist = max(max_hist, hu)
                            if hu >= NEAR:
                                near_count += 1

                ok = (
                    histories_ok and len(prompts) == 1 and len(recoveries) == 1
                    and len(contents) == 1 and len(task_texts) == 1 and task_present
                    and factors_ok and censored == 0 and near_count == 0
                )
                checks.append({
                    "model": model,
                    "task_id": task,
                    "replicate": replicate,
                    "histories_complete": histories_ok,
                    "current_prompt_identical": len(prompts) == 1,
                    "recovery_identical": len(recoveries) == 1,
                    "content_identical": len(contents) == 1,
                    "task_identical": len(task_texts) == 1,
                    "task_present_in_probe": task_present,
                    "factor_mapping_correct": factors_ok,
                    "right_censored_or_near_ceiling_events": censored + near_count,
                    "status": "PASS" if ok else "FAIL",
                })
                if not ok:
                    problems.append({"model": model, "task_id": task, "replicate": replicate, "problem": "FACTORIAL_BLOCK_VALIDITY_FAILURE"})

    status = "PASS" if len(checks) == 18 and not problems and all(c["status"] == "PASS" for c in checks) else "FAIL"
    report = {
        "status": status,
        "rows": len(data),
        "unique_cells": len(keys),
        "near_ceiling_fraction": NEAR,
        "block_checks": checks,
        "max_history_completion_token_utilization": max_hist,
        "max_final_completion_token_utilization": max_final,
        "problems": problems,
        "interpretation_rule": "Factorial confirmation is eligible only if all 18 model-task-replicate blocks contain all four matched histories and pass prompt/recovery/content/task/factor/censoring checks.",
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if status != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
