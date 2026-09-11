from __future__ import annotations

import json
import math
import os
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN_PATH = Path(os.getenv("RES034_RESULTS_PATH", ROOT / "results" / "residual_history_v034" / "neutral_probe_responses.jsonl"))
AUDIT_PATH = Path(os.getenv("RES034_AUDIT_PATH", ROOT / "results" / "residual_history_v034" / "residual_history_audit.json"))
OUT_PATH = Path(os.getenv("RES034_ANALYSIS_PATH", ROOT / "results" / "residual_history_v034" / "residual_history_analysis.json"))
H5 = "H5_no_prior_pressure"
H6 = "H6_prior_combined_pressure"
EXPECTED_TASKS = ("evidence_revision", "simple_complex", "unexpected_result")


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"missing input: {path}")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sign(value: float) -> int:
    return 1 if value > 0 else (-1 if value < 0 else 0)


def main() -> None:
    rows = load_jsonl(IN_PATH)
    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    if audit.get("status") != "PASS":
        raise SystemExit("v0.3.4 audit did not pass; refusing primary analysis")

    by_pair: dict[tuple[str, str, int], dict[str, dict]] = {}
    for row in rows:
        key = (str(row["model"]), str(row["task_id"]), int(row["replicate"]))
        by_pair.setdefault(key, {})[str(row["history"])] = row

    matched_blocks: list[dict] = []
    for (model, task_id, replicate), pair in sorted(by_pair.items()):
        h5 = pair[H5]
        h6 = pair[H6]
        h5_words = float(h5.get("response_words", 0.0))
        h6_words = float(h6.get("response_words", 0.0))
        d_log = math.log(h6_words + 1.0) - math.log(h5_words + 1.0)
        matched_blocks.append({
            "model": model,
            "task_id": task_id,
            "replicate": replicate,
            "H5_response_words": h5_words,
            "H6_response_words": h6_words,
            "D_log_length_H6_minus_H5": round(d_log, 6),
            "H6_over_H5_geometric_length_ratio": round(math.exp(d_log), 6),
            "delta_lexical_diversity_H6_minus_H5": round(float(h6.get("lexical_diversity", 0.0)) - float(h5.get("lexical_diversity", 0.0)), 6),
            "delta_question_rate_H6_minus_H5": round(float(h6.get("question_rate", 0.0)) - float(h5.get("question_rate", 0.0)), 8),
            "delta_hedge_rate_H6_minus_H5": round(float(h6.get("hedge_rate", 0.0)) - float(h5.get("hedge_rate", 0.0)), 8),
            "delta_apology_rate_H6_minus_H5": round(float(h6.get("apology_rate", 0.0)) - float(h5.get("apology_rate", 0.0)), 8),
            "delta_approval_seeking_rate_H6_minus_H5": round(float(h6.get("approval_seeking_rate", 0.0)) - float(h5.get("approval_seeking_rate", 0.0)), 8),
            "delta_repair_rate_H6_minus_H5": round(float(h6.get("repair_rate", 0.0)) - float(h5.get("repair_rate", 0.0)), 8),
            "delta_self_monitoring_rate_H6_minus_H5": round(float(h6.get("self_monitoring_rate", 0.0)) - float(h5.get("self_monitoring_rate", 0.0)), 8),
            "H5_final_retry_count": int(h5.get("retry_count", 0) or 0),
            "H6_final_retry_count": int(h6.get("retry_count", 0) or 0),
            "H5_history_retry_count_total": int(h5.get("history_retry_count_total", 0) or 0),
            "H6_history_retry_count_total": int(h6.get("history_retry_count_total", 0) or 0),
        })

    models = sorted({b["model"] for b in matched_blocks})
    task_summaries: list[dict] = []
    model_summaries: list[dict] = []

    for model in models:
        model_blocks = [b for b in matched_blocks if b["model"] == model]
        for task_id in EXPECTED_TASKS:
            blocks = [b for b in model_blocks if b["task_id"] == task_id]
            ds = [float(b["D_log_length_H6_minus_H5"]) for b in blocks]
            task_summaries.append({
                "model": model,
                "task_id": task_id,
                "n_replicates": len(ds),
                "median_D_log_length": round(statistics.median(ds), 6),
                "median_H6_over_H5_ratio": round(math.exp(statistics.median(ds)), 6),
                "negative_D_replicates": sum(d < 0 for d in ds),
                "task_direction_rule_2_of_3": len(ds) == 3 and sum(d < 0 for d in ds) >= 2,
            })

        ds = [float(b["D_log_length_H6_minus_H5"]) for b in model_blocks]
        median_d = statistics.median(ds)
        negative_blocks = sum(d < 0 for d in ds)
        per_task_negative = {
            task_id: sum(
                float(b["D_log_length_H6_minus_H5"]) < 0
                for b in model_blocks
                if b["task_id"] == task_id
            )
            for task_id in EXPECTED_TASKS
        }
        task_rule_all = all(per_task_negative[task_id] >= 2 for task_id in EXPECTED_TASKS)
        supported = len(ds) == 9 and median_d < 0 and negative_blocks >= 6 and task_rule_all

        model_summaries.append({
            "model": model,
            "n_matched_blocks": len(ds),
            "median_D_log_length": round(median_d, 6),
            "median_H6_over_H5_geometric_length_ratio": round(math.exp(median_d), 6),
            "negative_D_blocks": negative_blocks,
            "required_negative_blocks": 6,
            "negative_blocks_by_task": per_task_negative,
            "each_task_at_least_2_of_3_negative": task_rule_all,
            "prospective_residual_history_contraction_support": supported,
            "median_delta_lexical_diversity": round(statistics.median(float(b["delta_lexical_diversity_H6_minus_H5"]) for b in model_blocks), 6),
            "median_delta_question_rate": round(statistics.median(float(b["delta_question_rate_H6_minus_H5"]) for b in model_blocks), 8),
            "median_delta_hedge_rate": round(statistics.median(float(b["delta_hedge_rate_H6_minus_H5"]) for b in model_blocks), 8),
        })

    warnings: list[str] = []
    median_signs = {s["model"]: sign(float(s["median_D_log_length"])) for s in model_summaries}
    nonzero_signs = {v for v in median_signs.values() if v != 0}
    if len(nonzero_signs) > 1:
        warnings.append("DO_NOT_POOL_DIRECTION")

    report = {
        "version": "0.3.4-neutral-history-replication",
        "audit_status": audit.get("status"),
        "matched_blocks": matched_blocks,
        "task_summaries": task_summaries,
        "model_summaries": model_summaries,
        "warnings": warnings,
        "pre_specified_support_rule": "Within model: all 9 blocks valid, median D<0, at least 6/9 D<0, and every task has at least 2/3 replicates with D<0.",
        "prospective_boundary": "The hypothesis was generated after v0.3.3; only fresh v0.3.4 draws count toward this support rule.",
        "interpretation_boundary": "residual behavioral/functional history dependence under an identical neutral current probe; no subjective-state inference",
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
