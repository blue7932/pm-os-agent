"""Deterministic status-color check (prototype rules).

Owns green/yellow/red grading from structured tool evidence so the LLM critic
does not flip-flop on normal-severity issues. Other critic checks stay with the
LLM; this module never upgrades an LLM failure to a pass.
"""

from __future__ import annotations

import re
from typing import Any

_SEV1 = {"sev-1", "sev1", "sev_1"}
_COLOR_RE = re.compile(
    r"(?i)(?:\*{0,2}\s*)?(?:project\s+)?status\s*(?:\*{0,2}\s*)?[:\-–—]\s*"
    r"(?:\*{0,2}\s*)?(green|yellow|red)\b"
)


def normalize_severity(raw: Any) -> str:
    return str(raw or "").strip().lower().replace(" ", "")


def is_sev1(severity: Any) -> bool:
    return normalize_severity(severity) in _SEV1


def extract_claimed_color(proposed_output: str) -> str | None:
    """Return 'green'|'yellow'|'red' if the draft states an overall status color."""
    if not proposed_output:
        return None
    matches = _COLOR_RE.findall(proposed_output)
    if not matches:
        return None
    return matches[0].lower()


def update_status_evidence(evidence: dict, fn: str, result: Any) -> None:
    """Mutate evidence from a successful get_project / get_activity tool result."""
    if not isinstance(result, dict) or "error" in result:
        return
    if fn == "get_project":
        if "status" in result:
            evidence["status"] = result.get("status")
            evidence["project_seen"] = True
        if "flags" in result:
            evidence["flags"] = list(result.get("flags") or [])
        if "project_id" in result:
            evidence["project_id"] = result.get("project_id")
    elif fn == "get_activity":
        evidence["activity_seen"] = True
        if "project_id" in result and result.get("project_id"):
            evidence["project_id"] = result.get("project_id")
        issues = []
        for item in result.get("activity") or []:
            if not isinstance(item, dict):
                continue
            if item.get("type") == "issue_open":
                issues.append({
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "severity": item.get("severity"),
                })
        evidence["open_issues"] = issues


def _downgrade_triggers(evidence: dict) -> tuple[bool, list[str]]:
    """Return (must_not_be_green, evidence notes)."""
    notes: list[str] = []
    status = evidence.get("status")
    flags = list(evidence.get("flags") or [])
    issues = list(evidence.get("open_issues") or [])

    sev1_ids = [str(i.get("id")) for i in issues if is_sev1(i.get("severity"))]
    hold = "launch_hold" in flags
    on_track = status == "on_track"

    if sev1_ids:
        notes.append(f"open Sev-1 issue(s): {', '.join(sev1_ids)}")
    if hold:
        notes.append("launch_hold flag present")
    if status is not None and not on_track:
        notes.append(f"project status is {status!r} (not on_track)")

    downgrade = bool(sev1_ids) or hold or (status is not None and not on_track)
    return downgrade, notes


def validate_status_color(proposed_output: str, evidence: dict | None) -> dict:
    """Grade draft status color against structured evidence.

    Missing or contradictory evidence fails safely (never invents a pass).
    """
    evidence = dict(evidence or {})
    claimed = extract_claimed_color(proposed_output)
    snapshot = {
        "claimed_color": claimed,
        "status": evidence.get("status"),
        "flags": list(evidence.get("flags") or []),
        "open_issues": list(evidence.get("open_issues") or []),
        "project_seen": bool(evidence.get("project_seen")),
        "activity_seen": bool(evidence.get("activity_seen")),
    }

    if claimed is None:
        return {
            "check": "status_color",
            "verdict": "fail",
            "reasons": [
                "No overall status color (Green/Yellow/Red) found in the draft."
            ],
            "evidence": snapshot,
        }

    if not evidence.get("project_seen") or evidence.get("status") is None:
        return {
            "check": "status_color",
            "verdict": "fail",
            "reasons": [
                "Insufficient structured status evidence: get_project did not "
                "provide a project status to validate the claimed color."
            ],
            "evidence": snapshot,
        }

    if not evidence.get("activity_seen"):
        return {
            "check": "status_color",
            "verdict": "fail",
            "reasons": [
                "Insufficient structured severity evidence: get_activity was not "
                "observed, so open-issue severities cannot be verified."
            ],
            "evidence": snapshot,
        }

    downgrade, notes = _downgrade_triggers(evidence)
    normal_ids = [
        str(i.get("id")) for i in (evidence.get("open_issues") or [])
        if not is_sev1(i.get("severity"))
    ]

    if claimed == "green":
        if downgrade:
            detail = "; ".join(notes) if notes else "downgrade triggers present"
            return {
                "check": "status_color",
                "verdict": "fail",
                "reasons": [
                    f"Claimed Green is not supported by source evidence ({detail})."
                ],
                "evidence": snapshot,
            }
        return {
            "check": "status_color",
            "verdict": "pass",
            "reasons": [],
            "evidence": {
                **snapshot,
                "note": (
                    "Green supported: on_track, no Sev-1, no launch_hold"
                    + (f"; normal open issues may be listed: {', '.join(normal_ids)}"
                       if normal_ids else "")
                ),
            },
        }

    # Yellow or Red
    if not downgrade:
        extra = ""
        if normal_ids:
            extra = (
                f" Normal-severity open issue(s) ({', '.join(normal_ids)}) "
                "do not, by themselves, require Yellow or Red."
            )
        return {
            "check": "status_color",
            "verdict": "fail",
            "reasons": [
                f"Claimed {claimed.capitalize()} is a false downgrade: status is "
                f"on_track with no open Sev-1 and no launch_hold.{extra}"
            ],
            "evidence": snapshot,
        }

    return {
        "check": "status_color",
        "verdict": "pass",
        "reasons": [],
        "evidence": {
            **snapshot,
            "note": "Non-green color allowed: " + "; ".join(notes),
        },
    }


def merge_verdicts(status_check: dict, llm_verdict: dict) -> dict:
    """BOTH must pass. Never drop or rewrite LLM failure reasons."""
    status_pass = status_check.get("verdict") == "pass"
    llm_pass = llm_verdict.get("verdict") == "pass"
    reasons: list[str] = []
    if not status_pass:
        reasons.extend(list(status_check.get("reasons") or []))
    if not llm_pass:
        # Preserve LLM reasons verbatim; do not filter status-color complaints.
        reasons.extend(list(llm_verdict.get("reasons") or []))

    out = {
        "verdict": "pass" if (status_pass and llm_pass) else "fail",
        "reasons": reasons,
        "status_color": status_check,
        "llm_critic": {k: v for k, v in llm_verdict.items() if k != "_usage"},
    }
    if "_usage" in llm_verdict:
        out["_usage"] = llm_verdict["_usage"]
    return out
