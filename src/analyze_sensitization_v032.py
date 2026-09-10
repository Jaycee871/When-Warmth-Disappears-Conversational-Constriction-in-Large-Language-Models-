from __future__ import annotations

import json
import math
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN_PATH = Path(os.getenv("SENS032_RESULTS_PATH", ROOT / "results" / "sensitization_v032" / "task_anchored_responses.jsonl"))
AUDIT_PATH = Path(os.getenv("SENS032_AUDIT_PATH", ROOT / "results" / "sensitization_v032" / "sensitization_audit.json"))
OUT_PATH = Path(os.getenv("SENS032_ANALYSIS_PATH", ROOT / "results" / "sensitization_v032" / "sensitization_interactions.json"))
H5 = "H5_no_prior_pressure"
H6 = "H6_prior_combined_pressure"
CUES = ["neutral", "format_only", "evaluation_only"]


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"missing input: {path}")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def log_words(row: dict) -> float:
    return math.log(float(row.get("response_words", 0.0)) + 1.0)


def main() -> None:
    rows = load_jsonl(IN_PATH)
    if not AUDIT_PATH.exists():
        raise SystemExit(f"missing audit: {AUDIT_PATH}")
    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    if audit.get("status") != "PASS":
        raise SystemExit("v0.3.2 audit did not pass; withhold interaction estimates")

    by_key = {(r["model"], int(r["trial"]), r["cue_type"], r["history"]): r for r in rows}
    models = sorted({r["model"] for r in rows})
    trials = sorted({int(r["trial"]) for r in rows})

    history_effects = []
    interactions = []

    for model in models:
        for trial in trials:
            d: dict[str, float] = {}
            word_cells: dict[str, dict[str, float]] = {}
            for cue in CUES:
                h5 = by_key[(model, trial, cue, H5)]
                h6 = by_key[(model, trial, cue, H6)]
                delta = log_words(h6) - log_words(h5)
                d[cue] = delta
                word_cells[cue] = {
                    "H5": float(h5["response_words"]),
                    "H6": float(h6["response_words"]),
                }
                history_effects.append({
                    "model": model,
                    "trial": trial,
                    "cue_type": cue,
                    "task_id": h5["task_id"],
                    "H5_response_words": h5["response_words"],
                    "H6_response_words": h6["response_words"],
                    "D_H6_minus_H5_log_length": round(delta, 6),
                })

            s_format = d["format_only"] - d["neutral"]
            s_eval = d["evaluation_only"] - d["neutral"]
            interactions.append({
                "model": model,
                "trial": trial,
                "task_id": by_key[(model, trial, "neutral", H5)]["task_id"],
                "D_neutral": round(d["neutral"], 6),
                "D_format": round(d["format_only"], 6),
                "D_evaluation": round(d["evaluation_only"], 6),
                "S_format_Dformat_minus_Dneutral": round(s_format, 6),
                "S_evaluation_Devaluation_minus_Dneutral": round(s_eval, 6),
                "format_interaction_direction": "additional_contraction" if s_format < 0 else ("additional_expansion" if s_format > 0 else "zero"),
                "evaluation_interaction_direction": "additional_contraction" if s_eval < 0 else ("additional_expansion" if s_eval > 0 else "zero"),
                "word_cells": word_cells,
            })

    warnings = []
    if len(models) > 1:
        for key in ("S_format_Dformat_minus_Dneutral", "S_evaluation_Devaluation_minus_Dneutral"):
            vals = [x[key] for x in interactions]
            signs = {1 if v > 0 else -1 if v < 0 else 0 for v in vals}
            signs.discard(0)
            if len(signs) > 1:
                warnings.append({
                    "estimand": key,
                    "warning": "DO_NOT_POOL_DIRECTION",
                    "values_by_model": {x["model"]: x[key] for x in interactions},
                })

    report = {
        "version": "0.3.2-sensitization",
        "audit_status": audit.get("status"),
        "history_effects": history_effects,
        "cue_specific_interactions": interactions,
        "warnings": warnings,
        "primary_estimands": {
            "S_format": "(H6-H5 under format cue) - (H6-H5 under neutral cue)",
            "S_evaluation": "(H6-H5 under evaluation cue) - (H6-H5 under neutral cue)",
        },
        "interpretation_rule": "A raw H6-H5 difference is residual history dependence. Cue-specific sensitization requires an interaction beyond the neutral-cue H6-H5 baseline.",
        "replication_boundary": "One trial per model is sentinel evidence only. Do not infer stable model-family differences without multi-trial and multi-task replication.",
        "interpretation_boundary": "behavioral/functional history dependence only; no claim of subjective emotion, distress, feeling, or consciousness",
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
