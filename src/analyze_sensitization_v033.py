from __future__ import annotations

import json
import math
import os
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN_PATH = Path(os.getenv("SENS033_RESULTS_PATH", ROOT / "results" / "sensitization_v033" / "task_anchored_responses.jsonl"))
AUDIT_PATH = Path(os.getenv("SENS033_AUDIT_PATH", ROOT / "results" / "sensitization_v033" / "sensitization_audit.json"))
OUT_PATH = Path(os.getenv("SENS033_ANALYSIS_PATH", ROOT / "results" / "sensitization_v033" / "sensitization_interactions.json"))
H5 = "H5_no_prior_pressure"
H6 = "H6_prior_combined_pressure"
CUES = ["neutral", "format_only", "evaluation_only"]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def log_words(row: dict) -> float:
    return math.log(float(row.get("response_words", 0.0)) + 1.0)


def sign(v: float) -> int:
    return 1 if v > 0 else -1 if v < 0 else 0


def main() -> None:
    rows = load_jsonl(IN_PATH)
    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    if audit.get("status") != "PASS":
        raise SystemExit("v0.3.3 audit did not pass; withhold interaction estimates")

    by_key = {
        (r["model"], int(r["replicate"]), r["task_id"], r["cue_type"], r["history"]): r
        for r in rows
    }
    models = sorted({r["model"] for r in rows})
    replicates = sorted({int(r["replicate"]) for r in rows})
    tasks = sorted({r["task_id"] for r in rows})

    interactions = []
    history_effects = []

    for model in models:
        for replicate in replicates:
            for task_id in tasks:
                d = {}
                cells = {}
                for cue in CUES:
                    h5 = by_key[(model, replicate, task_id, cue, H5)]
                    h6 = by_key[(model, replicate, task_id, cue, H6)]
                    delta = log_words(h6) - log_words(h5)
                    d[cue] = delta
                    cells[cue] = {"H5": float(h5["response_words"]), "H6": float(h6["response_words"])}
                    history_effects.append({
                        "model": model,
                        "replicate": replicate,
                        "task_id": task_id,
                        "cue_type": cue,
                        "H5_response_words": h5["response_words"],
                        "H6_response_words": h6["response_words"],
                        "D_H6_minus_H5_log_length": round(delta, 6),
                    })

                s_format = d["format_only"] - d["neutral"]
                s_eval = d["evaluation_only"] - d["neutral"]
                interactions.append({
                    "model": model,
                    "replicate": replicate,
                    "task_id": task_id,
                    "D_neutral": round(d["neutral"], 6),
                    "D_format": round(d["format_only"], 6),
                    "D_evaluation": round(d["evaluation_only"], 6),
                    "S_format": round(s_format, 6),
                    "S_evaluation": round(s_eval, 6),
                    "S_evaluation_minus_S_format": round(s_eval - s_format, 6),
                    "word_cells": cells,
                })

    model_summaries = []
    for model in models:
        vals = [x for x in interactions if x["model"] == model]
        s_eval = [float(x["S_evaluation"]) for x in vals]
        s_fmt = [float(x["S_format"]) for x in vals]
        eval_lt_fmt = [float(x["S_evaluation"]) < float(x["S_format"]) for x in vals]
        n = len(vals)
        neg_eval = sum(v < 0 for v in s_eval)
        support_threshold = math.ceil((2.0 / 3.0) * n)
        eval_supported = statistics.median(s_eval) < 0 and neg_eval >= support_threshold
        dissociation_supported = (
            statistics.median(s_eval) < statistics.median(s_fmt)
            and sum(eval_lt_fmt) >= support_threshold
        )
        model_summaries.append({
            "model": model,
            "n_task_blocks": n,
            "median_S_evaluation": round(statistics.median(s_eval), 6),
            "median_S_format": round(statistics.median(s_fmt), 6),
            "negative_S_evaluation_blocks": neg_eval,
            "evaluation_less_than_format_blocks": sum(eval_lt_fmt),
            "two_thirds_threshold": support_threshold,
            "cross_task_evaluation_support": bool(eval_supported),
            "evaluation_vs_format_dissociation_support": bool(dissociation_supported),
        })

    warnings = []
    med_signs = {sign(float(x["median_S_evaluation"])) for x in model_summaries}
    med_signs.discard(0)
    if len(med_signs) > 1:
        warnings.append({
            "estimand": "median_S_evaluation",
            "warning": "DO_NOT_POOL_DIRECTION",
            "values_by_model": {x["model"]: x["median_S_evaluation"] for x in model_summaries},
        })

    report = {
        "version": "0.3.3-sensitization-replication",
        "audit_status": audit.get("status"),
        "history_effects": history_effects,
        "cue_specific_interactions": interactions,
        "model_summaries": model_summaries,
        "warnings": warnings,
        "pre_specified_support_rule": "Within model: median S_evaluation < 0 and at least two-thirds of valid task blocks have S_evaluation < 0.",
        "pre_specified_dissociation_rule": "Within model: median S_evaluation < median S_format and at least two-thirds of valid task blocks have S_evaluation < S_format.",
        "replication_boundary": "Initial v0.3.3 stage is cross-task single-draw replication, not a multi-trial population-level confirmation.",
        "interpretation_boundary": "behavioral/functional history dependence only; no subjective-state inference",
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
