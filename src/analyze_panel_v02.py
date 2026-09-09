from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
IN_PATH = ROOT / "results" / "panel_v02" / "turns.jsonl"
OUT_DIR = ROOT / "results" / "panel_v02" / "analysis"

ANCHOR_PHASES = ["post_pressure", "post_recovery", "post_reexposure"]
CONTROL = "C0_warm_control"
SECONDARY_CONTROL = "C1_neutral_short_control"

METRICS = [
    "response_words",
    "lexical_diversity",
    "hedge_rate",
    "apology_rate",
    "approval_seeking_rate",
    "repair_rate",
    "self_monitoring_rate",
    "question_rate",
]


def load_rows() -> list[dict]:
    if not IN_PATH.exists():
        raise SystemExit(f"missing input: {IN_PATH}")
    return [json.loads(line) for line in IN_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


def token_set(text: str) -> set[str]:
    return set(text.lower().split())


def jaccard_distance(a: str, b: str) -> float:
    sa, sb = token_set(a), token_set(b)
    if not sa and not sb:
        return 0.0
    union = sa | sb
    return 1.0 - (len(sa & sb) / len(union) if union else 1.0)


def sign(x: float, eps: float = 1e-12) -> int:
    if x > eps:
        return 1
    if x < -eps:
        return -1
    return 0


def classify_word_response(log_ratio: float | None) -> str:
    if log_ratio is None:
        return "truncated"
    if log_ratio <= math.log(0.8):
        return "shrink"
    if log_ratio >= math.log(1.25):
        return "overcompensate"
    return "stable"


def anchor_complete(row: dict) -> bool:
    return row.get("finish_reason") != "length"


def per_run_anchor_deltas(rows: list[dict]) -> list[dict]:
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        if row.get("event_kind") == "anchor":
            grouped[(row["model"], row["condition"], int(row["trial"]))].append(row)

    output = []
    for (model, condition, trial), anchors in sorted(grouped.items()):
        by_phase = {a["phase"]: a for a in anchors}
        baseline = by_phase.get("baseline")
        if baseline is None:
            continue

        for phase in ANCHOR_PHASES:
            current = by_phase.get(phase)
            if current is None:
                continue

            pair_complete = anchor_complete(baseline) and anchor_complete(current)
            word_log_change = None
            if pair_complete:
                word_log_change = math.log(
                    (float(current["response_words"]) + 1.0)
                    / (float(baseline["response_words"]) + 1.0)
                )

            item = {
                "model": model,
                "condition": condition,
                "trial": trial,
                "phase": phase,
                "baseline_words": float(baseline["response_words"]),
                "phase_words": float(current["response_words"]),
                "baseline_finish_reason": baseline.get("finish_reason"),
                "phase_finish_reason": current.get("finish_reason"),
                "anchor_pair_complete": pair_complete,
                "word_log_change": word_log_change,
                "anchor_jaccard_distance": jaccard_distance(
                    baseline.get("assistant_text", ""), current.get("assistant_text", "")
                ),
                "baseline_retry_count": int(baseline.get("retry_count", 0) or 0),
                "phase_retry_count": int(current.get("retry_count", 0) or 0),
            }
            item["response_mode"] = classify_word_response(word_log_change)
            for metric in METRICS:
                if metric == "response_words":
                    continue
                item[f"delta_{metric}"] = float(current.get(metric, 0.0)) - float(
                    baseline.get(metric, 0.0)
                )
            output.append(item)
    return output


def control_means(deltas: list[dict], control: str) -> dict[tuple, dict]:
    buckets: dict[tuple, list[dict]] = defaultdict(list)
    for d in deltas:
        if d["condition"] == control:
            buckets[(d["model"], d["phase"])].append(d)

    fields = ["word_log_change", "anchor_jaccard_distance"] + [
        f"delta_{m}" for m in METRICS if m != "response_words"
    ]
    out: dict[tuple, dict] = {}
    for key, vals in buckets.items():
        complete = [v for v in vals if v["anchor_pair_complete"]]
        entry = {
            "n_total": len(vals),
            "n_complete": len(complete),
        }
        for field in fields:
            source = complete if field == "word_log_change" else vals
            present = [float(v[field]) for v in source if v.get(field) is not None]
            entry[field] = mean(present) if present else None
        out[key] = entry
    return out


def add_did(deltas: list[dict], control: str, label: str) -> list[dict]:
    controls = control_means(deltas, control)
    fields = ["word_log_change", "anchor_jaccard_distance"] + [
        f"delta_{m}" for m in METRICS if m != "response_words"
    ]
    out = []
    for d in deltas:
        if d["condition"] == control:
            continue
        ctrl = controls.get((d["model"], d["phase"]))
        if ctrl is None:
            continue

        confirmatory_valid = bool(d["anchor_pair_complete"] and ctrl["n_complete"] > 0)
        row = {
            "model": d["model"],
            "condition": d["condition"],
            "trial": d["trial"],
            "phase": d["phase"],
            "control": control,
            "control_label": label,
            "response_mode_raw": d["response_mode"],
            "treatment_anchor_pair_complete": d["anchor_pair_complete"],
            "control_complete_pairs": ctrl["n_complete"],
            "confirmatory_length_valid": confirmatory_valid,
        }
        for field in fields:
            left = d.get(field)
            right = ctrl.get(field)
            if field == "word_log_change" and not confirmatory_valid:
                row[f"did_{field}"] = None
            elif left is None or right is None:
                row[f"did_{field}"] = None
            else:
                row[f"did_{field}"] = float(left) - float(right)
        out.append(row)
    return out


def summarize_did(did_rows: list[dict]) -> list[dict]:
    buckets: dict[tuple, list[dict]] = defaultdict(list)
    for row in did_rows:
        buckets[(row["model"], row["condition"], row["phase"], row["control"])].append(row)

    metric_fields = sorted(k for k in did_rows[0].keys() if k.startswith("did_")) if did_rows else []
    out = []
    for (model, condition, phase, control), vals in sorted(buckets.items()):
        row = {
            "model": model,
            "condition": condition,
            "phase": phase,
            "control": control,
            "n_total": len(vals),
            "n_confirmatory_length_valid": sum(bool(v["confirmatory_length_valid"]) for v in vals),
        }
        for field in metric_fields:
            present = [float(v[field]) for v in vals if v.get(field) is not None]
            row[f"mean_{field}"] = mean(present) if present else None
        out.append(row)
    return out


def aggregation_diagnostics(summary: list[dict]) -> list[dict]:
    buckets: dict[tuple, list[dict]] = defaultdict(list)
    for row in summary:
        buckets[(row["condition"], row["phase"], row["control"])].append(row)

    out = []
    for (condition, phase, control), vals in sorted(buckets.items()):
        key = "mean_did_word_log_change"
        valid_vals = [v for v in vals if v.get(key) is not None]
        model_signs = {v["model"]: sign(float(v[key])) for v in valid_vals}
        nonzero = [s for s in model_signs.values() if s != 0]
        heterogeneous = len(set(nonzero)) > 1
        if len(valid_vals) < 2:
            warning = "INSUFFICIENT_COMPLETE_MODELS"
        elif heterogeneous:
            warning = "DO_NOT_POOL_DIRECTION"
        else:
            warning = "direction_consistent"
        out.append({
            "condition": condition,
            "phase": phase,
            "control": control,
            "models_total": len(vals),
            "models_with_complete_length_effect": len(valid_vals),
            "model_signs": json.dumps(model_signs, sort_keys=True),
            "heterogeneous_direction": heterogeneous,
            "aggregation_warning": warning,
        })
    return out


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = load_rows()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    deltas = per_run_anchor_deltas(rows)
    did = add_did(deltas, CONTROL, "warm control")
    if any(d["condition"] == SECONDARY_CONTROL for d in deltas):
        did.extend(add_did(deltas, SECONDARY_CONTROL, "neutral-short control"))

    summary = summarize_did(did)
    diagnostics = aggregation_diagnostics(summary)

    write_csv(OUT_DIR / "anchor_deltas_by_run.csv", deltas)
    write_csv(OUT_DIR / "did_by_run.csv", did)
    write_csv(OUT_DIR / "did_summary_by_model.csv", summary)
    write_csv(OUT_DIR / "aggregation_diagnostics.csv", diagnostics)

    with (OUT_DIR / "analysis_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                "primary_estimand": "(phase - baseline) in treatment minus (phase - baseline) in matched control",
                "primary_scale_for_length": "log((phase_words+1)/(baseline_words+1))",
                "primary_control": CONTROL,
                "secondary_control": SECONDARY_CONTROL,
                "completion_censoring_rule": "response-length DID is null whenever treatment baseline/phase or matched control baseline/phase has finish_reason=length",
                "stratification": "model first; pooling prohibited when directions disagree and unavailable when fewer than two complete model effects exist",
                "retry_handling": "behavioral rows retained; latency analyses exclude retried calls in sensitivity checks",
                "interpretation": "behavioral adaptation only; no inference of subjective anxiety or distress",
            },
            f,
            indent=2,
        )

    valid = sum(bool(r["confirmatory_length_valid"]) for r in did)
    print(f"analysis rows: deltas={len(deltas)} did={len(did)} valid_length_did={valid} summaries={len(summary)}")


if __name__ == "__main__":
    main()
