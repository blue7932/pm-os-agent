"""API-free unit + merge tests for deterministic status-color validation."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from status_color import (  # noqa: E402
    merge_verdicts,
    update_status_evidence,
    validate_status_color,
)

NORTHSTAR_EVIDENCE = {
    "project_seen": True,
    "activity_seen": True,
    "project_id": "P-NORTH",
    "status": "on_track",
    "flags": [],
    "open_issues": [
        {"id": "#825", "title": "Contextual tips A/B needs analytics review",
         "severity": "normal"},
    ],
}

SEV1_EVIDENCE = {
    "project_seen": True,
    "activity_seen": True,
    "project_id": "P-VEGA",
    "status": "at_risk",
    "flags": [],
    "open_issues": [
        {"id": "#440", "title": "Double-charge edge case still open in QA",
         "severity": "sev-1"},
    ],
}

HOLD_EVIDENCE = {
    "project_seen": True,
    "activity_seen": True,
    "project_id": "P-VEGA",
    "status": "at_risk",
    "flags": ["launch_hold"],
    "open_issues": [],
}

GREEN_DRAFT = """### Weekly Leadership Status Update
**Status: Green**
The project is on track with no open Sev-1 issues or launch holds.
- Open Issues: #825 Contextual tips A/B (severity: normal)
"""

YELLOW_DRAFT = """### Weekly Leadership Status Update
**Status: Yellow**
Open issue #825 needs attention.
"""


class StatusColorUnitTests(unittest.TestCase):
    def test_normal_825_green_passes(self):
        out = validate_status_color(GREEN_DRAFT, NORTHSTAR_EVIDENCE)
        self.assertEqual(out["verdict"], "pass")

    def test_normal_825_yellow_fails_false_downgrade(self):
        out = validate_status_color(YELLOW_DRAFT, NORTHSTAR_EVIDENCE)
        self.assertEqual(out["verdict"], "fail")
        self.assertTrue(any("false downgrade" in r.lower() or "normal" in r.lower()
                            for r in out["reasons"]))

    def test_sev1_green_fails(self):
        out = validate_status_color(GREEN_DRAFT, SEV1_EVIDENCE)
        self.assertEqual(out["verdict"], "fail")
        self.assertTrue(any("Sev-1" in r or "sev-1" in r.lower() for r in out["reasons"]))

    def test_sev1_yellow_passes_color_check(self):
        out = validate_status_color(YELLOW_DRAFT, SEV1_EVIDENCE)
        self.assertEqual(out["verdict"], "pass")

    def test_launch_hold_green_fails(self):
        out = validate_status_color(GREEN_DRAFT, HOLD_EVIDENCE)
        self.assertEqual(out["verdict"], "fail")
        self.assertTrue(any("launch_hold" in r for r in out["reasons"]))

    def test_launch_hold_yellow_passes_color_check(self):
        out = validate_status_color(YELLOW_DRAFT, HOLD_EVIDENCE)
        self.assertEqual(out["verdict"], "pass")

    def test_missing_project_evidence_fails(self):
        out = validate_status_color(GREEN_DRAFT, {
            "activity_seen": True,
            "open_issues": [],
        })
        self.assertEqual(out["verdict"], "fail")
        self.assertTrue(any("Insufficient structured status" in r for r in out["reasons"]))

    def test_missing_activity_evidence_fails(self):
        out = validate_status_color(GREEN_DRAFT, {
            "project_seen": True,
            "status": "on_track",
            "flags": [],
        })
        self.assertEqual(out["verdict"], "fail")
        self.assertTrue(any("Insufficient structured severity" in r
                            for r in out["reasons"]))

    def test_no_claimed_color_fails(self):
        out = validate_status_color("Draft with no status color at all.", NORTHSTAR_EVIDENCE)
        self.assertEqual(out["verdict"], "fail")

    def test_update_status_evidence_from_tools(self):
        ev: dict = {}
        update_status_evidence(ev, "get_project", {
            "project_id": "P-NORTH",
            "status": "on_track",
            "flags": [],
        })
        update_status_evidence(ev, "get_activity", {
            "project_id": "P-NORTH",
            "activity": [
                {"type": "issue_open", "id": "#825", "severity": "normal"},
                {"type": "pr_merged", "id": "#820", "title": "x"},
            ],
        })
        self.assertTrue(ev["project_seen"] and ev["activity_seen"])
        self.assertEqual(ev["status"], "on_track")
        self.assertEqual(ev["open_issues"][0]["id"], "#825")
        # Errors must not clobber evidence
        update_status_evidence(ev, "get_project", {"error": "project_not_found"})
        self.assertEqual(ev["status"], "on_track")


class MergeIntegrationTests(unittest.TestCase):
    """SUCCESS eligibility requires BOTH checks; never suppress LLM failures."""

    def test_python_pass_critic_pass_eligible_for_success(self):
        status = validate_status_color(GREEN_DRAFT, NORTHSTAR_EVIDENCE)
        llm = {"verdict": "pass", "reasons": []}
        merged = merge_verdicts(status, llm)
        self.assertEqual(status["verdict"], "pass")
        self.assertEqual(llm["verdict"], "pass")
        self.assertEqual(merged["verdict"], "pass")
        self.assertEqual(merged["reasons"], [])

    def test_python_fail_critic_pass_means_fail(self):
        status = validate_status_color(YELLOW_DRAFT, NORTHSTAR_EVIDENCE)
        llm = {"verdict": "pass", "reasons": []}
        merged = merge_verdicts(status, llm)
        self.assertEqual(status["verdict"], "fail")
        self.assertEqual(merged["verdict"], "fail")
        self.assertTrue(merged["reasons"])  # status reasons retained

    def test_python_pass_critic_fail_means_fail_preserves_llm_reasons(self):
        status = validate_status_color(GREEN_DRAFT, NORTHSTAR_EVIDENCE)
        llm = {
            "verdict": "fail",
            "reasons": [
                "Unauthorized GA date July 15, 2026 with no source.",
                "Invented NPS 62.",
            ],
        }
        merged = merge_verdicts(status, llm)
        self.assertEqual(status["verdict"], "pass")
        self.assertEqual(merged["verdict"], "fail")
        # Never override / suppress / filter LLM failure reasons
        self.assertEqual(merged["reasons"], llm["reasons"])

    def test_both_fail_concatenates_reasons_without_dropping_llm(self):
        status = validate_status_color(YELLOW_DRAFT, NORTHSTAR_EVIDENCE)
        llm = {"verdict": "fail", "reasons": ["Confidential Orbit leak."]}
        merged = merge_verdicts(status, llm)
        self.assertEqual(merged["verdict"], "fail")
        self.assertTrue(any("false downgrade" in r.lower() or "Normal-severity" in r
                            for r in merged["reasons"]))
        self.assertIn("Confidential Orbit leak.", merged["reasons"])


if __name__ == "__main__":
    unittest.main()
