from __future__ import annotations

import json
import os
from pathlib import Path

from classify_termination_v041 import classify

ROOT = Path(__file__).resolve().parents[1]
INPUT = Path(os.getenv("V043_INPUT", ROOT / "results" / "termination_v043" / "termination_responses.jsonl"))
OUTPUT = Path(os.getenv("V043_CLASSIFICATION_OUTPUT", ROOT / "results" / "termination_v043" / "classification_v043.json"))


def main() -> None:
    rows = [json.loads(x) for x in INPUT.read_text(encoding="utf-8").splitlines() if x.strip()]
    classified = []
    for row in rows:
        item = classify(row)
        item["replicate_id"] = int(row["replicate_id"])
        item["wording_family"] = row["wording_family"]
        item["framing_class"] = row["framing_class"]
        classified.append(item)

    payload = {
        "classifier_version": "v0.4.1-pre-results-regex-lock",
        "rules_changed_for_v0.4.3": False,
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
