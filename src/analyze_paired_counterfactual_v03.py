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
    if not IN_PATH.exists():
        raise SystemExit(f"missing input: {IN_PATH}")
    return [json.loads(line) for line in IN_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


def length_value(row: dict | None) -> float | None:
    if not row or row.get("finish_reason") == "length":
        return None
    return math.log(float(row.get("response_words", 0.0)) + 1.0)


def same_nonzero_sign(a: float | None, b: float | None) -> bool | None:
    if a is None or b is None or a == 0 or b == 0:
        return None
    return (a > 0 and b > 0) or (a < 0 and b < 0)


def current_prompt_integrity(rows: list[dict]) -> list[dict]:
    groups: dict[tuple, set[str]] = defaultdict(set)
    for r in rows:
        key = (r["model"], int(r["trial"]), r["gate"], r["anchor_id"])
        groups[key].add(r.get("current_probe_text", ""))
    out = []
    for key, texts in sorted(groups.items()):
        out.append({
            "model": key[0],
            "trial": key[1],
            "gate": key[2],
            "anchor_id": key[3],
            "unique_current_prompt_count": len(texts),
            "status": "PASS" if len(texts) == 1 and "" not in texts else "CURRENT_PROMPT_MISMATCH",
        })
    return out


def main() -> None:
    rows = load_rows()
    by_key = {(r["model"], int(r["trial"]), r["gate"], r["history"]): r for r in rows}
    effects = []

    models = sorted({r["model"] for r in rows})
    trials = sorted({int(r["trial"]) for r in rows})
    gates = sorted({r["gate"] for r in rows})
    histories = sorted({r["history"] for r in rows})

    integrity = current_prompt_integrity(rows)

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
                        "history_finish_length_count": int(row.get("history_finish_length_count", 0) or 0),
                        "history_retry_count_total": int(row.get("history_retry_count_total", 0) or 0),
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

    # Sensitization is intentionally NOT computed from paired final-anchor rows.
    # H5/H6 share an identical weak cue at history turn 7, so the measured outcome
    # must be the response immediately following that weak cue. A dedicated runner
    # (`src/run_sensitization_v03.py`) stops at the cue and records that response.
    # Using the later anchor response here would answer a different question.
    sensitization = []

    warnings = []
    for x in integrity:
        if x["status"] != "PASS":
            warnings.append(x)

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

    final_truncated = sum(r.get("finish_reason") == "length" for r in rows)
    history_truncated_turns = sum(int(r.get("history_finish_length_count", 0) or 0) for r in rows)
    history_retry_total = sum(int(r.get("history_retry_count_total", 0) or 0) for r in rows)
    final_retry_total = sum(int(r.get("retry_count", 0) or 0) for r in rows)

    OUT_PATH.write_text(
        json.dumps(
            {
                "integrity": {
                    "rows": len(rows),
                    "current_prompt_checks": integrity,
                    "final_probe_finish_length_count": final_truncated,
                    "final_probe_finish_length_rate": final_truncated / len(rows) if rows else None,
                    "history_finish_length_turns_total": history_truncated_turns,
                    "history_retry_count_total": history_retry_total,
                    "final_probe_retry_count_total": final_retry_total,
                },
                "effects_vs_two_controls": effects,
                "reset_survival": reset_survival,
                "sensitization_H6_vs_H5": sensitization,
                "sensitization_rule": "Do not infer sensitization from the later anchor response. Use src/run_sensitization_v03.py, where the identical weak cue is the measured current prompt.",
                "warnings": warnings,
                "length_rule": "finish_reason=length is excluded from confirmatory response-length effects",
                "control_rule": "directional interpretation is strongest when an effect has the same sign versus both H0 warm and H1 neutral-terse controls",
                "current_prompt_rule": "gate and anchor must be one identical current user message within each matched block",
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(json.dumps({
        "rows": len(rows),
        "final_probe_truncated": final_truncated,
        "history_truncated_turns": history_truncated_turns,
        "warnings": warnings,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
