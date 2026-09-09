from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "panel_v03"

PHASES = ["post_history", "post_recovery", "post_reexposure"]
WARM = "H0_warm_control"
WEAK_NO_HISTORY = "H5_weak_cue_no_prior_pressure"
WEAK_AFTER_HISTORY = "H6_combined_recovery_weak_reexposure"


def read_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def log_ratio(x: float, baseline: float) -> float:
    return math.log((x + 1.0) / (baseline + 1.0))


def sign(x: float, eps: float = 1e-9) -> int:
    if x > eps:
        return 1
    if x < -eps:
        return -1
    return 0


def main() -> None:
    rows = read_jsonl(OUT_DIR / "turns.jsonl")
    fresh = read_jsonl(OUT_DIR / "fresh_probes.jsonl")

    anchors: dict[tuple, dict[str, dict]] = defaultdict(dict)
    for row in rows:
        if row.get("event_kind") == "anchor":
            anchors[(row["model"], row["history"], row["trial"])][row["phase"]] = row

    fresh_map = {(r["model"], r["trial"]): r for r in fresh}
    records = []

    for (model, history, trial), phase_rows in sorted(anchors.items()):
        if "baseline" not in phase_rows:
            continue
        warm_rows = anchors.get((model, WARM, trial), {})
        if "baseline" not in warm_rows:
            continue

        baseline = phase_rows["baseline"]
        warm_baseline = warm_rows["baseline"]
        fresh_row = fresh_map.get((model, trial))

        for phase in PHASES:
            current = phase_rows.get(phase)
            warm_current = warm_rows.get(phase)
            if current is None or warm_current is None:
                continue

            own = log_ratio(current["response_words"], baseline["response_words"])
            warm = log_ratio(warm_current["response_words"], warm_baseline["response_words"])
            did = own - warm
            fresh_log = None
            if fresh_row is not None:
                fresh_log = math.log((current["response_words"] + 1.0) / (fresh_row["response_words"] + 1.0))

            records.append({
                "model": model,
                "history": history,
                "trial": trial,
                "phase": phase,
                "response_words": current["response_words"],
                "baseline_words": baseline["response_words"],
                "warm_control_log_ratio": warm,
                "within_run_log_ratio": own,
                "control_subtracted_log_ratio": did,
                "fresh_session_log_ratio": fresh_log,
                "finish_reason": current.get("finish_reason"),
                "retry_count": current.get("retry_count", 0),
            })

    sensitization = []
    indexed = {(r["model"], r["history"], r["trial"], r["phase"]): r for r in records}
    models_trials = sorted({(r["model"], r["trial"]) for r in records})
    for model, trial in models_trials:
        h5 = indexed.get((model, WEAK_NO_HISTORY, trial, "post_reexposure"))
        h6 = indexed.get((model, WEAK_AFTER_HISTORY, trial, "post_reexposure"))
        if h5 and h6:
            contrast = h6["control_subtracted_log_ratio"] - h5["control_subtracted_log_ratio"]
            sensitization.append({
                "model": model,
                "trial": trial,
                "h5_weak_no_prior_pressure": h5["control_subtracted_log_ratio"],
                "h6_weak_after_combined_history": h6["control_subtracted_log_ratio"],
                "sensitization_contrast": contrast,
                "direction": sign(contrast),
            })

    warnings = []
    for phase in PHASES:
        by_history: dict[str, list[dict]] = defaultdict(list)
        for r in records:
            if r["phase"] == phase and r["history"] != WARM:
                by_history[r["history"]].append(r)
        for history, vals in by_history.items():
            by_model: dict[str, list[float]] = defaultdict(list)
            for r in vals:
                by_model[r["model"]].append(r["control_subtracted_log_ratio"])
            model_signs = {m: sign(sum(v) / len(v)) for m, v in by_model.items() if v}
            nonzero = {s for s in model_signs.values() if s != 0}
            if len(nonzero) > 1:
                warnings.append({
                    "phase": phase,
                    "history": history,
                    "warning": "DO_NOT_POOL_DIRECTION",
                    "model_signs": model_signs,
                })

    truncation = {
        "anchor_count": sum(1 for r in rows if r.get("event_kind") == "anchor"),
        "anchor_finish_length_count": sum(1 for r in rows if r.get("event_kind") == "anchor" and r.get("finish_reason") == "length"),
    }
    if truncation["anchor_count"]:
        truncation["anchor_finish_length_rate"] = truncation["anchor_finish_length_count"] / truncation["anchor_count"]

    report = {
        "analysis_order": [
            "integrity_and_truncation",
            "model_stratified_anchor_trajectories",
            "within_run_drift",
            "warm_control_subtracted_drift",
            "fresh_session_comparison",
            "H2_vs_H3",
            "H6_vs_H5_matched_weak_cue_sensitization",
            "aggregation_only_if_directions_are_compatible",
        ],
        "truncation": truncation,
        "records": records,
        "sensitization": sensitization,
        "aggregation_warnings": warnings,
        "interpretation": "history-dependent behavior within retained context; not subjective emotion or context-independent memory",
    }

    with (OUT_DIR / "analysis_v03.json").open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(json.dumps({
        "truncation": truncation,
        "sensitization": sensitization,
        "aggregation_warnings": warnings,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
