
# Agent Line Map: Cortex PM Chief-of-Staff Agent

> Module 1 · The Agent Line

## The workflow, decision by decision

Cortex is an AI chief-of-staff that gathers product information, drafts leadership updates, identifies risks, and proposes backlog work. Its autonomy should be limited by the potential consequences of each action.

Scoring:
- Reversibility: High = easy to undo; Low = difficult to undo.
- Blast radius: High = potentially widespread harm; Low = limited consequences.
- Measurability: High = easy to verify correctness; Low = difficult to assess.

| Decision / action | Reversibility | Blast radius | Measurability | Agent line | HITL? |
|---|---|---|---|---|---|
| Retrieve authorized project data from GitHub/Jira | High | Low | High | Below | No |
| Identify overdue tasks and potential blockers | High | Low | High | Below | No |
| Draft a weekly leadership status update | High | Low | High | Below | Review before publishing |
| Propose backlog stories based on the PRD | High | Low | Medium | Below | Review before creation |
| Recommend changes to sprint priorities | High | Medium | Medium | HITL | Required before implementation |
| Modify or overwrite existing backlog tickets | Low | High | Medium | Above | Required |
| Publish a leadership update or commit a ship date | Low | High | Medium | Above | Required |
| Mark a launch gate green or close a critical ticket | Low | High | Medium | Above | Required |

## Agent anatomy (sketch)

**Model:**
A fast, cost-effective LLM handles routine data retrieval, summarization, and drafting. More complex or ambiguous decisions can be escalated to a more capable model, but model capability does not change the agent's permissions.

**Tools:**
- Read-only access to authorized project data.
- Search across previous status updates and project documentation.
- Retrieve roadmap priorities and team norms.
- Generate draft leadership updates.
- Propose backlog stories in a review queue, capped at 10 items.
- No autonomous publishing, destructive editing, or modification of existing commitments.

**Memory:**
Retain approved project context, team norms, previous decisions, and relevant status history. Distinguish verified facts from AI-generated interpretations. Refresh outdated information and avoid retaining unnecessary sensitive data.

**Loop:**
Cortex receives a task, gathers relevant evidence, drafts an output, and submits it to a critic for validation. If the critic identifies a problem, Cortex may revise within defined limits. The loop stops when validation passes, a limit is reached, or human intervention is required.

**Bounds:**
- Maximum 8 iterations per run.
- Maximum 2 revisions.
- Maximum estimated cost of $0.50 per run.
- Maximum 10 proposed backlog items.
- Read-only access to source project data.
- Human approval required for publishing or modifying live records.
- Stop and escalate when evidence is insufficient or contradictory.

**Evals:**
Evaluate factual accuracy, source grounding, compliance with project scope, identification of blockers, and adherence to permissions. Test whether Cortex correctly escalates unsupported claims and stops when bounds are reached.

## The golden rule, applied

A decision belongs below the agent line only when mistakes are easily reversible, consequences are contained, and correctness can be measured.

**Recommend sprint priority changes:** Human approval is required because an incorrect recommendation, if implemented, could disrupt multiple teams and its impact may be difficult to measure immediately.

**Modify existing backlog tickets:** This stays above the line because an incorrect edit could erase requirements, alter commitments, or create dependencies that affect other teams. Preventing deletion alone is insufficient protection.

**Publish leadership updates or commit ship dates:** This stays above the line because incorrect information can create organizational commitments, damage credibility, and influence business decisions before the mistake is discovered.

**Mark launch gates green or close critical tickets:** This stays above the line because an incorrect decision could trigger a premature release or conceal unresolved risks. Reversing the record would not necessarily reverse the consequences.

## Hardest call

My hardest decision was whether Cortex should be allowed to modify existing backlog tickets independently.

At first, editing a ticket seems relatively low risk because the change can theoretically be reversed. But reversibility is not just about whether an undo button exists. A changed requirement or priority might trigger work across multiple teams before anyone notices.

Even prohibiting deletion is insufficient. An agent with editing permissions could overwrite the entire description of a critical task, effectively destroying its useful contents without deleting the record.

The deciding factor was blast radius.

My decision is to let Cortex autonomously analyze tickets and propose changes, but require human approval before any changes are applied to existing records.

Over time, I would consider granting narrowly scoped editing permissions only after the agent demonstrates consistent accuracy through evaluations, with version history, audit logs, and rollback mechanisms in place.

The principle guiding my decision is simple:

**Capability is not permission. The fact that an agent can perform an action does not mean it should be authorized to do so.**
