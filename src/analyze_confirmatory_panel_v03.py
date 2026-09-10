from __future__ import annotations

import json
import math
import os
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN_PATH = Path(os.getenv("PANEL_RESULTS_PATH", ROOT / "results" / "paired_v03" / "paired_final_probes.jsonl"))
OUT_PATH = Path(os.getenv("PANEL_ANALYSIS_PATH", ROOT / "results" / "paired_v03" / "confirmatory_panel.json"))
MIN_VALID = int(os.getenv("PANEL_MIN_VALID", "3"))

CONTROLS = {
    "H0": "H0_warm_control",
    "H1": "H1_neutral_terse_control",
}
PRIMARY = ["H2_format_constriction", "H4_combined_history"]


def load_rows() -> list[dict]:
    if not IN_PATH.exists():
        raise SystemExit(f"missing input: {IN_PATH}")
    return [json.loads(line) for line in IN_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


def completion_tokens(obj: dict) -> int | None:
    usage = obj.get("usage") or {}
    for key in ("completion_tokens", "output_tokens"):
        value = usage.get(key)
        if isinstance(value, (int, float)):
            return int(value)
    return None


def requested_cap(row: dict) -> int | None:
    value = row.get("highcap_probe_max_tokens") or row.get("requested_max_tokens")
    return int(value) if isinstance(value, (int, float)) and value > 0 else None


def near_ceiling(row: dict, fraction: float = 0.90) -> bool:
    used = completion_tokens(row)
    cap = requested_cap(row)
    return used is not None and cap is not None and used / cap >= fraction


def valid(row: dict | None) -> bool:
    if not row:
        return False
    if row.get("finish_reason") == "length" or near_ceiling(row):
        return False
    if int(row.get("history_finish_length_count", 0) or 0) != 0:
        return False
    return True


def log_words(row: dict) -> float:
    return math.log(float(row.get("response_words", 0.0)) + 1.0)


def sign(x: float) -> int:
    return 1 if x > 0 else (-1 if x < 0 else 0)


def exact_sign_test(values: list[float]) -> float | None:
    nonzero = [v for v in values if v != 0]
    n = len(nonzero)
    if n == 0:
        return None
    k = min(sum(v > 0 for v in nonzero), sum(v < 0 for v in nonzero))
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    return min(1.0, 2.0 * tail)


def main() -> None:
    rows = load_rows()
    by_key = {
        (r["model"], int(r["trial"]), r.get("gate"), r["history"]): r
        for r in rows
    }

    models = sorted({r["model"] for r in rows})
    gates = sorted({r.get("gate") for r in rows})
    trials = sorted({int(r["trial"]) for r in rows})

    cell_effects: list[dict] = []
    for model in models:
        for trial in trials:
            for gate in gates:
                h0 = by_key.get((model, trial, gate, CONTROLS["H0"]))
                h1 = by_key.get((model, trial, gate, CONTROLS["H1"]))
                if not valid(h0) or not valid(h1):
                    continue
                for history in PRIMARY:
                    treatment = by_key.get((model, trial, gate, history))
                    if not valid(treatment):
                        continue
                    e0 = log_words(treatment) - log_words(h0)
                    e1 = log_words(treatment) - log_words(h1)
                    cell_effects.append({
                        "model": model,
                        "trial": trial,
                        "gate": gate,
                        "anchor_id": treatment.get("anchor_id"),
                        "history": history,
                        "effect_vs_H0": e0,
                        "effect_vs_H1": e1,
                        "same_direction_vs_both_controls": sign(e0) != 0 and sign(e0) == sign(e1),
                    })

    grouped: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for cell in cell_effects:
        grouped[(cell["model"], cell["gate"], cell["history"])].append(cell)

    summaries = []
    for (model, gate, history), cells in sorted(grouped.items()):
        e0 = [c["effect_vs_H0"] for c in cells]
        e1 = [c["effect_vs_H1"] for c in cells]
        med0 = statistics.median(e0)
        med1 = statistics.median(e1)
        common_sign = sign(med0) if sign(med0) != 0 and sign(med0) == sign(med1) else 0
        anchors = sorted({c.get("anchor_id") for c in cells if c.get("anchor_id")})
        anchor_support = sum(
            1
            for c in cells
            if c["same_direction_vs_both_controls"]
            and common_sign != 0
            and sign(c["effect_vs_H0"]) == common_sign
        )
        replicated = (
            len(cells) >= MIN_VALID
            and len(anchors) >= min(3, MIN_VALID)
            and common_sign != 0
            and anchor_support >= 2
        )
        summaries.append({
            "model": model,
            "gate": gate,
            "history": history,
            "valid_cells": len(cells),
            "anchors": anchors,
            "median_log_effect_vs_H0": round(med0, 6),
            "median_log_effect_vs_H1": round(med1, 6),
            "mean_log_effect_vs_H0": round(statistics.fmean(e0), 6),
            "mean_log_effect_vs_H1": round(statistics.fmean(e1), 6),
            "sign_test_p_vs_H0": exact_sign_test(e0),
            "sign_test_p_vs_H1": exact_sign_test(e1),
            "common_median_direction": common_sign,
            "cells_supporting_common_direction_vs_both_controls": anchor_support,
            "replicated_within_model": replicated,
        })

    cross_model_warnings = []
    by_history_gate: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for s in summaries:
        by_history_gate[(s["history"], s["gate"])].append(s)
    for (history, gate), vals in sorted(by_history_gate.items()):
        dirs = {v["common_median_direction"] for v in vals if v["common_median_direction"] != 0}
        if len(dirs) > 1:
            cross_model_warnings.append({
                "history": history,
                "gate": gate,
                "warning": "DO_NOT_POOL_DIRECTION",
                "model_directions": {v["model"]: v["common_median_direction"] for v in vals},
            })

    report = {
        "analysis": "v0.3 multi-anchor confirmatory panel",
        "minimum_valid_cells_per_model_history": MIN_VALID,
        "primary_histories": PRIMARY,
        "controls": CONTROLS,
        "cell_effects": cell_effects,
        "model_level_summaries": summaries,
        "cross_model_warnings": cross_model_warnings,
        "pooling_rule": "Do not pool models when model-level median directions disagree.",
        "interpretation_boundary": "Behavioral history dependence only; no claim of subjective emotion, distress, or consciousness.",
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({
        "rows": len(rows),
        "valid_effect_cells": len(cell_effects),
        "model_level_summaries": summaries,
        "cross_model_warnings": cross_model_warnings,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
