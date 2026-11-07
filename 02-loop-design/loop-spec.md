# Loop Spec: Cortex PM Chief-of-Staff Agent

> Module 2 · Loop Engineering, ★ Deliverable 2
>
> ✅ **What this validates:** the agent knows when to run and when to stop, by the end you'll have proven a one-page Loop Spec with a trigger, a definition of "done," and explicit stop conditions.
>
> Your one-page blueprint for how the work you handed to the agent (M1) actually *runs*.
> An agent is just a prompt that fires itself, this spec says when it fires, what "done" means, and what it needs to do the job. Living document; refine as the course progresses.

## 1. Trigger & loop type

**Chosen type:** hook (primary) · cron (backup)

**Why:** Hook makes sense because Cortex should respond when someone requests a status update or asks it to triage incoming PM work. Cron (Monday morning) ensures a weekly draft gets prepared even if nobody asks.

**Ruled out:** Heartbeat — frequent polling is unnecessary. Goal as the trigger — Cortex should work on specific requests, not pursue open-ended objectives.

**Dedupe / idempotency:** Use project + reporting period + task type as a unique identifier. If a matching draft already exists, update or flag it rather than create a duplicate. Never overwrite an approved draft without human permission.

## 2. Goal / definition of done

**Goal:** Produce an accurate, useful PM status update grounded in available project information, ready for human review.

**Definition of done (all must be true):**
- A draft has been created and saved.
- Its claims are supported by available source information.
- The independent critic has passed the draft.
- The draft is queued for human review.
- Nothing has been sent, published, or changed in live project systems.

**If critic fails at revision limit:** Save the draft with a clear "Needs Human Review — Validation Failed" status. This is a safe stop, not successful completion.

**Hard limits (never "done" if these happened):** Cortex must never send updates, commit delivery dates, or create or modify live tickets without explicit human approval.

## 3. Stop conditions

| Condition | What it looks like | What happens |
|---|---|---|
| **Success** | Draft is saved, grounded in available data, passes the critic, and is queued for human review. | Mark the drafting task complete. Do not publish or send anything. |
| **Stuck / give up** | Required data unavailable after 3 attempts, OR revision limit reached without critic pass, OR no progress across 2 iterations. | Stop, log the reason, preserve any useful draft, flag for human review. Never invent missing information. |
| **Escalate to human** | Confidential/embargoed information, a delivery-date commitment, a story batch over the configured limit, or any action that would publish or modify live systems. | Pause that action and request explicit human approval. Approval applies only to the specific proposed action. |

## 4. State

**Working set Cortex retains:**
- Project identity and reporting period.
- Verified project facts and their sources.
- The previous approved status update.
- The current draft and its approval status.
- Critic feedback and validation results.
- Proposed stories awaiting human review.
- Run status and identifiers to prevent duplicate drafts.

**Scope:** Memory is scoped to the specific project and reporting period. Approved historical updates stay available for reference, but unnecessary working data is not carried indefinitely.

**Hard boundaries:**
- Never mix confidential information between projects.
- Never treat an unapproved draft or proposed story as an established fact.
- Never treat previous human approval as permission for future actions.
- Keep source references so claims can be verified.
- Restrict access to sensitive information based on project permissions.

## 5. The five things a loop can lean on

_`state` is always-on. Below: current capabilities vs planned. Context plan (M4) and bounds & evals (M5) land in later deliverables, not here._

| Component | For Cortex |
|---|---|
| **Work tree** (isolated workspace per run, a git worktree) | **Not needed yet** for the current single-run prototype. Consider isolated workspaces later if multiple agents or concurrent runs can modify files. |
| **Skills** (reusable capabilities) | **Planned (not yet implemented as reusable skills):** `draft_status_update`, `propose_stories`, `escalate_for_approval`. Today these behaviors live inline in the main loop / tools, not as named skill packages. |
| **Plugins / connectors** (tools & access, optional if you don't have one yet) | **Current:** mock tools + sample data in `00-build` (`get_project`, `get_activity`, `search_past_updates`, `get_roadmap`, `get_norms`, `propose_stories`, etc.). **Planned:** real project-management and messaging integrations — future work, not current capability. |
| **Subagents** (independent check when the loop can't grade itself) | **Current:** `critic.py` is a separate model call that never saw the drafting context; it returns pass/fail + reasons on proposed output vs source data. `agent.py` owns the revision cap that stops a critic↔drafter loop. This is an independent validator call, not a fully orchestrated multi-agent team. **Additional specialized subagents:** not needed yet → M3 `orchestration-map.md`. |
| **State tracking** | **Designed (Section 4 working set):** scoped by project + reporting period, with hard boundaries against confidential leakage and treating unapproved drafts as facts. **Currently persisted in the build:** in-run source log, draft written to `run-output/`, critic verdicts, revision count, and queue results for the active run. **Proposed for future persistence:** durable per-project/period working set (draft status, approved history, dedupe IDs) across runs. |

> Context plan (M4) and the hand-off to bounds & evals (M5) come in later modules, you'll add them to their own deliverables then, not here.

## Link to live loop

[`00-build/agent.py`](../00-build/agent.py)
