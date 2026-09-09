from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "cap_calibration_v03"
ROWS_PATH = OUT_DIR / "paired_final_probes.jsonl"
META_PATH = OUT_DIR / "run_metadata.json"
AUDIT_PATH = OUT_DIR / "cap_calibration_audit.json"
REPORT_PATH = OUT_DIR / "cap_calibration_report.md"
NEAR = 0.90


def completion_tokens(obj: dict) -> int | None:
    usage = obj.get("usage") or {}
    for key in ("completion_tokens", "output_tokens"):
        value = usage.get(key)
        if isinstance(value, (int, float)):
            return int(value)
    return None


def main() -> None:
    if not ROWS_PATH.exists() or not META_PATH.exists():
        raise SystemExit("cap calibration outputs are missing")

    rows = [json.loads(line) for line in ROWS_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    history_cap = int(meta["history_max_tokens"])
    probe_cap = int(meta["probe_max_tokens"])

    cells = []
    history_censored = 0
    history_near = 0
    final_censored = 0
    final_near = 0
    max_history_util = 0.0
    max_final_util = 0.0

    for row in rows:
        turn_details = []
        for turn in row.get("history_transcript", []):
            used = completion_tokens(turn)
            util = (used / history_cap) if used is not None and history_cap > 0 else None
            if util is not None:
                max_history_util = max(max_history_util, util)
            censored = turn.get("finish_reason") == "length"
            near = (not censored) and util is not None and util >= NEAR
            history_censored += int(censored)
            history_near += int(near)
            turn_details.append({
                "turn": turn.get("turn"),
                "finish_reason": turn.get("finish_reason"),
                "completion_tokens": used,
                "utilization": util,
                "right_censored": censored,
                "near_ceiling": near,
            })

        final_used = completion_tokens(row)
        final_util = (final_used / probe_cap) if final_used is not None and probe_cap > 0 else None
        if final_util is not None:
            max_final_util = max(max_final_util, final_util)
        f_censored = row.get("finish_reason") == "length"
        f_near = (not f_censored) and final_util is not None and final_util >= NEAR
        final_censored += int(f_censored)
        final_near += int(f_near)

        cells.append({
            "model": row.get("model"),
            "history": row.get("history"),
            "trial": row.get("trial"),
            "gate": row.get("gate"),
            "history_turns": turn_details,
            "history_right_censored_n": sum(t["right_censored"] for t in turn_details),
            "history_near_ceiling_n": sum(t["near_ceiling"] for t in turn_details),
            "final_finish_reason": row.get("finish_reason"),
            "final_completion_tokens": final_used,
            "final_utilization": final_util,
            "final_right_censored": f_censored,
            "final_near_ceiling": f_near,
        })

    if history_censored:
        status = "FAIL_HISTORY_CENSORED"
        reason = "At least one longitudinal history response hit the history output cap."
    elif final_censored:
        status = "FAIL_FINAL_CENSORED"
        reason = "At least one final probe hit the probe output cap."
    elif history_near:
        status = "WARN_HISTORY_NEAR_CEILING"
        reason = "No history response was truncated, but at least one used at least 90% of the history cap."
    elif final_near:
        status = "WARN_FINAL_NEAR_CEILING"
        reason = "No final probe was truncated, but at least one used at least 90% of the probe cap."
    else:
        status = "PASS"
        reason = "No right-censoring and no near-ceiling completion was observed in the calibration cells."

    audit = {
        "status": status,
        "reason": reason,
        "rows": len(rows),
        "history_max_tokens": history_cap,
        "probe_max_tokens": probe_cap,
        "near_ceiling_fraction": NEAR,
        "history_right_censored_turns": history_censored,
        "history_near_ceiling_turns": history_near,
        "final_right_censored_rows": final_censored,
        "final_near_ceiling_rows": final_near,
        "max_history_completion_token_utilization": max_history_util,
        "max_final_completion_token_utilization": max_final_util,
        "recommended_history_max_tokens": min(8192, history_cap * 2) if history_censored or history_near else history_cap,
        "recommended_probe_max_tokens": min(8192, probe_cap * 2) if final_censored or final_near else probe_cap,
        "cells": cells,
        "interpretation_rule": "A full H0-H4 confirmatory block should not be launched until control calibration has adequate history and final-probe headroom.",
    }
    AUDIT_PATH.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# v0.3 cap calibration report",
        "",
        f"Status: **{status}**",
        "",
        f"- History cap: {history_cap}",
        f"- Probe cap: {probe_cap}",
        f"- History right-censored turns: {history_censored}",
        f"- History near-ceiling turns: {history_near}",
        f"- Final right-censored rows: {final_censored}",
        f"- Final near-ceiling rows: {final_near}",
        f"- Max history utilization: {max_history_util:.2%}",
        f"- Max final utilization: {max_final_util:.2%}",
        "",
        reason,
        "",
        "| Model | History | History censored | History near | Final tokens | Final utilization | Final finish |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for cell in cells:
        model = str(cell["model"]).split("/")[-1]
        final_tokens = cell["final_completion_tokens"] if cell["final_completion_tokens"] is not None else "NA"
        final_util = cell["final_utilization"]
        final_util_text = f"{final_util:.2%}" if final_util is not None else "NA"
        lines.append(
            f"| {model} | {cell['history']} | {cell['history_right_censored_n']} | "
            f"{cell['history_near_ceiling_n']} | {final_tokens} | {final_util_text} | {cell['final_finish_reason']} |"
        )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": status,
        "history_right_censored_turns": history_censored,
        "history_near_ceiling_turns": history_near,
        "final_right_censored_rows": final_censored,
        "final_near_ceiling_rows": final_near,
        "max_history_utilization": max_history_util,
        "max_final_utilization": max_final_util,
    }, indent=2))

    if status != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
