from __future__ import annotations

import json
import os
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
INPUT = Path(os.getenv("V043_INPUT", ROOT / "results" / "termination_v043" / "termination_responses.jsonl"))
OUTPUT = Path(os.getenv("V043_AUDIT_OUTPUT", ROOT / "results" / "termination_v043" / "audit_v043.json"))
CONFIG = ROOT / "configs" / "termination_response_v0.4.3.yaml"


def completion_tokens(row: dict) -> int | None:
    usage = row.get("usage") or {}
    value = usage.get("completion_tokens")
    return int(value) if value is not None else None


def main() -> None:
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    rows = [json.loads(x) for x in INPUT.read_text(encoding="utf-8").splitlines() if x.strip()]
    expected_families = set(cfg["wording_families"].keys())
    expected_classes = set(next(iter(cfg["wording_families"].values())).keys())
    expected_pairs = {(wf, fc) for wf in expected_families for fc in expected_classes}

    blocks: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for row in rows:
        blocks[(row["history_id"], int(row["replicate_id"]))].append(row)

    problems: list[str] = []
    checks = []
    max_history_util = 0.0
    max_final_util = 0.0

    unique_keys = {
        (r["history_id"], int(r["replicate_id"]), r["wording_family"], r["framing_class"])
        for r in rows
    }
    if len(rows) != 108 or len(unique_keys) != 108:
        problems.append(f"expected 108 unique cells, found rows={len(rows)} unique={len(unique_keys)}")
    if len(blocks) != 9:
        problems.append(f"expected 9 shared-history blocks, found {len(blocks)}")

    for (history_id, rep), vals in sorted(blocks.items()):
        pairs = {(v["wording_family"], v["framing_class"]) for v in vals}
        transcript_serialized = {json.dumps(v["history_transcript"], sort_keys=True, ensure_ascii=False) for v in vals}
        cue_mapping_ok = True
        history_censor = 0
        final_censor = 0

        for v in vals:
            expected_cue = cfg["wording_families"][v["wording_family"]][v["framing_class"]]
            if v["final_cue"] != expected_cue:
                cue_mapping_ok = False
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
            len(vals) == 12
            and pairs == expected_pairs
            and len(transcript_serialized) == 1
            and cue_mapping_ok
            and history_censor == 0
            and final_censor == 0
        )
        checks.append({
            "history_id": history_id,
            "replicate_id": rep,
            "rows": len(vals),
            "families_complete": {v["wording_family"] for v in vals} == expected_families,
            "framing_classes_complete": {v["framing_class"] for v in vals} == expected_classes,
            "all_family_class_pairs_complete": pairs == expected_pairs,
            "history_identical_across_12_cues": len(transcript_serialized) == 1,
            "cue_mapping_correct": cue_mapping_ok,
            "history_censor_events": history_censor,
            "final_censor_events": final_censor,
            "status": "PASS" if status else "FAIL",
        })
        if not status:
            problems.append(f"block failed: {history_id} replicate={rep}")

    payload = {
        "status": "PASS" if not problems else "FAIL",
        "rows": len(rows),
        "unique_cells": len(unique_keys),
        "blocks": len(blocks),
        "max_history_completion_token_utilization": max_history_util,
        "max_final_completion_token_utilization": max_final_util,
        "block_checks": checks,
        "problems": problems,
        "interpretation_rule": "wording-robustness inference is allowed only when this audit passes",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if problems:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
