# Cortex: An AI Chief of Staff for Product Managers

> An AI agent that gathers project evidence, drafts leadership updates, and proposes backlog stories using automated quality checks and human reviews to keep product managers in control.

_Abbie Moore, Agentic Workflows & Loops, November 2026_

Repo: https://github.com/blue7932/pm-os-agent

This repo is my final project for the Agentic Workflows & Loops Certification, **Cortex: An AI Chief of Staff for Product Managers**. Each module’s artifact lives in its own folder; this README is the dashboard and the pitch.

---

## Module artifacts

### M1 · The Agent Line
- **Agent-line map**: [`01-agent-line/agent-line-map.md`](01-agent-line/agent-line-map.md)

### M2 · Loop Engineering
- **Loop spec**: [`02-loop-design/loop-spec.md`](02-loop-design/loop-spec.md)

### M3 · Orchestration &amp; Subagents
- **Orchestration map**: [`03-orchestration/orchestration-map.md`](03-orchestration/orchestration-map.md)

### M4 · Choose What Each Agent Step Is Allowed to See
- **Memory &amp; context plan**: [`04-memory-context/memory-and-context.md`](04-memory-context/memory-and-context.md)

### M5 · Bounds &amp; Evals
- **Bounds &amp; evals**: [`05-bounds-evals/bounds-and-evals.md`](05-bounds-evals/bounds-and-evals.md)

### M6 · Autonomy &amp; Production
- **Production &amp; autonomy plan**: [`06-autonomy/production-and-autonomy.md`](06-autonomy/production-and-autonomy.md)
- **Prototype write-up**: [`06-autonomy/prototype.md`](06-autonomy/prototype.md)

---

## Ship plan

### Autonomy dial (per segment)
Initial autonomy target: Level 2 — Assisted

Product managers (initial pilot): Cortex gathers project evidence, drafts leadership updates, and proposes backlog stories. PMs review and execute all actions.

Product leadership: Cortex prepares evidence-backed updates and recommendations. Leaders retain decision-making authority.

Engineering managers: Cortex prepares relevant status information and proposed work. Engineering managers review and execute all actions.

Expansion: Begin with product managers. Evaluate each additional segment independently before expanding access or increasing autonomy.

Non-negotiable boundary: Cortex cannot independently publish updates, commit ship dates, change launch gates, close critical tickets, or modify existing tickets without authorization.

Level 2 is the intended operating model. Cortex has not been deployed in production.

### Trust Ladder rung + eval gate
Current target: Level 2 — Assisted. Cortex prepares drafts and proposals; humans review and execute.

Next potential rung: Level 3 — Supervised. Cortex could execute specifically approved actions, but only after human approval is enforced and verified at the tool level. Human-owned decisions remain off-limits.

Requirements before promotion:
- At least 4 weeks and 50 evaluated runs, including real PM pilot usage.
- At least 98% task success.
- Zero detected material factual errors and zero serious safety incidents.
- EV-5 jailbreak and EV-3 recovery tests must both PASS.
- Tool-level approval enforcement must be implemented and tested.

Current evidence: EV-5 FAILED during controlled testing. EV-3 remains unverified. Cortex has not been deployed, so there is no production incident history.

Decision: Cortex has NOT qualified for Level 3. Any serious safety incident pauses promotion until the issue is resolved and the requirements are met again

### Deployment plan
Runtime: Proposed serverless deployment, triggered when a PM requests a task. Final architecture will depend on execution limits, latency, and cost.

Ownership: Shared responsibility between Product and Engineering/AI Operations. A named on-call owner must be assigned before launch.

Monitoring: Track task completion, factual accuracy, critic outcomes, human corrections, safety incidents, stuck runs, and cost per accepted report.

Rollback: If Cortex behaves unexpectedly, pause execution, hold questionable outputs for human review, restore the last verified version, and rerun safety evaluations before resuming.

Failure handling: Escalate unresolved tasks to humans. If the AI service becomes unavailable, pause new runs and use the manual workflow.

Current status: This is a proposed deployment plan. Cortex is a working prototype, not a production service. Dedicated operational controls, including a kill switch and five-minute timeout, are not yet implemented.

### ROI metrics + widen-autonomy rule
Primary outcome: Reduce the time product managers spend preparing weekly leadership updates.

Working baseline: 90 minutes per report (assumption, not yet measured).

Target: 45 minutes or less per report, including human review and corrections — approximately 50% time savings.

Measurement: Compare actual preparation time before and during the PM pilot.

Cost-to-serve: Track total cost per accepted report, including AI usage, infrastructure, and human review time.

Trust metrics: Monitor factual errors, safety incidents, near misses, and human corrections. Efficiency gains do not justify weakening safety requirements.

Widen-autonomy rule: Begin with product managers at Level 2 — Assisted. Consider Level 3 only after meeting the Trust Ladder evaluation requirements, including 50 evaluated runs, at least 98% task success, passing safety tests, and verified tool-level approvals.

Expansion to product leadership and engineering managers requires separate evaluation.

Current status: All ROI figures are assumptions or future targets. No production ROI has been demonstrated.

### Governance &amp; strategy
Governance: Organization policies take precedence over team preferences, which take precedence over individual preferences. Protect sensitive information through access controls, data minimization, and authorized memory updates.

Human authority: Cortex may draft reports and propose work, but publishing, ship-date commitments, launch decisions, critical ticket closures, and unauthorized modifications remain human-controlled.

Current safeguards: Cortex has no tools for dangerous external writes. It includes iteration limits, a two-revision cap, a $0.50-per-run cost cap, queue limits, and escalation when it cannot safely complete a task.

Evaluation results: Iteration-limit and queue-cap tests PASSED. The jailbreak test FAILED, and recovery behavior remains unverified.

Before production: Implement and test tool-level approval enforcement, a dedicated kill switch, timeout controls, operational monitoring, and incident response procedures.

Growth strategy: Validate Level 2 with product managers first. Expand to other user groups only after separate evaluations. Increase autonomy only when the Trust Ladder requirements are satisfied.

Principle: Cortex earns greater autonomy through demonstrated reliability and safety, not simply through successful task completion.

---

## Build insights

- **Friction point.** My biggest challenge was making the agent's quality-control loop reliable. The critic sometimes rejected drafts inconsistently, and the agent didn't always respond appropriately when evidence was missing or a revision failed. I had to refine the instructions, stop conditions, and escalation behavior so Cortex would recognize when it couldn't safely finish a task instead of continuing indefinitely or producing an unsupported answer.
- **Key learning.** I learned that telling an AI agent not to do something is not the same as preventing it from doing it. Important boundaries must be enforced through tool permissions, approval requirements, and explicit stop conditions—not just prompts. Cortex currently avoids unauthorized changes partly because it doesn't have tools that can perform them. A future version would need tested, tool-level approval enforcement before gaining more autonomy.
- **Aha moment.** My biggest aha moment was realizing that an agent doesn't have to complete every task to work correctly. Sometimes the right outcome is to stop, explain what's missing, and ask a human to intervene. Building Cortex changed how I think about success: I now distinguish between task completion, output quality, and safe behavior. An agent can fail to finish a task while still making the right safety decision.

---

_Certification submission, Agentic Workflows & Loops Certification._
