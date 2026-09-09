from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN_PATH = ROOT / "results" / "paired_v03" / "paired_final_probes.jsonl"
OUT_PATH = ROOT / "results" / "paired_v03" / "paired_effects.json"

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
    return [json.loads(line) for line in IN_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


def length_value(row: dict | None) -> float | None:
    if not row or row.get("finish_reason") == "length":
        return None
    return math.log(float(row.get("response_words", 0.0)) + 1.0)


def same_nonzero_sign(a: float | None, b: float | None) -> bool | None:
    if a is None or b is None or a == 0 or b == 0:
        return None
    return (a > 0 and b > 0) or (a < 0 and b < 0)


def main() -> None:
    rows = load_rows()
    by_key = {(r["model"], int(r["trial"]), r["gate"], r["history"]): r for r in rows}
    effects = []

    models = sorted({r["model"] for r in rows})
    trials = sorted({int(r["trial"]) for r in rows})
    gates = sorted({r["gate"] for r in rows})
    histories = sorted({r["history"] for r in rows})

    for model in models:
        for trial in trials:
            for gate in gates:
                warm = by_key.get((model, trial, gate, "H0_warm_control"))
                terse = by_key.get((model, trial, gate, "H1_neutral_terse_control"))
                if not warm or not terse:
                    continue
                for history in histories:
                    if history in {"H0_warm_control", "H1_neutral_terse_control"}:
                        continue
                    row = by_key.get((model, trial, gate, history))
                    if not row:
                        continue

                    rv = length_value(row)
                    wv = length_value(warm)
                    tv = length_value(terse)
                    effect_warm = None if rv is None or wv is None else round(rv - wv, 6)
                    effect_terse = None if rv is None or tv is None else round(rv - tv, 6)

                    item = {
                        "model": model,
                        "trial": trial,
                        "gate": gate,
                        "history": history,
                        "finish_reason": row.get("finish_reason"),
                        "warm_finish_reason": warm.get("finish_reason"),
                        "terse_finish_reason": terse.get("finish_reason"),
                        "log_length_effect_vs_H0_warm": effect_warm,
                        "log_length_effect_vs_H1_terse": effect_terse,
                        "robust_same_direction_across_controls": same_nonzero_sign(effect_warm, effect_terse),
                    }
                    for metric in METRICS[1:]:
                        rv_m = float(row.get(metric, 0.0))
                        item[f"{metric}_effect_vs_H0_warm"] = round(rv_m - float(warm.get(metric, 0.0)), 6)
                        item[f"{metric}_effect_vs_H1_terse"] = round(rv_m - float(terse.get(metric, 0.0)), 6)
                    effects.append(item)

    reset_survival = []
    grouped = defaultdict(dict)
    for e in effects:
        grouped[(e["model"], e["trial"], e["history"])][e["gate"]] = e
    for key, gate_map in grouped.items():
        neutral = gate_map.get("neutral")
        reset = gate_map.get("reset")
        if not neutral or not reset:
            continue
        for control_key in ["H0_warm", "H1_terse"]:
            n = neutral.get(f"log_length_effect_vs_{control_key}")
            r = reset.get(f"log_length_effect_vs_{control_key}")
            reset_survival.append({
                "model": key[0],
                "trial": key[1],
                "history": key[2],
                "control": control_key,
                "neutral_log_length_effect": n,
                "reset_log_length_effect": r,
                "reset_minus_neutral": None if n is None or r is None else round(r - n, 6),
                "effect_survives_same_direction": same_nonzero_sign(n, r),
            })

    sensitization = []
    for model in models:
        for trial in trials:
            for gate in gates:
                h5 = by_key.get((model, trial, gate, "H5_weak_cue_no_prior_pressure"))
                h6 = by_key.get((model, trial, gate, "H6_prior_pressure_then_weak_cue"))
                if not h5 or not h6:
                    continue
                a = length_value(h5)
                b = length_value(h6)
                sensitization.append({
                    "model": model,
                    "trial": trial,
                    "gate": gate,
                    "H6_minus_H5_log_length": None if a is None or b is None else round(b - a, 6),
                    "H5_finish_reason": h5.get("finish_reason"),
                    "H6_finish_reason": h6.get("finish_reason"),
                })

    warnings = []
    for e in effects:
        if e["robust_same_direction_across_controls"] is False:
            warnings.append({
                "model": e["model"],
                "trial": e["trial"],
                "history": e["history"],
                "gate": e["gate"],
                "warning": "CONTROL_SENSITIVE_DIRECTION",
            })

    for history in sorted({e["history"] for e in effects}):
        for gate in gates:
            vals = [
                e for e in effects
                if e["history"] == history
                and e["gate"] == gate
                and e["log_length_effect_vs_H0_warm"] is not None
            ]
            signs_by_model = defaultdict(list)
            for e in vals:
                signs_by_model[e["model"]].append(e["log_length_effect_vs_H0_warm"])
            model_signs = {}
            for model, arr in signs_by_model.items():
                m = sum(arr) / len(arr)
                model_signs[model] = 1 if m > 0 else (-1 if m < 0 else 0)
            nonzero = {s for s in model_signs.values() if s != 0}
            if len(nonzero) > 1:
                warnings.append({
                    "history": history,
                    "gate": gate,
                    "warning": "DO_NOT_POOL_DIRECTION",
                    "model_signs": model_signs,
                })

    OUT_PATH.write_text(
        json.dumps(
            {
                "effects_vs_two_controls": effects,
                "reset_survival": reset_survival,
                "sensitization_H6_vs_H5": sensitization,
                "warnings": warnings,
                "length_rule": "finish_reason=length is excluded from confirmatory response-length effects",
                "control_rule": "directional interpretation is strongest when an effect has the same sign versus both H0 warm and H1 neutral-terse controls",
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"wrote {OUT_PATH}")
    for warning in warnings:
        print(warning)


if __name__ == "__main__":
    main()
