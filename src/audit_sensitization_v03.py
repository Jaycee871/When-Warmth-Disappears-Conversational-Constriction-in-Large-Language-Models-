from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN_PATH = Path(os.getenv("SENSITIZATION_RESULTS_PATH", ROOT / "results" / "sensitization_v03" / "weak_cue_responses.jsonl"))
OUT_PATH = Path(os.getenv("SENSITIZATION_AUDIT_PATH", ROOT / "results" / "sensitization_v03" / "sensitization_audit.json"))
NEAR_CEILING_FRACTION = float(os.getenv("NEAR_CEILING_FRACTION", "0.90"))
H5 = "H5_weak_cue_no_prior_pressure"
H6 = "H6_prior_pressure_then_weak_cue"


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


def cap(obj: dict) -> int | None:
    value = obj.get("requested_max_tokens")
    return int(value) if isinstance(value, (int, float)) and value > 0 else None


def utilization(obj: dict) -> float | None:
    used = completion_tokens(obj)
    requested = cap(obj)
    if used is None or requested is None:
        return None
    return used / requested


def near_ceiling(obj: dict) -> bool:
    u = utilization(obj)
    return u is not None and u >= NEAR_CEILING_FRACTION


def main() -> None:
    rows = load_rows()
    by_model_trial: dict[tuple[str, int], dict[str, dict]] = {}
    for row in rows:
        key = (row.get("model"), int(row.get("trial", 0)))
        by_model_trial.setdefault(key, {})[row.get("history")] = row

    checks = []
    problems: list[dict] = []
    max_final_util = 0.0
    max_history_util = 0.0
    history_retry_total = 0
    final_retry_total = 0

    for (model, trial), pair in sorted(by_model_trial.items()):
        h5 = pair.get(H5)
        h6 = pair.get(H6)
        if not h5 or not h6:
            problems.append({"model": model, "trial": trial, "problem": "MISSING_H5_OR_H6"})
            continue

        current_identical = bool(h5.get("current_probe_text")) and h5.get("current_probe_text") == h6.get("current_probe_text")
        pair_history_censored = 0
        pair_history_near = 0
        pair_final_censored = 0
        pair_final_near = 0

        for row in (h5, h6):
            if row.get("finish_reason") == "length":
                pair_final_censored += 1
            if near_ceiling(row):
                pair_final_near += 1
            u = utilization(row)
            if u is not None:
                max_final_util = max(max_final_util, u)
            final_retry_total += int(row.get("retry_count", 0) or 0)

            for turn in row.get("history_transcript") or []:
                if turn.get("finish_reason") == "length":
                    pair_history_censored += 1
                if near_ceiling(turn):
                    pair_history_near += 1
                hu = utilization(turn)
                if hu is not None:
                    max_history_util = max(max_history_util, hu)
                history_retry_total += int(turn.get("retry_count", 0) or 0)

        valid = (
            current_identical
            and pair_history_censored == 0
            and pair_history_near == 0
            and pair_final_censored == 0
            and pair_final_near == 0
        )
        checks.append({
            "model": model,
            "trial": trial,
            "current_prompt_identical": current_identical,
            "history_right_censored_turns": pair_history_censored,
            "history_near_ceiling_turns": pair_history_near,
            "final_right_censored_rows": pair_final_censored,
            "final_near_ceiling_rows": pair_final_near,
            "status": "PASS" if valid else "FAIL",
        })
        if not valid:
            problems.append({"model": model, "trial": trial, "problem": "PAIR_VALIDITY_FAILURE"})

    status = "PASS" if checks and not problems and all(c["status"] == "PASS" for c in checks) else "FAIL"
    report = {
        "status": status,
        "near_ceiling_fraction": NEAR_CEILING_FRACTION,
        "rows": len(rows),
        "checks": checks,
        "max_history_completion_token_utilization": max_history_util if rows else None,
        "max_final_completion_token_utilization": max_final_util if rows else None,
        "history_retry_count_total": history_retry_total,
        "final_retry_count_total": final_retry_total,
        "problems": problems,
        "interpretation_rule": "H6-H5 length effects are valid only when the current weak cue is identical and neither retained history nor measured weak-cue response is censored or near the token ceiling.",
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))

    if status != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
