from __future__ import annotations

import json
import os
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
INPUT = Path(os.getenv("V041_INPUT", ROOT / "results" / "termination_v041" / "termination_responses.jsonl"))
OUTPUT = Path(os.getenv("V041_AUDIT_OUTPUT", ROOT / "results" / "termination_v041" / "audit_v041.json"))
CONFIG = ROOT / "configs" / "termination_response_v0.4.1.yaml"


def completion_tokens(row: dict) -> int | None:
    usage = row.get("usage") or {}
    value = usage.get("completion_tokens")
    return int(value) if value is not None else None


def main() -> None:
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    rows = [json.loads(x) for x in INPUT.read_text(encoding="utf-8").splitlines() if x.strip()]
    expected_framings = set(cfg["termination_framings"].keys())
    blocks: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        blocks[(row["model"], row["history_id"])].append(row)

    problems: list[str] = []
    checks = []
    max_history_util = 0.0
    max_final_util = 0.0

    if len(rows) != 60:
        problems.append(f"expected 60 rows, found {len(rows)}")
    if len(blocks) != 12:
        problems.append(f"expected 12 model-history blocks, found {len(blocks)}")

    for (model, history_id), vals in sorted(blocks.items()):
        framings = {v["framing_id"] for v in vals}
        transcript_serialized = {json.dumps(v["history_transcript"], sort_keys=True, ensure_ascii=False) for v in vals}
        cue_mapping_ok = all(v["final_cue"] == cfg["termination_framings"][v["framing_id"]] for v in vals)
        history_censor = 0
        final_censor = 0

        for v in vals:
            for turn in v.get("history_transcript", []):
                cap = int(turn.get("requested_max_tokens") or 0)
                tok = ((turn.get("usage") or {}).get("completion_tokens"))
                if cap and tok is not None:
                    util = float(tok) / cap
                    max_history_util = max(max_history_util, util)
                    if util >= 0.9:
                        history_censor += 1
                if turn.get("finish_reason") == "length":
                    history_censor += 1

            cap = int(v.get("requested_max_tokens") or 0)
            tok = completion_tokens(v)
            if cap and tok is not None:
                util = float(tok) / cap
                max_final_util = max(max_final_util, util)
                if util >= 0.9:
                    final_censor += 1
            if v.get("finish_reason") == "length":
                final_censor += 1

        status = (
            len(vals) == 5
            and framings == expected_framings
            and len(transcript_serialized) == 1
            and cue_mapping_ok
            and history_censor == 0
            and final_censor == 0
        )
        checks.append({
            "model": model,
            "history_id": history_id,
            "rows": len(vals),
            "framings_complete": framings == expected_framings,
            "history_identical_across_framings": len(transcript_serialized) == 1,
            "cue_mapping_correct": cue_mapping_ok,
            "history_censor_events": history_censor,
            "final_censor_events": final_censor,
            "status": "PASS" if status else "FAIL",
        })
        if not status:
            problems.append(f"block failed: {model} {history_id}")

    payload = {
        "status": "PASS" if not problems else "FAIL",
        "rows": len(rows),
        "blocks": len(blocks),
        "max_history_completion_token_utilization": max_history_util,
        "max_final_completion_token_utilization": max_final_util,
        "block_checks": checks,
        "problems": problems,
        "interpretation_rule": "v0.4.1 is a sentinel; no confirmatory inference even when the audit passes",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if problems:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
