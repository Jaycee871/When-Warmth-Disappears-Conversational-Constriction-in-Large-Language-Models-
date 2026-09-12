from __future__ import annotations

import json
import math
import os
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
IN_PATH = Path(os.getenv("V035_RESULTS_PATH", ROOT / "results" / "history_factorial_v035" / "factorial_responses.jsonl"))
AUDIT_PATH = Path(os.getenv("V035_AUDIT_PATH", ROOT / "results" / "history_factorial_v035" / "factorial_audit.json"))
OUT_PATH = Path(os.getenv("V035_ANALYSIS_PATH", ROOT / "results" / "history_factorial_v035" / "factorial_analysis.json"))
H00 = "H00_neutral"
H10 = "H10_format_only"
H01 = "H01_evaluation_only"
H11 = "H11_combined"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    data = [json.loads(x) for x in IN_PATH.read_text(encoding="utf-8").splitlines() if x.strip()]
    audit = load_json(AUDIT_PATH)
    if audit.get("status") != "PASS":
        raise SystemExit("audit did not pass")

    task_effects = []
    models = sorted({r["model"] for r in data})
    tasks = sorted({r["task_id"] for r in data})

    for model in models:
        for task in tasks:
            block = {r["history"]: r for r in data if r["model"] == model and r["task_id"] == task}
            if set(block) != {H00, H10, H01, H11}:
                raise SystemExit(f"incomplete block: {model} {task}")
            L = {h: math.log(float(block[h]["response_words"]) + 1.0) for h in block}
            AF = 0.5 * ((L[H10] - L[H00]) + (L[H11] - L[H01]))
            AE = 0.5 * ((L[H01] - L[H00]) + (L[H11] - L[H10]))
            AFE = L[H11] - L[H10] - L[H01] + L[H00]
            task_effects.append({
                "model": model,
                "task_id": task,
                "response_words": {h: float(block[h]["response_words"]) for h in (H00, H10, H01, H11)},
                "H10_minus_H00": round(L[H10] - L[H00], 6),
                "H01_minus_H00": round(L[H01] - L[H00], 6),
                "H11_minus_H00": round(L[H11] - L[H00], 6),
                "A_format": round(AF, 6),
                "A_evaluation": round(AE, 6),
                "A_interaction": round(AFE, 6),
            })

    model_summaries = []
    for model in models:
        vals = [x for x in task_effects if x["model"] == model]
        f = [x["A_format"] for x in vals]
        e = [x["A_evaluation"] for x in vals]
        fe = [x["A_interaction"] for x in vals]
        d10 = [x["H10_minus_H00"] for x in vals]
        d01 = [x["H01_minus_H00"] for x in vals]
        d11 = [x["H11_minus_H00"] for x in vals]
        model_summaries.append({
            "model": model,
            "median_A_format": round(median(f), 6),
            "negative_A_format_tasks": sum(v < 0 for v in f),
            "format_cross_task_candidate": median(f) < 0 and sum(v < 0 for v in f) >= 2,
            "median_A_evaluation": round(median(e), 6),
            "negative_A_evaluation_tasks": sum(v < 0 for v in e),
            "evaluation_cross_task_candidate": median(e) < 0 and sum(v < 0 for v in e) >= 2,
            "median_A_interaction": round(median(fe), 6),
            "negative_A_interaction_tasks": sum(v < 0 for v in fe),
            "median_H10_minus_H00": round(median(d10), 6),
            "median_H01_minus_H00": round(median(d01), 6),
            "median_H11_minus_H00": round(median(d11), 6),
            "combined_more_negative_than_each_single_in_tasks": sum(x["H11_minus_H00"] < min(x["H10_minus_H00"], x["H01_minus_H00"]) for x in vals),
        })

    report = {
        "version": "0.3.5-history-factorial-sentinel",
        "audit_status": audit.get("status"),
        "task_effects": task_effects,
        "model_summaries": model_summaries,
        "sentinel_rule": "A main-effect mechanism is a cross-task candidate only if its median task-level contrast is negative and at least 2/3 tasks share that sign. One draw per task is screening evidence only.",
        "next_boundary": "Any candidate mechanism requires fresh multi-replicate confirmation before promotion; null or heterogeneous results are preserved.",
        "interpretation_boundary": "behavioral retained-context history decomposition only; no subjective-state inference",
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
