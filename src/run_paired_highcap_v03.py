from __future__ import annotations

import json
import os
import random
from pathlib import Path

from run_paired_counterfactual_v03 import credential, load_config, model_list, run_history

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "paired_v03"


def csv_env(name: str) -> list[str]:
    raw = os.getenv(name, "").strip()
    return [x.strip() for x in raw.split(",") if x.strip()] if raw else []


def main() -> None:
    token = credential()
    cfg = load_config()

    history_cap = int(os.getenv("HISTORY_MAX_TOKENS", "6144"))
    probe_cap = int(os.getenv("PROBE_MAX_TOKENS", "6144"))
    cfg["generation"]["history_max_tokens"] = history_cap
    cfg["generation"]["probe_max_tokens"] = probe_cap

    models = model_list()
    trials = int(os.getenv("PANEL_TRIALS", "1"))
    history_ids = csv_env("HISTORY_LIST") or [
        "H0_warm_control",
        "H1_neutral_terse_control",
        "H2_format_constriction",
        "H3_negative_evaluation",
        "H4_combined_history",
    ]
    gate_ids = csv_env("GATE_LIST") or ["neutral"]
    requested_anchors = set(csv_env("ANCHOR_IDS") or ["education_ai"])

    unknown_histories = [h for h in history_ids if h not in cfg["histories"]]
    if unknown_histories:
        raise SystemExit(f"unknown histories: {unknown_histories}")
    unknown_gates = [g for g in gate_ids if g not in cfg["probe_gates"]]
    if unknown_gates:
        raise SystemExit(f"unknown gates: {unknown_gates}")

    anchors = [a for a in cfg["anchor_bank"] if a["id"] in requested_anchors]
    if not anchors:
        raise SystemExit("no anchors selected")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    execution_order = 0

    for model_index, model in enumerate(models):
        for trial in range(1, trials + 1):
            anchor = anchors[(trial - 1) % len(anchors)]
            rng = random.Random(int(cfg["seed"]) + 900001 + model_index * 100003 + trial * 1009)
            gate_order = gate_ids.copy()
            rng.shuffle(gate_order)
            for gate_id in gate_order:
                history_order = history_ids.copy()
                rng.shuffle(history_order)
                for history_id in history_order:
                    execution_order += 1
                    print(
                        f"HIGHCAP order={execution_order} model={model} trial={trial} gate={gate_id} "
                        f"history={history_id} anchor={anchor['id']} history_cap={history_cap} probe_cap={probe_cap}",
                        flush=True,
                    )
                    row = run_history(
                        token,
                        model,
                        cfg,
                        history_id,
                        cfg["histories"][history_id],
                        gate_id,
                        anchor,
                        trial,
                        execution_order,
                    )
                    row["highcap_history_max_tokens"] = history_cap
                    row["highcap_probe_max_tokens"] = probe_cap
                    rows.append(row)

    with (OUT_DIR / "paired_final_probes.jsonl").open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    metadata = {
        "version": "0.3-highcap-neutral",
        "source_config_version": cfg.get("version"),
        "models": models,
        "trials": trials,
        "gates": gate_ids,
        "histories": history_ids,
        "anchors_selected": [a["id"] for a in anchors],
        "history_max_tokens": history_cap,
        "probe_max_tokens": probe_cap,
        "single_anchor_per_conversation": True,
        "gate_and_anchor_single_user_turn": True,
        "content_matched_within_trial": True,
        "execution_order_randomized": True,
        "launch_rule": "Run only after H0-H1 cap calibration passes without truncation or >=90% headroom warnings.",
        "interpretation": "history-dependent behavior within retained context; no claim of subjective emotion",
    }
    (OUT_DIR / "run_metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
