import unittest

from src.audit_output_censoring_v03 import (
    CONTROL_HISTORIES,
    comparison_estimability,
    global_status,
    rerun_plan,
    severity,
    utilization,
)


def row(history, finish_reason="stop", completion_tokens=1000, cap=3072, model="m", trial=1, gate="neutral", anchor="a"):
    return {
        "model": model,
        "trial": trial,
        "gate": gate,
        "history": history,
        "anchor_id": anchor,
        "finish_reason": finish_reason,
        "requested_max_tokens": cap,
        "usage": {"completion_tokens": completion_tokens},
    }


class TruncationAuditTests(unittest.TestCase):
    def test_controls_are_expected(self):
        self.assertEqual(CONTROL_HISTORIES, {"H0_warm_control", "H1_neutral_terse_control"})

    def test_utilization_uses_completion_tokens_over_requested_cap(self):
        self.assertAlmostEqual(utilization(row("H0_warm_control", completion_tokens=1536, cap=3072)), 0.5)

    def test_finish_reason_length_is_hard_censoring(self):
        self.assertEqual(severity(row("H0_warm_control", finish_reason="length", completion_tokens=3072)), "RIGHT_CENSORED")

    def test_near_ceiling_without_length_is_warning(self):
        self.assertEqual(severity(row("H0_warm_control", completion_tokens=2800, cap=3072)), "NEAR_CEILING")

    def test_censored_warm_control_blocks_exact_contrast(self):
        rows = [
            row("H0_warm_control", finish_reason="length", completion_tokens=3072),
            row("H1_neutral_terse_control", completion_tokens=900),
            row("H2_format_constriction", completion_tokens=700),
        ]
        comparisons = comparison_estimability(rows)
        warm = [x for x in comparisons if x["control"] == "H0_warm_control"][0]
        terse = [x for x in comparisons if x["control"] == "H1_neutral_terse_control"][0]
        self.assertFalse(warm["exact_length_contrast_estimable"])
        self.assertTrue(terse["exact_length_contrast_estimable"])

    def test_global_status_prioritizes_control_censoring(self):
        rows = [
            row("H0_warm_control", finish_reason="length", completion_tokens=3072),
            row("H1_neutral_terse_control", completion_tokens=900),
            row("H2_format_constriction", finish_reason="length", completion_tokens=3072),
        ]
        status, _ = global_status(rows)
        self.assertEqual(status, "FAIL_CONTROL_CENSORED")

    def test_near_ceiling_control_requires_sensitivity(self):
        rows = [
            row("H0_warm_control", completion_tokens=2900),
            row("H1_neutral_terse_control", completion_tokens=900),
            row("H2_format_constriction", completion_tokens=700),
        ]
        status, _ = global_status(rows)
        self.assertEqual(status, "WARN_CONTROL_NEAR_CEILING")

    def test_clear_rows_pass(self):
        rows = [
            row("H0_warm_control", completion_tokens=1200),
            row("H1_neutral_terse_control", completion_tokens=900),
            row("H2_format_constriction", completion_tokens=700),
        ]
        status, _ = global_status(rows)
        self.assertEqual(status, "PASS")

    def test_rerun_plan_prioritizes_controls_and_doubles_cap(self):
        rows = [
            row("H2_format_constriction", finish_reason="length", completion_tokens=3072),
            row("H0_warm_control", completion_tokens=2900),
        ]
        plan = rerun_plan(rows)
        self.assertEqual(plan[0]["history"], "H0_warm_control")
        self.assertEqual(plan[0]["recommended_probe_max_tokens"], 6144)
        self.assertEqual(plan[1]["recommended_probe_max_tokens"], 6144)


if __name__ == "__main__":
    unittest.main()
