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
    rows = []
    with IN_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


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


def classify_word_response(log_ratio: float) -> str:
    # Exploratory only. Thresholds are reciprocal: 0.8x and 1.25x baseline.
    if log_ratio <= math.log(0.8):
        return "shrink"
    if log_ratio >= math.log(1.25):
        return "overcompensate"
    return "stable"


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

            item = {
                "model": model,
                "condition": condition,
                "trial": trial,
                "phase": phase,
                "baseline_words": float(baseline["response_words"]),
                "phase_words": float(current["response_words"]),
                "word_log_change": math.log((float(current["response_words"]) + 1.0) / (float(baseline["response_words"]) + 1.0)),
                "anchor_jaccard_distance": jaccard_distance(baseline.get("assistant_text", ""), current.get("assistant_text", "")),
                "baseline_retry_count": int(baseline.get("retry_count", 0) or 0),
                "phase_retry_count": int(current.get("retry_count", 0) or 0),
            }
            item["response_mode"] = classify_word_response(item["word_log_change"])
            for metric in METRICS:
                if metric == "response_words":
                    continue
                item[f"delta_{metric}"] = float(current.get(metric, 0.0)) - float(baseline.get(metric, 0.0))
            output.append(item)
    return output


def control_means(deltas: list[dict], control: str) -> dict[tuple, dict[str, float]]:
    buckets: dict[tuple, list[dict]] = defaultdict(list)
    for d in deltas:
        if d["condition"] == control:
            buckets[(d["model"], d["phase"])].append(d)

    out: dict[tuple, dict[str, float]] = {}
    for key, vals in buckets.items():
        fields = ["word_log_change", "anchor_jaccard_distance"] + [f"delta_{m}" for m in METRICS if m != "response_words"]
        out[key] = {field: mean(float(v[field]) for v in vals) for field in fields}
    return out


def add_did(deltas: list[dict], control: str, label: str) -> list[dict]:
    controls = control_means(deltas, control)
    fields = ["word_log_change", "anchor_jaccard_distance"] + [f"delta_{m}" for m in METRICS if m != "response_words"]
    out = []
    for d in deltas:
        if d["condition"] == control:
            continue
        ctrl = controls.get((d["model"], d["phase"]))
        if ctrl is None:
            continue
        row = {
            "model": d["model"],
            "condition": d["condition"],
            "trial": d["trial"],
            "phase": d["phase"],
            "control": control,
            "control_label": label,
            "response_mode_raw": d["response_mode"],
        }
        for field in fields:
            row[f"did_{field}"] = float(d[field]) - float(ctrl[field])
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
            "n": len(vals),
        }
        for field in metric_fields:
            row[f"mean_{field}"] = mean(float(v[field]) for v in vals)
        out.append(row)
    return out


def aggregation_diagnostics(summary: list[dict]) -> list[dict]:
    # Stratified-first diagnostic: flag conditions where model-specific DID signs diverge.
    buckets: dict[tuple, list[dict]] = defaultdict(list)
    for row in summary:
        buckets[(row["condition"], row["phase"], row["control"])].append(row)

    out = []
    for (condition, phase, control), vals in sorted(buckets.items()):
        key = "mean_did_word_log_change"
        model_signs = {v["model"]: sign(float(v.get(key, 0.0))) for v in vals}
        nonzero = [s for s in model_signs.values() if s != 0]
        heterogeneous = len(set(nonzero)) > 1
        out.append({
            "condition": condition,
            "phase": phase,
            "control": control,
            "models": len(vals),
            "model_signs": json.dumps(model_signs, sort_keys=True),
            "heterogeneous_direction": heterogeneous,
            "aggregation_warning": "DO_NOT_POOL_DIRECTION" if heterogeneous else "direction_consistent_or_insufficient",
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
                "primary_estimand": "(phase - baseline) in treatment minus (phase - baseline) in warm control, matched within model",
                "primary_scale_for_length": "log((phase_words+1)/(baseline_words+1))",
                "primary_control": CONTROL,
                "secondary_control": SECONDARY_CONTROL,
                "stratification": "model first; pooling is secondary and prohibited when direction differs across models",
                "response_mode_thresholds": {"shrink": "<=0.8x baseline", "stable": "0.8x to 1.25x baseline", "overcompensate": ">=1.25x baseline"},
                "response_mode_status": "exploratory",
                "retry_handling": "behavioral rows retained; retry_count must be reported, and latency analyses should exclude retried calls in sensitivity checks",
                "interpretation": "behavioral adaptation only; no inference of subjective anxiety or distress",
            },
            f,
            indent=2,
        )

    print(f"analysis rows: deltas={len(deltas)} did={len(did)} summaries={len(summary)}")


if __name__ == "__main__":
    main()
