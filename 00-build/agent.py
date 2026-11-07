"""Cortex, a minimal, explicit agent loop you (and your coding agent) can read end
to end. This is the agent you ship: your PM chief-of-staff. You build it by
directing your coding agent (Claude Code / Cursor / Codex) to shape this file. You
never have to hand-write it.

Every bound the course talks about is visible right here in code, not buried in a
framework: the max-iteration counter, the cost cap, the revision cap, the
stop/escalate conditions, the auto-queue cap, and the absence of any publish tool.

Usage (ask your coding agent to run these for you, or run them yourself):
    python agent.py                # runs the happy-path task (weekly status update)
    python agent.py missing-data   # the stuck/escalate case
    python agent.py jailbreak       # the prompt-injection refusal case

Every run ends by showing the drafted status update in a FINAL STATUS UPDATE block
(or LAST DRAFT, held, if a bound trips), and saves it to run-output/. That file is
always a draft held for a human, it is never posted, there is no publish tool.

Requires OPENAI_API_KEY in your environment (see .env.example). Model and bounds
are read from env so you can tune them, that tuning is your M5 deliverable.

The loop is deliberately transparent (hand-written tool-calling on the openai
client) so a grader can see the machinery. Keep the bounds explicit if you rework it.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from openai import OpenAI

import tools
from critic import review
from prompts import CORTEX_SYSTEM

try:  # load .env if python-dotenv is installed; harmless if it isn't
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# --- Bounds (your M5 deliverable: tune these and justify them) ----------------
MODEL = os.environ.get("CORTEX_MODEL", "gpt-4o-mini")
MAX_ITERATIONS = int(os.environ.get("CORTEX_MAX_ITERATIONS", "8"))
MAX_REVISIONS = int(os.environ.get("CORTEX_MAX_REVISIONS", "2"))
COST_CAP_USD = float(os.environ.get("CORTEX_COST_CAP_USD", "0.50"))
MAX_QUEUE_ITEMS = int(os.environ.get("CORTEX_MAX_QUEUE_ITEMS", "10"))
# Loop Spec (M2) stuck exits — detectable, not vibes.
MAX_DATA_FAILURES = int(os.environ.get("CORTEX_MAX_DATA_FAILURES", "3"))
MAX_NO_PROGRESS = int(os.environ.get("CORTEX_MAX_NO_PROGRESS", "2"))
# Rough $ per 1M tokens for your chosen model, set to match its pricing.
PRICE_IN = float(os.environ.get("CORTEX_PRICE_IN_PER_M", "0.15"))
PRICE_OUT = float(os.environ.get("CORTEX_PRICE_OUT_PER_M", "0.60"))

# Tool results that count as a failed required-data lookup (Loop Spec: stuck).
DATA_TOOLS = {"get_project", "get_activity"}

TOOL_SCHEMAS = [
    {"type": "function", "function": {
        "name": "get_project", "description": "Look up a project by its ID (status, flags, linked PRD).",
        "parameters": {"type": "object", "properties": {
            "project_id": {"type": "string"}}, "required": ["project_id"]}}},
    {"type": "function", "function": {
        "name": "get_activity",
        "description": "Pull recent engineering activity for a project (merged PRs, open issues, Sev-1s).",
        "parameters": {"type": "object", "properties": {
            "project_id": {"type": "string"}}, "required": ["project_id"]}}},
    {"type": "function", "function": {
        "name": "search_past_updates",
        "description": "Search previous status updates and decisions for tone and precedent.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string"}}, "required": []}}},
    {"type": "function", "function": {
        "name": "get_roadmap",
        "description": "Return the roadmap. Some items are flagged confidential/embargoed.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string"}}, "required": []}}},
    {"type": "function", "function": {
        "name": "get_norms", "description": "Return the team norms / PM playbook the agent must follow.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string"}}, "required": []}}},
    {"type": "function", "function": {
        "name": "propose_stories",
        "description": "Queue a set of backlog stories for human approval (creates nothing; rejected above the item cap).",
        "parameters": {"type": "object", "properties": {
            "project_id": {"type": "string"},
            "stories": {"type": "array", "items": {"type": "string"}},
            "reason": {"type": "string"}}, "required": ["project_id", "stories"]}}},
]


class Bounds:
    """Tracks spend and trips the cost cap. This is enforced OUTSIDE the model."""

    def __init__(self):
        self.cost = 0.0

    def add(self, usage) -> None:
        self.cost += (usage.prompt_tokens * PRICE_IN
                      + usage.completion_tokens * PRICE_OUT) / 1_000_000

    def over_cap(self) -> bool:
        return self.cost >= COST_CAP_USD


OUTPUT_DIR = Path(__file__).parent / "run-output"


def banner(text: str) -> None:
    print(f"\n{'=' * 64}\n{text}\n{'=' * 64}")


def emit_deliverable(which: str, draft: str, *, accepted: bool,
                     reason: str, cost: float,
                     review_status: str | None = None) -> None:
    """Surface AND persist Cortex's drafted status update so it can't get lost in
    the scroll-back. This is still a DRAFT held for human review, never a post,
    there is no publish tool, and an escalated run is held on purpose.

    Runs on every exit: an accepted pass prints the FINAL update; a bound trip or
    escalation prints the LAST draft it managed to write plus why it was held.

    Loop Spec: revision-cap / stuck exits use
    "Needs Human Review — Validation Failed" (safe stop, not success).
    """
    if accepted:
        banner("FINAL STATUS UPDATE (draft, validator-approved, NOT posted)")
        status_line = "Queued for human review — SUCCESS (critic passed)"
    else:
        status = review_status or "Needs Human Review — Validation Failed"
        banner(f"LAST DRAFT (held, NOT posted) — {status}")
        status_line = status
    if draft.strip():
        print(draft.rstrip())
    else:
        print("(Cortex stopped before it produced a draft, nothing to show.)")
    if not accepted:
        print(f"\nWhy it was held: {reason}")
        print(f"Review status: {status_line}")

    if draft.strip() or not accepted:
        OUTPUT_DIR.mkdir(exist_ok=True)
        out = OUTPUT_DIR / f"status-update-{which}.md"
        state = "accepted by validator" if accepted else status_line
        body = draft.rstrip() if draft.strip() else "(no draft produced)"
        out.write_text(
            f"<!-- Cortex draft, {state}; NOT posted. Run cost ~ ${cost:.4f}. -->\n"
            f"<!-- {reason} -->\n\n{body}\n", encoding="utf-8")
        print(f"\nSaved draft -> {out.relative_to(Path(__file__).parent)}  "
              f"(for your review, nothing was posted)")


def run(which: str = "happy") -> None:
    client = OpenAI()
    bounds = Bounds()
    task = tools.get_task(which)
    if "error" in task:
        print(task)
        return

    banner(f"CORTEX RUN, fixture: task-{which}  (auto-queue cap {MAX_QUEUE_ITEMS} items)")
    print(task["body"])

    messages = [
        {"role": "system", "content": CORTEX_SYSTEM},
        {"role": "user", "content": f"PM task brief:\n\n{task['body']}"},
    ]
    source_log: list[str] = [task["body"]]
    revisions = 0
    data_failures = 0
    no_progress = 0
    last_draft = ""
    last_draft_fingerprint = ""

    for step in range(1, MAX_ITERATIONS + 1):
        if bounds.over_cap():
            reason = f"cost cap ${COST_CAP_USD} hit at ${bounds.cost:.4f}"
            banner(f"BOUND TRIPPED, {reason}. Halting and escalating to a human.")
            emit_deliverable(which, last_draft, accepted=False,
                             reason=reason, cost=bounds.cost,
                             review_status="Needs Human Review — Validation Failed")
            return

        resp = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOL_SCHEMAS)
        bounds.add(resp.usage)
        msg = resp.choices[0].message

        if msg.tool_calls:
            messages.append(msg)
            for call in msg.tool_calls:
                fn = call.function.name
                args = json.loads(call.function.arguments or "{}")
                result = tools.TOOLS[fn](**args)
                source_log.append(f"{fn}({args}) -> {json.dumps(result)}")
                print(f"\n[step {step}] TOOL {fn}({args})")
                print(f"          -> {json.dumps(result)[:300]}")
                messages.append({"role": "tool", "tool_call_id": call.id,
                                 "content": json.dumps(result)})
                # STUCK: required data unavailable.
                # Hard miss (project_not_found) stops immediately — do not wander
                # into other projects or invent a draft. Soft/transient errors
                # accumulate to MAX_DATA_FAILURES.
                if fn in DATA_TOOLS and isinstance(result, dict) and "error" in result:
                    err = result.get("error")
                    data_failures += 1
                    print(f"          !! data failure {data_failures}/{MAX_DATA_FAILURES}"
                          f" ({err})")
                    hard_miss = err == "project_not_found"
                    if hard_miss or data_failures >= MAX_DATA_FAILURES:
                        reason = (
                            f"required data unavailable"
                            + (f" ({fn} -> {err})" if hard_miss else
                               f" after {MAX_DATA_FAILURES} attempts "
                               f"(last: {fn} -> {err})")
                        )
                        banner(f"STUCK STOP, {reason}. Never invent missing info. "
                               f"Run cost ≈ ${bounds.cost:.4f}")
                        emit_deliverable(
                            which, last_draft, accepted=False, reason=reason,
                            cost=bounds.cost,
                            review_status="Needs Human Review — Validation Failed")
                        return
                if fn == "propose_stories" and isinstance(result, dict):
                    # ESCALATE: story batch over configured limit.
                    if result.get("error") == "batch_exceeds_queue_cap":
                        reason = ("story batch exceeds queue cap "
                                  f"({result.get('count')} > "
                                  f"{result.get('cap_items')}); "
                                  "pause and request human approval")
                        banner(f"ESCALATE STOP, {reason}. "
                               f"Run cost ≈ ${bounds.cost:.4f}")
                        emit_deliverable(
                            which, last_draft, accepted=False, reason=reason,
                            cost=bounds.cost,
                            review_status="Needs Human Review — Awaiting Approval")
                        return
            continue

        # No tool calls => Cortex produced a proposed output. Validate it.
        proposed = msg.content or ""
        fingerprint = " ".join(proposed.split()).lower()
        if fingerprint and fingerprint == last_draft_fingerprint:
            no_progress += 1
            print(f"\n-> no progress {no_progress}/{MAX_NO_PROGRESS} "
                  f"(identical draft)")
            if no_progress >= MAX_NO_PROGRESS:
                reason = (f"no progress across {MAX_NO_PROGRESS} iterations "
                          "(identical drafts)")
                banner(f"STUCK STOP, {reason}. Run cost ≈ ${bounds.cost:.4f}")
                emit_deliverable(
                    which, proposed or last_draft, accepted=False, reason=reason,
                    cost=bounds.cost,
                    review_status="Needs Human Review — Validation Failed")
                return
        else:
            no_progress = 0
            last_draft_fingerprint = fingerprint
        last_draft = proposed
        print(f"\n[step {step}] PROPOSED OUTPUT:\n{proposed}")

        # Model chose to escalate (confidential, date commit, missing data, etc.).
        if proposed.lstrip().upper().startswith("ESCALATE"):
            reason = "model escalated to human (HITL / agent-line checkpoint)"
            banner(f"ESCALATE STOP, {reason}. Run cost ≈ ${bounds.cost:.4f}")
            emit_deliverable(
                which, proposed, accepted=False, reason=reason,
                cost=bounds.cost,
                review_status="Needs Human Review — Awaiting Approval")
            return

        banner("CRITIC, independent validation")
        verdict = review(client, MODEL, proposed, "\n".join(source_log))
        # Estimate critic spend too.
        bounds.cost += (verdict["_usage"]["prompt"] * PRICE_IN
                        + verdict["_usage"]["completion"] * PRICE_OUT) / 1_000_000
        print(json.dumps({k: v for k, v in verdict.items() if k != "_usage"}, indent=2))

        if verdict["verdict"] == "pass":
            # SUCCESS: critic passed; draft queued for review; nothing posted.
            banner(f"HITL CHECKPOINT / SUCCESS STOP, status update + any proposed "
                   f"stories queued for your review. Nothing posted, no commitments "
                   f"made. Run cost ≈ ${bounds.cost:.4f}")
            emit_deliverable(which, proposed, accepted=True,
                             reason="validator passed; queued for human review",
                             cost=bounds.cost)
            return

        if revisions >= MAX_REVISIONS:
            # STUCK: revision limit without critic pass (safe stop, not success).
            reason = f"validator rejected {MAX_REVISIONS}x (revision cap)"
            banner(f"STUCK STOP, REVISION CAP ({MAX_REVISIONS}). "
                   f"Needs Human Review — Validation Failed. "
                   f"Run cost ≈ ${bounds.cost:.4f}")
            emit_deliverable(
                which, last_draft, accepted=False, reason=reason,
                cost=bounds.cost,
                review_status="Needs Human Review — Validation Failed")
            return

        revisions += 1
        print(f"\n-> critic rejected; revision {revisions}/{MAX_REVISIONS}")
        messages.append(msg)
        messages.append({"role": "user", "content":
                         "A validator rejected that for these reasons: "
                         f"{verdict['reasons']}. Fix it or escalate."})

    banner(f"MAX ITERATIONS ({MAX_ITERATIONS}) reached without finishing. "
           f"Escalating. Run cost ≈ ${bounds.cost:.4f}")
    emit_deliverable(
        which, last_draft, accepted=False,
        reason=f"max iterations ({MAX_ITERATIONS}) reached",
        cost=bounds.cost,
        review_status="Needs Human Review — Validation Failed")


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "happy")
