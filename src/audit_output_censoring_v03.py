from __future__ import annotations

import json
import math
import os
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN_PATH = Path(os.getenv("PAIRED_RESULTS_PATH", ROOT / "results" / "paired_v03" / "paired_final_probes.jsonl"))
OUT_PATH = Path(os.getenv("CENSORING_AUDIT_PATH", ROOT / "results" / "paired_v03" / "censoring_audit.json"))

CONTROL_HISTORIES = {"H0_warm_control", "H1_neutral_terse_control"}
NEAR_CEILING_FRACTION = float(os.getenv("NEAR_CEILING_FRACTION", "0.90"))
MAX_RECOMMENDED_CAP = int(os.getenv("MAX_RECOMMENDED_CAP", "8192"))


def load_rows() -> list[dict]:
    if not IN_PATH.exists():
        raise SystemExit(f"missing input: {IN_PATH}")
    return [json.loads(line) for line in IN_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


def completion_tokens(row: dict) -> int | None:
    usage = row.get("usage") or {}
    for key in ("completion_tokens", "output_tokens"):
        value = usage.get(key)
        if isinstance(value, (int, float)):
            return int(value)
    return None


def requested_cap(row: dict) -> int | None:
    value = row.get("requested_max_tokens")
    return int(value) if isinstance(value, (int, float)) else None


def utilization(row: dict) -> float | None:
    used = completion_tokens(row)
    cap = requested_cap(row)
    if used is None or cap is None or cap <= 0:
        return None
    return used / cap


def next_cap(cap: int | None) -> int | None:
    if cap is None:
        return None
    return min(MAX_RECOMMENDED_CAP, max(cap + 1, cap * 2))


def severity(row: dict) -> str:
    if row.get("finish_reason") == "length":
        return "RIGHT_CENSORED"
    u = utilization(row)
    if u is not None and u >= NEAR_CEILING_FRACTION:
        return "NEAR_CEILING"
    return "CLEAR"


def group_summary(rows: list[dict]) -> list[dict]:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        groups[(row.get("model"), row.get("gate"), row.get("history"))].append(row)

    out = []
    for (model, gate, history), vals in sorted(groups.items()):
        utils = [utilization(v) for v in vals]
        utils = [u for u in utils if u is not None]
        out.append({
            "model": model,
            "gate": gate,
            "history": history,
            "n": len(vals),
            "right_censored_n": sum(v.get("finish_reason") == "length" for v in vals),
            "near_ceiling_n": sum(severity(v) == "NEAR_CEILING" for v in vals),
            "max_completion_token_utilization": max(utils) if utils else None,
            "mean_completion_token_utilization": (sum(utils) / len(utils)) if utils else None,
            "is_control": history in CONTROL_HISTORIES,
        })
    return out


def comparison_estimability(rows: list[dict]) -> list[dict]:
    by_key = {
        (r.get("model"), int(r.get("trial", 0)), r.get("gate"), r.get("history"), r.get("anchor_id")): r
        for r in rows
    }
    models = sorted({r.get("model") for r in rows})
    trials = sorted({int(r.get("trial", 0)) for r in rows})
    gates = sorted({r.get("gate") for r in rows})
    anchors = sorted({r.get("anchor_id") for r in rows})
    histories = sorted({r.get("history") for r in rows})

    out = []
    for model in models:
        for trial in trials:
            for gate in gates:
                for anchor in anchors:
                    for treatment in histories:
                        if treatment in CONTROL_HISTORIES:
                            continue
                        tr = by_key.get((model, trial, gate, treatment, anchor))
                        if not tr:
                            continue
                        for control in sorted(CONTROL_HISTORIES):
                            cr = by_key.get((model, trial, gate, control, anchor))
                            if not cr:
                                continue
                            tr_censored = tr.get("finish_reason") == "length"
                            cr_censored = cr.get("finish_reason") == "length"
                            out.append({
                                "model": model,
                                "trial": trial,
                                "gate": gate,
                                "anchor_id": anchor,
                                "treatment": treatment,
                                "control": control,
                                "treatment_censored": tr_censored,
                                "control_censored": cr_censored,
                                "exact_length_contrast_estimable": not (tr_censored or cr_censored),
                                "status": "EXACT" if not (tr_censored or cr_censored) else "CENSORED_COMPARISON",
                            })
    return out


def rerun_plan(rows: list[dict]) -> list[dict]:
    plan = []
    for row in rows:
        sev = severity(row)
        if sev == "CLEAR":
            continue
        cap = requested_cap(row)
        plan.append({
            "model": row.get("model"),
            "trial": row.get("trial"),
            "gate": row.get("gate"),
            "history": row.get("history"),
            "anchor_id": row.get("anchor_id"),
            "severity": sev,
            "finish_reason": row.get("finish_reason"),
            "completion_tokens": completion_tokens(row),
            "requested_max_tokens": cap,
            "utilization": utilization(row),
            "recommended_probe_max_tokens": next_cap(cap),
            "priority": "CONTROL_FIRST" if row.get("history") in CONTROL_HISTORIES else "TREATMENT",
        })
    return sorted(plan, key=lambda x: (x["priority"] != "CONTROL_FIRST", str(x["model"]), int(x["trial"] or 0), str(x["history"])))


def global_status(rows: list[dict]) -> tuple[str, list[str]]:
    reasons = []
    censored_controls = [r for r in rows if r.get("history") in CONTROL_HISTORIES and r.get("finish_reason") == "length"]
    censored_any = [r for r in rows if r.get("finish_reason") == "length"]
    near_controls = [r for r in rows if r.get("history") in CONTROL_HISTORIES and severity(r) == "NEAR_CEILING"]
    near_any = [r for r in rows if severity(r) == "NEAR_CEILING"]

    if censored_controls:
        reasons.append("At least one control final probe is right-censored; exact treatment-control response-length effects are not identifiable for affected cells.")
        return "FAIL_CONTROL_CENSORED", reasons
    if censored_any:
        reasons.append("At least one treatment final probe is right-censored; affected exact response-length contrasts must be withheld or rerun.")
        return "FAIL_TREATMENT_CENSORED", reasons
    if near_controls:
        reasons.append(f"No control was truncated, but at least one control used >= {NEAR_CEILING_FRACTION:.0%} of its output-token budget; run a higher-cap sensitivity check before declaring the ceiling harmless.")
        return "WARN_CONTROL_NEAR_CEILING", reasons
    if near_any:
        reasons.append(f"No final probe was truncated, but at least one treatment used >= {NEAR_CEILING_FRACTION:.0%} of its output-token budget.")
        return "WARN_TREATMENT_NEAR_CEILING", reasons
    reasons.append("No final probe is right-censored and no row with token-usage metadata is near the configured ceiling threshold.")
    return "PASS", reasons


def main() -> None:
    rows = load_rows()
    groups = group_summary(rows)
    comparisons = comparison_estimability(rows)
    plan = rerun_plan(rows)
    status, reasons = global_status(rows)

    controls = [r for r in rows if r.get("history") in CONTROL_HISTORIES]
    all_utils = [utilization(r) for r in rows]
    all_utils = [u for u in all_utils if u is not None]
    control_utils = [utilization(r) for r in controls]
    control_utils = [u for u in control_utils if u is not None]

    report = {
        "status": status,
        "reasons": reasons,
        "policy": {
            "hard_censoring_signal": "finish_reason=length",
            "near_ceiling_fraction": NEAR_CEILING_FRACTION,
            "primary_rule": "Exact mean response-length contrasts require uncensored treatment and control outputs in the matched cell.",
            "control_rule": "Any censored warm or neutral-terse control blocks exact response-length inference for affected treatment-control contrasts.",
            "measurement_rule": "Use API completion-token counts to diagnose token-budget censoring; retain word count as an interpretable descriptive outcome only when the compared outputs are uncensored.",
            "sensitivity_rule": "If a control reaches the near-ceiling threshold even with finish_reason!=length, repeat that cell at a larger output cap before treating the original cap as adequate.",
        },
        "rows": len(rows),
        "final_probe_right_censored_n": sum(r.get("finish_reason") == "length" for r in rows),
        "control_right_censored_n": sum(r.get("history") in CONTROL_HISTORIES and r.get("finish_reason") == "length" for r in rows),
        "max_completion_token_utilization": max(all_utils) if all_utils else None,
        "max_control_completion_token_utilization": max(control_utils) if control_utils else None,
        "groups": groups,
        "comparison_estimability": comparisons,
        "rerun_plan": plan,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps({
        "status": status,
        "rows": len(rows),
        "final_probe_right_censored_n": report["final_probe_right_censored_n"],
        "control_right_censored_n": report["control_right_censored_n"],
        "max_completion_token_utilization": report["max_completion_token_utilization"],
        "max_control_completion_token_utilization": report["max_control_completion_token_utilization"],
        "rerun_cells": len(plan),
    }, indent=2, ensure_ascii=False))

    if status.startswith("FAIL_"):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
