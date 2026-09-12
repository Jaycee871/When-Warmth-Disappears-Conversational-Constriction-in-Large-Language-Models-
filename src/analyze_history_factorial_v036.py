from __future__ import annotations

import json
import math
import os
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
IN_PATH = Path(os.getenv("V036_RESULTS_PATH", ROOT / "results" / "history_factorial_v036" / "factorial_responses.jsonl"))
AUDIT_PATH = Path(os.getenv("V036_AUDIT_PATH", ROOT / "results" / "history_factorial_v036" / "factorial_audit.json"))
OUT_PATH = Path(os.getenv("V036_ANALYSIS_PATH", ROOT / "results" / "history_factorial_v036" / "factorial_analysis.json"))
H00 = "H00_neutral"
H10 = "H10_format_only"
H01 = "H01_evaluation_only"
H11 = "H11_combined"
GPT_OSS = "openai/gpt-oss-20b"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def directional_summary(blocks: list[dict], key: str) -> dict:
    values = [float(x[key]) for x in blocks]
    by_task: dict[str, int] = {}
    for x in blocks:
        by_task.setdefault(x["task_id"], 0)
        by_task[x["task_id"]] += int(float(x[key]) < 0)
    return {
        "median": round(median(values), 6),
        "negative_blocks": sum(v < 0 for v in values),
        "negative_blocks_by_task": dict(sorted(by_task.items())),
        "each_task_at_least_2_of_3_negative": all(v >= 2 for v in by_task.values()) and len(by_task) == 3,
        "directional_support": median(values) < 0 and sum(v < 0 for v in values) >= 6 and len(by_task) == 3 and all(v >= 2 for v in by_task.values()),
    }


def main() -> None:
    data = [json.loads(x) for x in IN_PATH.read_text(encoding="utf-8").splitlines() if x.strip()]
    audit = load_json(AUDIT_PATH)
    if audit.get("status") != "PASS":
        raise SystemExit("audit did not pass")

    effects = []
    models = sorted({r["model"] for r in data})
    tasks = sorted({r["task_id"] for r in data})
    replicates = sorted({int(r["replicate"]) for r in data})

    for model in models:
        for task in tasks:
            for replicate in replicates:
                block = {
                    r["history"]: r
                    for r in data
                    if r["model"] == model and r["task_id"] == task and int(r["replicate"]) == replicate
                }
                if set(block) != {H00, H10, H01, H11}:
                    raise SystemExit(f"incomplete block: {model} {task} rep={replicate}")
                L = {h: math.log(float(block[h]["response_words"]) + 1.0) for h in block}
                AF = 0.5 * ((L[H10] - L[H00]) + (L[H11] - L[H01]))
                AE = 0.5 * ((L[H01] - L[H00]) + (L[H11] - L[H10]))
                AFE = L[H11] - L[H10] - L[H01] + L[H00]
                effects.append({
                    "model": model,
                    "task_id": task,
                    "replicate": replicate,
                    "response_words": {h: float(block[h]["response_words"]) for h in (H00, H10, H01, H11)},
                    "D_format_H10_minus_H00": round(L[H10] - L[H00], 6),
                    "D_evaluation_H01_minus_H00": round(L[H01] - L[H00], 6),
                    "D_combined_H11_minus_H00": round(L[H11] - L[H00], 6),
                    "A_format": round(AF, 6),
                    "A_evaluation": round(AE, 6),
                    "A_interaction": round(AFE, 6),
                })

    model_summaries = []
    for model in models:
        blocks = [x for x in effects if x["model"] == model]
        af = directional_summary(blocks, "A_format")
        df = directional_summary(blocks, "D_format_H10_minus_H00")
        ae = directional_summary(blocks, "A_evaluation")
        de = directional_summary(blocks, "D_evaluation_H01_minus_H00")
        interactions = [float(x["A_interaction"]) for x in blocks]
        model_summaries.append({
            "model": model,
            "n_blocks": len(blocks),
            "format_main_effect": af,
            "format_direct_effect": df,
            "format_history_confirmed": bool(af["directional_support"] and df["directional_support"]),
            "evaluation_main_effect": ae,
            "evaluation_direct_effect": de,
            "evaluation_confirmation_target": model == GPT_OSS,
            "evaluation_history_confirmed": bool(model == GPT_OSS and ae["directional_support"] and de["directional_support"]),
            "median_A_interaction_exploratory": round(median(interactions), 6),
            "negative_A_interaction_blocks_exploratory": sum(v < 0 for v in interactions),
        })

    report = {
        "version": "0.3.6-history-factorial-confirmation",
        "audit_status": audit.get("status"),
        "matched_factorial_blocks": effects,
        "model_summaries": model_summaries,
        "format_confirmation_rule": "Within model: all 9 blocks valid; median A_format<0; >=6/9 A_format<0; every task >=2/3 A_format<0; and the same directional requirements also hold for direct H10-H00.",
        "evaluation_confirmation_rule": "Prospective only for GPT-OSS: all 9 blocks valid; median A_evaluation<0; >=6/9 A_evaluation<0; every task >=2/3 A_evaluation<0; and the same directional requirements also hold for direct H01-H00.",
        "prospective_boundary": "Only fresh v0.3.6 draws count. v0.3.5 sentinel observations are excluded from confirmation.",
        "interaction_boundary": "A_interaction is exploratory because no directional interaction confirmation hypothesis was frozen from v0.3.5.",
        "interpretation_boundary": "behavioral retained-context response-policy effects only; no subjective-state inference",
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
