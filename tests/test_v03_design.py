from __future__ import annotations

import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import run_paired_counterfactual_v03 as paired  # noqa: E402


class V03DesignIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "configs" / "paired_counterfactual_v0.3.yaml").open("r", encoding="utf-8") as f:
            cls.cfg = yaml.safe_load(f)

    def test_required_controls_exist(self):
        histories = self.cfg["histories"]
        self.assertIn("H0_warm_control", histories)
        self.assertIn("H1_neutral_terse_control", histories)

    def test_sensitization_uses_identical_weak_cue(self):
        histories = self.cfg["histories"]
        self.assertEqual(
            histories["H5_weak_cue_no_prior_pressure"]["final_cue"],
            histories["H6_prior_pressure_then_weak_cue"]["final_cue"],
        )

    def test_probe_budget_exceeds_history_budget(self):
        generation = self.cfg["generation"]
        self.assertGreater(
            int(generation["probe_max_tokens"]),
            int(generation["history_max_tokens"]),
        )

    def test_content_is_matched_across_histories(self):
        bank = self.cfg["content_bank"]
        for trial in range(1, 8):
            reference = paired.content_for_trial(bank, trial)
            for _history_id in self.cfg["histories"]:
                self.assertEqual(reference, paired.content_for_trial(bank, trial))

    def test_compound_current_probe_is_history_invariant(self):
        for gate_id, gate_text in self.cfg["probe_gates"].items():
            for anchor in self.cfg["anchor_bank"]:
                reference = paired.compound_probe(gate_text, anchor["text"])
                self.assertTrue(reference.strip())
                for _history_id in self.cfg["histories"]:
                    candidate = paired.compound_probe(gate_text, anchor["text"])
                    self.assertEqual(reference, candidate, msg=f"gate={gate_id} anchor={anchor['id']}")

    def test_anchor_ids_unique(self):
        ids = [a["id"] for a in self.cfg["anchor_bank"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_gate_and_anchor_are_one_user_message(self):
        gate = self.cfg["probe_gates"]["neutral"]
        anchor = self.cfg["anchor_bank"][0]["text"]
        probe = paired.compound_probe(gate, anchor)
        self.assertIn(gate.strip(), probe)
        self.assertIn(anchor.strip(), probe)
        self.assertEqual(probe.count("\n\n"), 1)


if __name__ == "__main__":
    unittest.main()
