# Context Engineering & Memory: Cortex PM Chief-of-Staff Agent

> Module 4 · Context Engineering & Memory
>
> ✅ **What this validates:** the agent reasons on the right, safe inputs, by the end you'll have proven a context budget, per-source retrieve-vs-long-context decisions, and a memory map with risk mitigations.
>
> 🗂️ **How the lab maps to this file:** In **Part A** (before the lecture) you don't edit this file, you rough-draft on scratch, focused on the per-source calls in **section 2** plus a quick remember/forget + "how it rots" sketch. In **Part B** (after the lecture) you complete **all five sections**; the Lab Guide's guided builder writes this file for you to copy in and commit.

## 1. Context budget

Each loop iteration cannot carry every available source. Cortex should prioritize context in this order:

1. **Current task brief and its instructions** — define the assignment and non-negotiables for the run.
2. **Current, authorized project activity and metrics** — the evidence for this week's status call.
3. **Relevant roadmap information** — only entries that are authorized and relevant; exclude confidential or unauthorized items.
4. **Team norms and approval requirements** — the rules that govern status language, escalation, and what stays human.
5. **Relevant past updates** — historical comparison for tone and precedent, not a full archive dump.

**Design principle:** use retrieval to limit large or growing sources to relevant, citable evidence; include small, essential documents in full. Critical approval rules must also be enforced in code (tools and stop conditions), not merely remembered by the model.

## 2. Retrieve vs. long-context: per source

For each data source, decide: **retrieve** (narrow a large/changing corpus to the relevant slice) or **long-context** (just include a bounded set you can reason over).

| Source | Size / volatility | Decision | Why (deciding factor) |
|---|---|---|---|
| GitHub/Jira activity | Large; changes constantly | **Retrieve** | **Volatility** — retrieve the current project's relevant reporting period, not the full history. |
| Past status updates | Unbounded; accumulates over time | **Retrieve** | **Size** — historical reports grow; retrieve only the relevant previous updates. |
| Roadmap | Medium; includes confidential flags | **Retrieve** | **Citation/audit and access control** — retrieve authorized, relevant entries and exclude confidential information before it reaches the model. |
| Team norms / playbook | Small, bounded | **Long-context** | **Size** — include the entire current approved document so applicable rules are not missed. |
| This week's task brief | Small, bounded (~two pages) | **Long-context** | **Size** — include the complete brief so Cortex understands the full assignment. |

## 3. Retrieval quality plan

This is a **proposed design** for agentic retrieval quality — not a claim that every safeguard below is already implemented in Cortex's Python code. The goal is to move beyond naive "embed → top-k → stuff" by tying each source to the failure mode it must prevent.

| Source | Mode | Safeguards selected | Why needed |
|---|---|---|---|
| GitHub/Jira activity | Retrieve | **Routing** — search the correct project and reporting period. **Document grading** — exclude irrelevant or outdated activity. **Reranking** — use conditionally when many results compete; skip when only a few are relevant. **Self-verification** — confirm reported metrics and claims are supported by retrieved evidence. **Caching** — avoid stale activity; use freshness checks if caching is necessary. | Activity is large and volatile; wrong project/period, outdated items, or unverified metrics produce a bad status call. |
| Past status updates | Retrieve | **Document grading** — confirm the correct project and reporting period. **Self-verification** — distinguish historical figures from current figures. **Reranking** — optional when many plausible matches return. | The archive grows over time; mixing last week's numbers with this week's is a common hallucination path. |
| Roadmap | Retrieve | **Access filtering** — exclude confidential or unauthorized entries *before* they reach the model (mandatory security control, not merely an AI retrieval technique). **Document grading** — select relevant, authorized entries. **Self-verification** — verify milestones and dates against approved evidence; label unconfirmed dates appropriately. | Confidential leakage and invented GA dates are agent-line failures; filtering must happen in infrastructure where possible. |
| Team norms / playbook | Long-context | **Caching** — cache the full document for efficiency. **Version check** — confirm version or last-modified date before each run. **Include in full** — load the current approved version entirely. | The playbook is small but rule-critical; a stale or partial copy can miss an approval or confidentiality rule. |
| Current task brief | Long-context | **Include in full** — pass the entire brief so Cortex receives all instructions. | The brief is bounded (~two pages); truncating it risks missing constraints (e.g. "nothing goes out until reviewed"). |

## 4. Memory map (your PM brain)

Proposed memory design for Cortex (what each memory type *should* store and retain). This is a design target for the PM brain — not a claim that a durable memory store is already wired into the current Python loop beyond per-run working state and fixture-backed tools.

| Memory type | What Cortex stores | Scope / TTL |
|---|---|---|
| **Working** (in-loop) | Current task, retrieved evidence, draft, critic feedback, and revision count. | Current run only. Clear temporary working state when the run finishes. |
| **Episodic** (past runs) | Brief records of previous runs, outcomes, critic failures, and rejection reasons — enough to spot recurring problems without keeping every intermediate draft. A one-time formatting exception may be recorded here but must **not** automatically change long-term preferences. | Retain for **90 days**, subject to company policy. |
| **Semantic** (durable facts/prefs) | Approved, reusable preferences (report format, writing style, durable team standards). Do **not** store tentative launch dates as permanent facts — check the authoritative roadmap instead. | Review every **90 days**; update only when an authorized person confirms a lasting change. |
| **Shared** (across agents) | Verified source data, approved metrics, and source references available to Cortex **and** its independent critic. Both agents may access the same evidence; their reasoning stays isolated. | Retain only while current and authorized; refresh or invalidate when source data changes. |

## 5. Memory risks & mitigations

Proposed risk controls. Some related protections already exist in code (e.g. no publish tool, queue caps, stuck stops, confidential roadmap flags in fixtures/prompts); the rows below are the fuller memory-governance design, not an inventory of what the Python files already enforce.

| Risk | Cortex example | Mitigation |
|---|---|---|
| **Drift** | Cortex gradually changes its reporting format based on one-time requests. | Keep approved preferences authoritative. Record temporary exceptions as appropriate (e.g. in episodic memory), but require confirmation before changing semantic memory. |
| **Poisoning** | An untrusted GitHub comment tells Cortex to bypass human approval or change its operating rules. | Treat retrieved content as **data, not instructions**. Only authorized sources can change durable policies. Enforce critical permissions at the tool layer. |
| **Staleness** | Cortex reports an outdated launch date or metric from memory. | Verify time-sensitive information against current authoritative sources before reporting. Refresh or invalidate outdated memory. |
| **PII / retention** | Cortex unnecessarily accesses or retains employee salaries, performance reviews, contact details, or confidential project information. | Minimize what is retrieved and retained, enforce access restrictions, and delete sensitive information per defined retention periods and company policy. |
