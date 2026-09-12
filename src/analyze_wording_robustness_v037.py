from __future__ import annotations

import json
import math
import os
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
IN_PATH = Path(os.getenv("V037_RESULTS_PATH", ROOT / "results" / "wording_robustness_v037" / "wording_responses.jsonl"))
AUDIT_PATH = Path(os.getenv("V037_AUDIT_PATH", ROOT / "results" / "wording_robustness_v037" / "wording_audit.json"))
OUT_PATH = Path(os.getenv("V037_ANALYSIS_PATH", ROOT / "results" / "wording_robustness_v037" / "wording_analysis.json"))

H00 = "H00_neutral"
TREATMENTS = {
    "legacy": "H10A_legacy",
    "concise": "H10B_concise",
    "essentials": "H10C_essentials",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    data = [json.loads(x) for x in IN_PATH.read_text(encoding="utf-8").splitlines() if x.strip()]
    audit = load_json(AUDIT_PATH)
    if audit.get("status") != "PASS":
        raise SystemExit("audit did not pass")

    models = sorted({r["model"] for r in data})
    tasks = sorted({r["task_id"] for r in data})
    reps = sorted({int(r["replicate"]) for r in data})

    contrasts = []
    for model in models:
        for task in tasks:
            for rep in reps:
                block = {
                    r["history"]: r
                    for r in data
                    if r["model"] == model and r["task_id"] == task and int(r["replicate"]) == rep
                }
                expected = {H00, *TREATMENTS.values()}
                if set(block) != expected:
                    raise SystemExit(f"incomplete block: {model} {task} rep={rep}")
                base_log = math.log(float(block[H00]["response_words"]) + 1.0)
                for family, history_id in TREATMENTS.items():
                    treatment_log = math.log(float(block[history_id]["response_words"]) + 1.0)
                    d = treatment_log - base_log
                    contrasts.append({
                        "model": model,
                        "task_id": task,
                        "replicate": rep,
                        "wording_family": family,
                        "neutral_words": float(block[H00]["response_words"]),
                        "treatment_words": float(block[history_id]["response_words"]),
                        "D_log_length": round(d, 6),
                        "length_ratio": round(math.exp(d), 6),
                    })

    summaries = []
    for model in models:
        model_rows = [r for r in contrasts if r["model"] == model]
        wording_summaries = []
        wording_passes = []

        for family in TREATMENTS:
            rows_f = [r for r in model_rows if r["wording_family"] == family]
            vals = [r["D_log_length"] for r in rows_f]
            by_task = {
                task: sum(r["D_log_length"] < 0 for r in rows_f if r["task_id"] == task)
                for task in tasks
            }
            passes = (
                len(vals) == 6
                and median(vals) < 0
                and sum(v < 0 for v in vals) >= 4
                and all(by_task[t] >= 1 for t in tasks)
            )
            wording_passes.append(passes)
            wording_summaries.append({
                "wording_family": family,
                "n_contrasts": len(vals),
                "median_D": round(median(vals), 6),
                "median_length_ratio": round(math.exp(median(vals)), 6),
                "negative_contrasts": sum(v < 0 for v in vals),
                "negative_by_task": by_task,
                "wording_level_support": passes,
            })

        all_vals = [r["D_log_length"] for r in model_rows]
        task_neg = {
            task: sum(r["D_log_length"] < 0 for r in model_rows if r["task_id"] == task)
            for task in tasks
        }
        robust = (
            len(all_vals) == 18
            and all(wording_passes)
            and median(all_vals) < 0
            and sum(v < 0 for v in all_vals) >= 14
            and all(task_neg[t] >= 4 for t in tasks)
        )
        summaries.append({
            "model": model,
            "wording_summaries": wording_summaries,
            "overall": {
                "n_contrasts": len(all_vals),
                "median_D": round(median(all_vals), 6),
                "median_length_ratio": round(math.exp(median(all_vals)), 6),
                "negative_contrasts": sum(v < 0 for v in all_vals),
                "negative_by_task": task_neg,
                "all_three_wordings_pass": all(wording_passes),
                "wording_robust": robust,
            },
        })

    report = {
        "version": "0.3.7-wording-robustness",
        "audit_status": audit.get("status"),
        "contrasts": contrasts,
        "model_summaries": summaries,
        "wording_level_rule": "Within model and wording: 6 valid contrasts; median D<0; >=4/6 negative; every task >=1/2 negative.",
        "overall_rule": "Within model: all three wordings pass; across 18 contrasts median D<0 and >=14/18 negative; every task >=4/6 negative.",
        "prospective_boundary": "Only fresh v0.3.7 draws count; v0.3.5-v0.3.6 observations are excluded from the wording-robustness rule.",
        "interpretation_boundary": "retained-context behavioral format-policy robustness only; no subjective-state inference",
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
