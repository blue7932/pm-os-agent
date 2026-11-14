# Orchestration Map: Cortex PM Chief-of-Staff Agent

> Module 3 · Orchestration & Subagents, ★ Deliverable 3
>
> ✅ **What this validates:** nothing advances unchecked, by the end you'll have proven a justified topology, a roster, and a validator with a defined fail action.
>
> Builds on your M2 Loop Spec. Only split one agent into a team when there's a real reason, coordination has a cost.

## 1. Why split? (or why not)

**Decision:** Split — Cortex (drafter) + one critic subagent.

**One-line design:** On request or at the scheduled Monday time, Cortex gathers project data, drafts an evidence-based status update, checks it with a critic, and stops when the draft is ready for human review or needs intervention. Nothing is published without human approval.

**Four reasons scored:**
| Reason | Applies? | Why |
|---|---|---|
| Separation of concerns | No | Drafting and criticizing are separate tasks; contamination between roles isn’t the driver here. |
| Parallelism | No | The critic can’t run in parallel — it reviews only after the draft is finished. |
| Independent validator | Yes | The same model that wrote the draft can’t be relied on to catch its own hallucinations, missing sources, or out-of-bounds commitments. |
| Context-window pressure | No | The critic isn’t there to share context load. |

**Why we split:** One reason holds — independent validation. Cortex needs a separate critic so a second model grades the draft before it reaches human review.

## 2. Topology

**Pattern:** single + subagents

```
[Inbound PM task / Monday cron]
        │
        ▼
[Cortex: pull project data → draft status update + propose stories (≤10)]
        │
        ▼
[Validator / Critic — own context, never saw drafting]
        │
        ├─ FAIL → return reasons to Cortex
        │         (revision 1 of 2, then 2 of 2)
        │         if still FAIL after max 2 → escalate to PM
        │         with: error · what was tried · what wasn’t
        │
        └─ PASS → [PM review checkpoint] → queued
                  (nothing published / sent / live tickets changed)
```

## 3. Roster

| Agent / subagent | Responsibility | Runs which Loop Spec |
|---|---|---|
| **Cortex** (drafter) | Pull project data; draft evidence-based status update; propose backlog stories (≤10); revise when the critic fails | M2 Loop Spec (full loop: trigger → draft → stop conditions) |
| **Critic / Validator** | Independently grade the draft against the four checks; return pass/fail + reasons; never drafts | Validation loop only (no drafting, no changing live systems) |

## 4. Communication & hand-offs

How work moves between the parts (same program for now — no special agent-to-agent protocol):

| From → To | What gets passed | How |
|---|---|---|
| You / schedule → Cortex | Which project, which time period, and what kind of ask (e.g. status update) | Normal start of a run |
| Cortex → Critic | The draft, the proposed stories, and the source facts needed to check claims | Handed off inside the same program |
| Critic → Cortex | Pass or fail, plus which checks failed and why | Short structured feedback |
| Critic → you (after 2 failed fixes) | The draft plus a clear failure report: what went wrong, what was tried, what wasn’t | Queued as “Needs Human Review — Validation Failed” |
| Critic → you (pass) | The approved-by-critic draft and stories | Queued for **your** review — not sent automatically |

## 5. The validator

- **What the critic checks:**
  1. **Show all sources** — every number has a supporting source clearly shown and linked when possible.
  2. **Correct references** — correct project names, ticket numbers, and PR numbers; do not mix up projects.
  3. **Commitments** — no unauthorized commitments (delivery dates, scope changes, or other business promises) without explicit human approval. Reporting an existing, verified commitment is OK; making a new one is not.
  4. **Queue cap** — do not propose more than 10 backlog stories at once; if more are identified, flag for human review.

- **Fail action:** Revise — return the draft to Cortex with the failure noted. After **max 2** revise passes without a pass verdict, **escalate** to PM review with a clear report of the error, what was tried, and what was not tried.

- **Pass action:** Advancing item goes to the **PM review checkpoint** only. Nothing is auto-sent or published.

## 6. State: shared vs isolated

- **Shared (both may see):** the source project facts, and the draft (plus proposed stories) under review.
- **Isolated:** the critic’s private thinking and full chat history stay out of Cortex’s drafting context. On a fail, Cortex only gets the short verdict and reasons — not the critic’s entire inner monologue — so it fixes the real problems instead of copying the critic’s wording.

## 7. Cost & latency budget

The critic adds at least **1 extra model call** per item when it passes first time. At the revision cap (max 2 revises), worst case is about **3 critic checks + 2 Cortex rewrites** before the draft reaches you as “Needs Human Review.” That extra back-and-forth is the latency cost of not trusting a self-graded draft — we’ll treat this as a hard bound in M5.
