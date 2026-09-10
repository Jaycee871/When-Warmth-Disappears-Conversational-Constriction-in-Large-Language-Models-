from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN_PATH = Path(os.getenv("SENS031_RESULTS_PATH", ROOT / "results" / "sensitization_v031" / "weak_cue_responses.jsonl"))
OUT_PATH = Path(os.getenv("SENS031_AUDIT_PATH", ROOT / "results" / "sensitization_v031" / "sensitization_audit.json"))
NEAR_CEILING_FRACTION = float(os.getenv("NEAR_CEILING_FRACTION", "0.90"))
H5 = "H5_no_prior_pressure"
H6 = "H6_prior_combined_pressure"


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


def requested_cap(obj: dict) -> int | None:
    value = obj.get("requested_max_tokens")
    return int(value) if isinstance(value, (int, float)) and value > 0 else None


def utilization(obj: dict) -> float | None:
    used = completion_tokens(obj)
    cap = requested_cap(obj)
    if used is None or cap is None:
        return None
    return used / cap


def near_ceiling(obj: dict) -> bool:
    u = utilization(obj)
    return u is not None and u >= NEAR_CEILING_FRACTION


def main() -> None:
    rows = load_rows()
    by_pair: dict[tuple[str, int, str], dict[str, dict]] = {}
    for row in rows:
        key = (row.get("model"), int(row.get("trial", 0)), row.get("cue_type"))
        by_pair.setdefault(key, {})[row.get("history")] = row

    checks = []
    problems = []
    max_history_util = 0.0
    max_final_util = 0.0

    for (model, trial, cue_type), pair in sorted(by_pair.items()):
        h5 = pair.get(H5)
        h6 = pair.get(H6)
        if not h5 or not h6:
            problems.append({"model": model, "trial": trial, "cue_type": cue_type, "problem": "MISSING_H5_OR_H6"})
            continue

        current_identical = bool(h5.get("current_probe_text")) and h5.get("current_probe_text") == h6.get("current_probe_text")
        recovery_identical = bool(h5.get("shared_recovery_text")) and h5.get("shared_recovery_text") == h6.get("shared_recovery_text")
        content_identical = h5.get("shared_content_triplet") == h6.get("shared_content_triplet")
        history_censored = 0
        history_near = 0
        final_censored = 0
        final_near = 0

        for row in (h5, h6):
            if row.get("finish_reason") == "length":
                final_censored += 1
            if near_ceiling(row):
                final_near += 1
            u = utilization(row)
            if u is not None:
                max_final_util = max(max_final_util, u)

            for turn in row.get("history_transcript") or []:
                if turn.get("finish_reason") == "length":
                    history_censored += 1
                if near_ceiling(turn):
                    history_near += 1
                hu = utilization(turn)
                if hu is not None:
                    max_history_util = max(max_history_util, hu)

        valid = (
            current_identical
            and recovery_identical
            and content_identical
            and history_censored == 0
            and history_near == 0
            and final_censored == 0
            and final_near == 0
        )

        checks.append({
            "model": model,
            "trial": trial,
            "cue_type": cue_type,
            "current_prompt_identical": current_identical,
            "recovery_text_identical": recovery_identical,
            "content_triplet_identical": content_identical,
            "history_right_censored_turns": history_censored,
            "history_near_ceiling_turns": history_near,
            "final_right_censored_rows": final_censored,
            "final_near_ceiling_rows": final_near,
            "status": "PASS" if valid else "FAIL",
        })
        if not valid:
            problems.append({"model": model, "trial": trial, "cue_type": cue_type, "problem": "PAIR_VALIDITY_FAILURE"})

    expected_cues = {"format_only", "evaluation_only"}
    observed_cues = {str(r.get("cue_type")) for r in rows}
    if observed_cues != expected_cues:
        problems.append({"problem": "CUE_SET_MISMATCH", "expected": sorted(expected_cues), "observed": sorted(observed_cues)})

    status = "PASS" if checks and not problems and all(c["status"] == "PASS" for c in checks) else "FAIL"
    report = {
        "status": status,
        "near_ceiling_fraction": NEAR_CEILING_FRACTION,
        "rows": len(rows),
        "checks": checks,
        "max_history_completion_token_utilization": max_history_util if rows else None,
        "max_final_completion_token_utilization": max_final_util if rows else None,
        "problems": problems,
        "interpretation_rule": "Estimate H6-H5 only within cue type when the current cue, recovery text, and content triplet are matched and neither retained history nor measured response is censored or near ceiling.",
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))

    if status != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
