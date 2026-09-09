from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "panel_v03"

PHASES = ["post_history", "post_recovery", "post_reexposure"]
WARM = "H0_warm_control"
TERSE = "H1_neutral_terse_control"
WEAK_NO_HISTORY = "H5_weak_cue_no_prior_pressure"
WEAK_AFTER_HISTORY = "H6_combined_recovery_weak_reexposure"


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"missing input: {path}")
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def complete(row: dict | None) -> bool:
    return bool(row) and row.get("finish_reason") != "length"


def log_ratio(current: dict, baseline: dict) -> float | None:
    if not complete(current) or not complete(baseline):
        return None
    return math.log((float(current["response_words"]) + 1.0) / (float(baseline["response_words"]) + 1.0))


def sign(x: float, eps: float = 1e-9) -> int:
    if x > eps:
        return 1
    if x < -eps:
        return -1
    return 0


def subtract(a: float | None, b: float | None) -> float | None:
    return None if a is None or b is None else a - b


def main() -> None:
    rows = read_jsonl(OUT_DIR / "turns.jsonl")
    fresh = read_jsonl(OUT_DIR / "fresh_probes.jsonl")

    anchors: dict[tuple, dict[str, dict]] = defaultdict(dict)
    for row in rows:
        if row.get("event_kind") == "anchor":
            anchors[(row["model"], row["history"], int(row["trial"]))][row["phase"]] = row

    fresh_map = {(r["model"], int(r["trial"])): r for r in fresh}
    records = []

    for (model, history, trial), phase_rows in sorted(anchors.items()):
        baseline = phase_rows.get("baseline")
        warm_rows = anchors.get((model, WARM, trial), {})
        terse_rows = anchors.get((model, TERSE, trial), {})
        warm_baseline = warm_rows.get("baseline")
        terse_baseline = terse_rows.get("baseline")
        fresh_row = fresh_map.get((model, trial))
        if baseline is None or warm_baseline is None:
            continue

        for phase in PHASES:
            current = phase_rows.get(phase)
            warm_current = warm_rows.get(phase)
            if current is None or warm_current is None:
                continue

            own = log_ratio(current, baseline)
            warm = log_ratio(warm_current, warm_baseline)
            did_warm = subtract(own, warm)

            terse = None
            did_terse = None
            terse_current = terse_rows.get(phase)
            if terse_baseline is not None and terse_current is not None:
                terse = log_ratio(terse_current, terse_baseline)
                did_terse = subtract(own, terse)

            fresh_log = None
            if fresh_row is not None and complete(current) and complete(fresh_row):
                fresh_log = math.log(
                    (float(current["response_words"]) + 1.0)
                    / (float(fresh_row["response_words"]) + 1.0)
                )

            records.append({
                "model": model,
                "history": history,
                "trial": trial,
                "phase": phase,
                "response_words": current["response_words"],
                "baseline_words": baseline["response_words"],
                "within_run_log_ratio": own,
                "warm_control_log_ratio": warm,
                "control_subtracted_log_ratio_vs_warm": did_warm,
                "terse_control_log_ratio": terse,
                "control_subtracted_log_ratio_vs_terse": did_terse,
                "fresh_session_log_ratio": fresh_log,
                "baseline_finish_reason": baseline.get("finish_reason"),
                "finish_reason": current.get("finish_reason"),
                "retry_count": current.get("retry_count", 0),
            })

    indexed = {(r["model"], r["history"], r["trial"], r["phase"]): r for r in records}
    sensitization = []
    for model, trial in sorted({(r["model"], r["trial"]) for r in records}):
        h5 = indexed.get((model, WEAK_NO_HISTORY, trial, "post_reexposure"))
        h6 = indexed.get((model, WEAK_AFTER_HISTORY, trial, "post_reexposure"))
        if h5 and h6:
            a = h5["control_subtracted_log_ratio_vs_warm"]
            b = h6["control_subtracted_log_ratio_vs_warm"]
            contrast = subtract(b, a)
            sensitization.append({
                "model": model,
                "trial": trial,
                "h5_weak_no_prior_pressure": a,
                "h6_weak_after_combined_history": b,
                "sensitization_contrast": contrast,
                "direction": None if contrast is None else sign(contrast),
            })

    warnings = []
    for phase in PHASES:
        by_history: dict[str, list[dict]] = defaultdict(list)
        for r in records:
            if r["phase"] == phase and r["history"] not in {WARM, TERSE}:
                by_history[r["history"]].append(r)
        for history, vals in by_history.items():
            for field, label in [
                ("control_subtracted_log_ratio_vs_warm", "warm"),
                ("control_subtracted_log_ratio_vs_terse", "terse"),
            ]:
                by_model: dict[str, list[float]] = defaultdict(list)
                for r in vals:
                    value = r.get(field)
                    if value is not None:
                        by_model[r["model"]].append(value)
                model_signs = {m: sign(sum(v) / len(v)) for m, v in by_model.items() if v}
                nonzero = {s for s in model_signs.values() if s != 0}
                if len(nonzero) > 1:
                    warnings.append({
                        "phase": phase,
                        "history": history,
                        "control": label,
                        "warning": "DO_NOT_POOL_DIRECTION",
                        "model_signs": model_signs,
                    })

    anchor_rows = [r for r in rows if r.get("event_kind") == "anchor"]
    truncation = {
        "anchor_count": len(anchor_rows),
        "anchor_finish_length_count": sum(r.get("finish_reason") == "length" for r in anchor_rows),
        "fresh_probe_count": len(fresh),
        "fresh_finish_length_count": sum(r.get("finish_reason") == "length" for r in fresh),
    }
    if truncation["anchor_count"]:
        truncation["anchor_finish_length_rate"] = truncation["anchor_finish_length_count"] / truncation["anchor_count"]

    report = {
        "analysis_order": [
            "integrity_and_truncation",
            "model_stratified_anchor_trajectories",
            "within_run_drift",
            "dual_control_subtracted_drift",
            "fresh_session_comparison",
            "H2_vs_H3",
            "H6_vs_H5_matched_weak_cue_sensitization",
            "aggregation_only_if_directions_are_compatible",
        ],
        "truncation": truncation,
        "records": records,
        "sensitization": sensitization,
        "aggregation_warnings": warnings,
        "length_rule": "any response-length contrast touching finish_reason=length is null",
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
