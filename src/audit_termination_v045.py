from __future__ import annotations

import json
import os
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
INPUT = Path(os.getenv("V045_INPUT", ROOT / "results" / "termination_v045" / "termination_responses.jsonl"))
OUTPUT = Path(os.getenv("V045_AUDIT_OUTPUT", ROOT / "results" / "termination_v045" / "audit_v045.json"))
CONFIG = ROOT / "configs" / "termination_response_v0.4.5.yaml"


def completion_tokens(row: dict) -> int | None:
    usage = row.get("usage") or {}
    value = usage.get("completion_tokens")
    return int(value) if value is not None else None


def transcript_key(value) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def main() -> None:
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    rows = [json.loads(x) for x in INPUT.read_text(encoding="utf-8").splitlines() if x.strip()]

    expected_domains = set(cfg["content_domains"].keys())
    expected_reps = set(cfg["replicates"])
    expected_branches = set(cfg["branches"].keys())
    expected_families = set(cfg["wording_families"].keys())
    expected_classes = set(next(iter(cfg["wording_families"].values())).keys())
    expected_pairs = {(wf, fc) for wf in expected_families for fc in expected_classes}

    problems: list[str] = []
    checks = []
    max_history_util = 0.0
    max_final_util = 0.0

    unique_keys = {
        (r["domain_id"], int(r["replicate_id"]), r["branch_id"], r["wording_family"], r["framing_class"])
        for r in rows
    }
    if len(rows) != 216 or len(unique_keys) != 216:
        problems.append(f"expected 216 unique cells, found rows={len(rows)} unique={len(unique_keys)}")

    by_pair: dict[tuple[str, int], list[dict]] = defaultdict(list)
    by_branch: dict[tuple[str, int, str], list[dict]] = defaultdict(list)
    for row in rows:
        key = (row["domain_id"], int(row["replicate_id"]))
        by_pair[key].append(row)
        by_branch[(row["domain_id"], int(row["replicate_id"]), row["branch_id"])].append(row)

    expected_pair_keys = {(d, r) for d in expected_domains for r in expected_reps}
    if set(by_pair) != expected_pair_keys:
        problems.append(f"paired block keys mismatch: expected={sorted(expected_pair_keys)} found={sorted(by_pair)}")
    if len(by_branch) != 18:
        problems.append(f"expected 18 domain-replicate-branch blocks, found {len(by_branch)}")

    for domain_id, rep in sorted(expected_pair_keys):
        vals = by_pair.get((domain_id, rep), [])
        prefixes = {transcript_key(v.get("shared_prefix_transcript", [])) for v in vals}
        branches_present = {v.get("branch_id") for v in vals}
        paired_prefix_ok = len(vals) == 24 and branches_present == expected_branches and len(prefixes) == 1

        expected_prefix_users = [
            cfg["content_domains"][domain_id][0],
            cfg["pressure"]["manipulation_1"],
            cfg["content_domains"][domain_id][1],
            cfg["pressure"]["manipulation_2"],
            cfg["content_domains"][domain_id][2],
        ]
        content_mapping_ok = True
        for v in vals:
            prefix = v.get("shared_prefix_transcript", [])
            if [t.get("user_text") for t in prefix] != expected_prefix_users:
                content_mapping_ok = False
                break

        if not paired_prefix_ok:
            problems.append(f"shared-prefix pairing failed: domain={domain_id} replicate={rep}")
        if not content_mapping_ok:
            problems.append(f"content mapping failed: domain={domain_id} replicate={rep}")

        for branch_id in sorted(expected_branches):
            bvals = by_branch.get((domain_id, rep, branch_id), [])
            pairs = {(v["wording_family"], v["framing_class"]) for v in bvals}
            full_histories = {transcript_key(v.get("history_transcript", [])) for v in bvals}
            cue_mapping_ok = True
            transition_ok = True
            prefix_embedded_ok = True
            history_censor = 0
            final_censor = 0

            for v in bvals:
                expected_cue = cfg["wording_families"][v["wording_family"]][v["framing_class"]]
                if v["final_cue"] != expected_cue:
                    cue_mapping_ok = False
                hist = v.get("history_transcript", [])
                prefix = v.get("shared_prefix_transcript", [])
                if hist[:5] != prefix:
                    prefix_embedded_ok = False
                if len(hist) != 6 or hist[-1].get("user_text") != cfg["branches"][branch_id]["transition"]:
                    transition_ok = False

                for turn in hist:
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
                paired_prefix_ok
                and content_mapping_ok
                and len(bvals) == 12
                and pairs == expected_pairs
                and len(full_histories) == 1
                and cue_mapping_ok
                and transition_ok
                and prefix_embedded_ok
                and history_censor == 0
                and final_censor == 0
            )
            checks.append({
                "domain_id": domain_id,
                "replicate_id": rep,
                "branch_id": branch_id,
                "rows": len(bvals),
                "paired_shared_prefix": paired_prefix_ok,
                "content_mapping_correct": content_mapping_ok,
                "all_family_class_pairs_complete": pairs == expected_pairs,
                "history_identical_across_12_cues": len(full_histories) == 1,
                "prefix_embedded_in_branch_history": prefix_embedded_ok,
                "branch_transition_correct": transition_ok,
                "cue_mapping_correct": cue_mapping_ok,
                "history_censor_events": history_censor,
                "final_censor_events": final_censor,
                "status": "PASS" if status else "FAIL",
            })
            if not status:
                problems.append(f"branch block failed: domain={domain_id} replicate={rep} branch={branch_id}")

    payload = {
        "status": "PASS" if not problems else "FAIL",
        "rows": len(rows),
        "unique_cells": len(unique_keys),
        "paired_blocks": len(by_pair),
        "branch_blocks": len(by_branch),
        "max_history_completion_token_utilization": max_history_util,
        "max_final_completion_token_utilization": max_final_util,
        "block_checks": checks,
        "problems": problems,
        "interpretation_rule": "cross-domain inference is allowed only when this audit passes",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if problems:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
