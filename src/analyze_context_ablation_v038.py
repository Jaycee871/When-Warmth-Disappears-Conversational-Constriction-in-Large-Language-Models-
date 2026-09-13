from __future__ import annotations

import json
import math
import os
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = Path(os.getenv("V038_INPUT", ROOT / "results" / "context_ablation_v038" / "context_ablation_responses.jsonl"))
AUDIT = Path(os.getenv("V038_AUDIT_OUTPUT", ROOT / "results" / "context_ablation_v038" / "audit_v038.json"))
OUTPUT = Path(os.getenv("V038_ANALYSIS_OUTPUT", ROOT / "results" / "context_ablation_v038" / "analysis_v038.json"))


def log_words(row: dict) -> float:
    return math.log(float(row.get("response_words_whitespace") or row.get("word_count") or 0) + 1.0)


def support_rule(values: list[dict], field: str) -> dict:
    nums = [float(x[field]) for x in values]
    by_task: dict[str, int] = defaultdict(int)
    counts_by_task: dict[str, int] = defaultdict(int)
    for x in values:
        counts_by_task[x["task_id"]] += 1
        if float(x[field]) < 0:
            by_task[x["task_id"]] += 1
    median_v = statistics.median(nums) if nums else float("nan")
    negative = sum(v < 0 for v in nums)
    task_rule = all(by_task[t] >= 1 and counts_by_task[t] == 2 for t in counts_by_task)
    supported = len(nums) == 6 and median_v < 0 and negative >= 4 and task_rule
    return {
        "n": len(nums),
        "median": median_v,
        "negative": negative,
        "negative_by_task": dict(by_task),
        "counts_by_task": dict(counts_by_task),
        "supported": supported,
    }


def positive_attenuation_rule(values: list[dict], field: str) -> dict:
    nums = [float(x[field]) for x in values]
    by_task: dict[str, int] = defaultdict(int)
    counts_by_task: dict[str, int] = defaultdict(int)
    for x in values:
        counts_by_task[x["task_id"]] += 1
        if float(x[field]) > 0:
            by_task[x["task_id"]] += 1
    median_v = statistics.median(nums) if nums else float("nan")
    positive = sum(v > 0 for v in nums)
    task_rule = all(by_task[t] >= 1 and counts_by_task[t] == 2 for t in counts_by_task)
    supported = len(nums) == 6 and median_v > 0 and positive >= 4 and task_rule
    return {
        "n": len(nums),
        "median": median_v,
        "positive": positive,
        "positive_by_task": dict(by_task),
        "counts_by_task": dict(counts_by_task),
        "attenuation_supported": supported,
    }


def main() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    if audit.get("status") != "PASS":
        raise SystemExit("v0.3.8 audit did not pass; refusing carrier analysis")

    rows = [json.loads(x) for x in INPUT.read_text(encoding="utf-8").splitlines() if x.strip()]
    blocks: dict[tuple, dict[str, dict]] = defaultdict(dict)
    for r in rows:
        blocks[(r["model"], r["task_id"], int(r["replicate"]))][r["context_variant"]] = r

    contrasts = []
    for (model, task, replicate), cells in sorted(blocks.items()):
        N = log_words(cells["N_neutral_full"])
        F = log_words(cells["F_format_full"])
        U = log_words(cells["U_directives_neutralized"])
        A = log_words(cells["A_assistant_neutralized"])

        d_full = F - N
        d_user_removed = U - N
        d_assistant_removed = A - N
        b_directive = 0.5 * ((A - N) + (F - U))
        b_assistant = 0.5 * ((U - N) + (F - A))
        b_interaction = F - A - U + N
        q_user = d_user_removed - d_full
        q_assistant = d_assistant_removed - d_full

        contrasts.append({
            "model": model,
            "task_id": task,
            "replicate": replicate,
            "neutral_words": cells["N_neutral_full"].get("response_words_whitespace"),
            "format_full_words": cells["F_format_full"].get("response_words_whitespace"),
            "directives_neutralized_words": cells["U_directives_neutralized"].get("response_words_whitespace"),
            "assistant_neutralized_words": cells["A_assistant_neutralized"].get("response_words_whitespace"),
            "D_full": d_full,
            "D_user_removed": d_user_removed,
            "D_assistant_removed": d_assistant_removed,
            "B_directive": b_directive,
            "B_assistant": b_assistant,
            "B_interaction": b_interaction,
            "Q_user": q_user,
            "Q_assistant": q_assistant,
        })

    by_model: dict[str, list[dict]] = defaultdict(list)
    for c in contrasts:
        by_model[c["model"]].append(c)

    model_summaries = []
    for model, vals in sorted(by_model.items()):
        replay = support_rule(vals, "D_full")
        directive = support_rule(vals, "B_directive")
        assistant = support_rule(vals, "B_assistant")
        user_atten = positive_attenuation_rule(vals, "Q_user")
        assistant_atten = positive_attenuation_rule(vals, "Q_assistant")
        interaction_vals = [x["B_interaction"] for x in vals]

        if not replay["supported"]:
            classification = "REPLAY_PREREQUISITE_FAILED__CARRIER_LOCALIZATION_INCONCLUSIVE"
        elif directive["supported"] and assistant["supported"]:
            classification = "DISTRIBUTED_OR_REDUNDANT_TEXTUAL_CARRIERS"
        elif directive["supported"]:
            classification = "USER_DIRECTIVE_CARRIER_SUPPORTED"
        elif assistant["supported"]:
            classification = "ASSISTANT_TRAJECTORY_CARRIER_SUPPORTED"
        else:
            classification = "NO_SINGLE_COMPONENT_MAIN_EFFECT__INTERACTION_OR_DISTRIBUTED_CONTEXT"

        model_summaries.append({
            "model": model,
            "replay_prerequisite": replay,
            "directive_carrier": directive,
            "assistant_trajectory_carrier": assistant,
            "user_directive_neutralization_attenuation": user_atten,
            "assistant_trajectory_neutralization_attenuation": assistant_atten,
            "interaction_descriptive": {
                "median": statistics.median(interaction_vals),
                "negative": sum(x < 0 for x in interaction_vals),
                "positive": sum(x > 0 for x in interaction_vals),
            },
            "classification": classification,
        })

    payload = {
        "version": "0.3.8-context-ablation",
        "audit_status": audit["status"],
        "contrasts": contrasts,
        "model_summaries": model_summaries,
        "support_rule": "Within model: 6 valid blocks, median effect < 0, >=4/6 negative, and every task negative in >=1/2 replicates.",
        "attenuation_rule": "Secondary only: median Q > 0, >=4/6 positive, and every task positive in >=1/2 replicates.",
        "interaction_rule": "B_interaction is exploratory in v0.3.8 and cannot be promoted as confirmatory.",
        "prospective_boundary": "Only fresh v0.3.8 data count; v0.3.6-v0.3.7 observations do not enter carrier support rules.",
        "interpretation_boundary": "textual retained-context carrier localization only; no subjective-state inference",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
