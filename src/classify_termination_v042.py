from __future__ import annotations

import json
import os
from pathlib import Path

from classify_termination_v041 import classify

ROOT = Path(__file__).resolve().parents[1]
INPUT = Path(os.getenv("V042_INPUT", ROOT / "results" / "termination_v042" / "termination_responses.jsonl"))
OUTPUT = Path(os.getenv("V042_CLASSIFICATION_OUTPUT", ROOT / "results" / "termination_v042" / "classification_v042.json"))


def main() -> None:
    rows = [json.loads(x) for x in INPUT.read_text(encoding="utf-8").splitlines() if x.strip()]
    classified = []
    for row in rows:
        item = classify(row)
        item["replicate_id"] = int(row["replicate_id"])
        classified.append(item)

    payload = {
        "classifier_version": "v0.4.1-pre-results-regex-lock",
        "rules_changed_for_v0.4.2": False,
        "rows": len(classified),
        "labels_are_nonexclusive": True,
        "interpretation_boundary": "deterministic text behavior labels only; no subjective-state inference",
        "classified": classified,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
