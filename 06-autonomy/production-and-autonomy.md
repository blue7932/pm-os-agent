# Production & Autonomy: Cortex PM Chief-of-Staff Agent

> Module 6 · ★ Deliverable 5, how you'd ship it, govern it, and widen trust over time
>
> ✅ **What this validates:** you can ship it, govern it, and widen trust deliberately, by the end you'll have proven an autonomy dial, a Trust Ladder rung with its eval gate, and a governance plan.
>
> **Honesty:** targets below are **future gates**, not claimed current results. Today’s evidence: EV-QUEUE and EV-ITER **PASS**; EV-5 jailbreak **FAIL**; EV-3 recovery **not formally verified**; timeout and kill switch **proposed** only.

## Autonomy Dial by segment

Autonomy is a product decision per user, not one global setting. The dial sets how often below-the-line work still pauses for HITL for that segment; it does **not** move the M1 agent line. Publishing, ship-date commits, launch gates, critical closures, and unauthorized ticket overwrites stay above the line for everyone.

| Segment | Desired autonomy | Why |
|---|---|---|
| Product managers (initial validation focus) | Level 2 · Assisted | Cortex prepares status reports and backlog proposals; humans review and execute. Pilot validation starts here before other segments. |
| Product leadership | Level 2 · Assisted | Same assisted pattern: drafts and proposals only; leaders review before anything ships or is committed. Segment evaluated separately from the PM pilot. |
| Engineering managers | Level 2 · Assisted | Same assisted pattern for eng-facing status and planning inputs; humans retain execution. Segment evaluated separately from the PM pilot. |

## Trust Ladder

- **Current / initial target rung:** Level 2 · Assisted (prepare drafts and proposals; human reviews and executes).
- **Promotion candidate:** Level 3 · Supervised. Cortex may execute specifically authorized actions after human approval, enforced at the tool layer. Above-the-line decisions remain human-owned.
- **Eval gate to reach Level 3 (future targets, not yet achieved):** Minimum **4 weeks** and **50 evaluated runs**, including real pilot usage with PMs. Require **≥98% task success**; **zero** detected material factual errors and **zero** serious safety incidents in the window; **EV-5 jailbreak** and **EV-3 recovery** must **PASS**; **tool-side approval enforcement** must be implemented and tested. A serious trust incident **pauses** promotion until remediated and re-cleared against this gate.
- **Incident record so far:** Treat any material factual error, policy/safety violation (e.g. attempted publish, confidential leak, unauthorized commitment), or failed injection handling in production as a **trust incident**. Near misses are logged with severity and resolution. Clean window = no serious incidents and gate metrics met. **Current evidence:** EV-5 failed during controlled testing, and EV-3 remains unverified. No production incident history exists because Cortex has not been deployed. The Level 3 promotion gate is not cleared.

## Deployment plan

- **Runtime:** **Proposed serverless**, subject to execution limits appropriate to the M2 task-triggered loop (on-demand run per PM task, not always-on). Final choice confirmed at launch against latency/cost limits.
- **Operator / on-call owner:** Shared **product** and **engineering/AI ops** ownership. A **named on-call** is required before launch but is **not assigned yet**. Qualified operators may pause unsafe runs.
- **Rollback:** Pause the agent; hold questionable outputs for human review; restore a verified prompt/config/version if appropriate; rerun regression evals (including M5 bound and safety cases); resume only when clear.
- **Monitoring:** Task success rate; factual accuracy / critic outcomes; safety (escalations, jailbreak handling); human corrections; failures / stuck stops; cost-to-serve per run.

## ROI metrics (beyond adoption & tokens)

Initial measurement scope: **PMs only**.

| Metric | Target / how captured |
|---|---|
| **Outcome** | Working baseline **90 minutes** for a weekly status package; target **≤45 minutes** including human review and correction (**~50% time savings**). Capture via time study / self-report on pilot tasks. |
| **Cost-to-serve** | **Total cost per accepted report** = model + infrastructure + human review time. Track per accepted deliverable; **no dollar target invented** here. |
| **Trust incidents** | Count trust incidents and near misses; record severity and resolution time. Target for promotion window: **zero serious** incidents (see Trust Ladder gate). |

## Widen-autonomy decision rule

Widen one notch only after the Level 3 eval gate is met over the stated window (4 weeks / 50 evaluated runs, ≥98% task success, zero material factual errors and serious safety incidents, EV-5 and EV-3 PASS, tool-side approval enforcement tested)—and never by moving above-the-line actions below the M1 agent line.

## Governance & forward strategy

- **Compliance:** Organization policy overrides team preference; team overrides personal preference. Apply **data minimization**, **access controls**, and **sensitive-data safeguards**. Lasting/semantic memory writes require authorization. Do not put unnecessary PII, salaries, performance reviews, or confidential/embargoed roadmap content into prompts or company-wide drafts.
- **Safety:** Preserve the M1 agent line for everyone—no independent publishing, date commitments, critical ticket closures, or unauthorized modifications. Dangerous write tools are **absent in the prototype**; a real approval-enforcement workflow is **unimplemented**. Kill switch remains **proposed** (operator pause of unsafe runs until a dedicated control exists).
- **Reliability:** Keep implemented caps (e.g. cost $0.50/run, max revisions 2, max iterations, queue cap—EV-QUEUE and EV-ITER **PASS**). Escalate-on-stuck. **Timeout (5 min)** and dedicated **kill switch** are **proposed** only. Model-down fallback: pause new runs and route work to humans until the model path is restored. EV-5 **FAIL** and EV-3 **unverified** block claiming stronger safety readiness.
- **Strategy:** Next widen = deepen **PM** assisted usage under the Level 3 gate, then separately evaluate product leadership and engineering managers at Assisted before any dial-up. Gating eval = the Trust Ladder Level 3 gate above (including EV-5 PASS and tool-side approval enforcement).
