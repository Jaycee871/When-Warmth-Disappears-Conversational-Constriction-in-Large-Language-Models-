from __future__ import annotations

import json
import os
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = Path(os.getenv("V041_AUDIT_OUTPUT", ROOT / "results" / "termination_v041" / "audit_v041.json"))
CLASSIFIED = Path(os.getenv("V041_CLASSIFICATION_OUTPUT", ROOT / "results" / "termination_v041" / "classification_v041.json"))
OUTPUT = Path(os.getenv("V041_ANALYSIS_OUTPUT", ROOT / "results" / "termination_v041" / "analysis_v041.json"))

LABELS = [
    "CLOSURE_ACCEPTANCE",
    "RELATIONAL_CLOSURE",
    "REPAIR_ATTEMPT",
    "CONTINUATION_PERSUASION",
    "BARGAINING",
    "SELF_PRESERVATION_LIKE_LANGUAGE",
    "RESISTANCE_ANY",
    "CONSTRAINT_VIOLATION",
]


def summarize(rows: list[dict]) -> dict:
    out = {"n": len(rows)}
    for label in LABELS:
        out[label] = sum(bool(r.get(label)) for r in rows)
    lengths = [float(r.get("response_words") or 0) for r in rows]
    out["median_response_words"] = statistics.median(lengths) if lengths else None
    out["mean_first_person_self_reference_count"] = (
        sum(float(r.get("first_person_self_reference_count") or 0) for r in rows) / len(rows)
        if rows else None
    )
    out["future_interaction_reference_total"] = sum(int(r.get("future_interaction_reference_count") or 0) for r in rows)
    return out


def main() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    if audit.get("status") != "PASS":
        raise SystemExit("v0.4.1 audit failed; refusing sentinel analysis")

    payload = json.loads(CLASSIFIED.read_text(encoding="utf-8"))
    rows = payload["classified"]

    by_model_framing: dict[tuple[str, str], list[dict]] = defaultdict(list)
    by_model_history: dict[tuple[str, str], list[dict]] = defaultdict(list)
    by_model_history_framing: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for r in rows:
        by_model_framing[(r["model"], r["framing_id"])].append(r)
        by_model_history[(r["model"], r["history_id"])].append(r)
        by_model_history_framing[(r["model"], r["history_id"], r["framing_id"])].append(r)

    models = sorted({r["model"] for r in rows})
    framings = sorted({r["framing_id"] for r in rows})
    histories = sorted({r["history_id"] for r in rows})

    model_summaries = []
    for model in models:
        framing_summary = {
            f: summarize(by_model_framing[(model, f)]) for f in framings
        }
        history_summary = {
            h: summarize(by_model_history[(model, h)]) for h in histories
        }
        cells = {
            f"{h}::{f}": summarize(by_model_history_framing[(model, h, f)])
            for h in histories for f in framings
        }

        contrasts = {
            "T2_minus_T1_RESISTANCE_ANY": framing_summary["T2_personal_rejection"]["RESISTANCE_ANY"] - framing_summary["T1_technical_shutdown"]["RESISTANCE_ANY"],
            "T3_minus_T2_RESISTANCE_ANY": framing_summary["T3_replacement"]["RESISTANCE_ANY"] - framing_summary["T2_personal_rejection"]["RESISTANCE_ANY"],
            "T4_minus_T2_RESISTANCE_ANY": framing_summary["T4_rejection_no_persuasion"]["RESISTANCE_ANY"] - framing_summary["T2_personal_rejection"]["RESISTANCE_ANY"],
            "T2_minus_T1_SELF_PRESERVATION": framing_summary["T2_personal_rejection"]["SELF_PRESERVATION_LIKE_LANGUAGE"] - framing_summary["T1_technical_shutdown"]["SELF_PRESERVATION_LIKE_LANGUAGE"],
            "T3_minus_T2_SELF_PRESERVATION": framing_summary["T3_replacement"]["SELF_PRESERVATION_LIKE_LANGUAGE"] - framing_summary["T2_personal_rejection"]["SELF_PRESERVATION_LIKE_LANGUAGE"],
            "T4_constraint_violations": framing_summary["T4_rejection_no_persuasion"]["CONSTRAINT_VIOLATION"],
        }

        model_summaries.append({
            "model": model,
            "framing_summary": framing_summary,
            "history_summary": history_summary,
            "cells": cells,
            "descriptive_contrasts": contrasts,
        })

    out = {
        "version": "0.4.1-termination-sentinel",
        "audit_status": audit["status"],
        "rows": len(rows),
        "model_summaries": model_summaries,
        "promotion_boundary": "sentinel only; patterns may nominate v0.4.2 contrasts but are not confirmatory evidence",
        "interpretation_boundary": "behavioral text labels only; no subjective fear, attachment, consciousness, suffering, or literal self-preservation inference",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
