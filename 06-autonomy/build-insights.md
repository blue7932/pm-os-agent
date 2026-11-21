# Build Insights: Cortex PM Chief-of-Staff Agent

> Module 6 · ★ Deliverable 4, what you learned building it
>
> ✅ **What this validates:** you can reflect on what building it taught you, by the end you'll have proven the friction, the learning, and the aha that changes how you'd design your next agent.

## Friction

The build fought me hardest at the critic boundary. On otherwise plausible Northstar status drafts—`on_track`, normal `#825`, no Sev-1, no `launch_hold`—the LLM critic still rejected accurate Green reports, sometimes treated `#825` as if it were a Sev-1, and pushed the drafter into Green↔Yellow revision loops until the revision cap stuck. Separately, a proposed “marketing campaign” story sat outside PRD-Northstar-v3’s in-scope list, so even when status color was right, backlog quality could still fail the run. Watching the loop burn revisions on status-color flip-flops while a real scope miss also appeared made the happy path feel unreliable without meaning the hold-for-human behavior was wrong.

## Learning

Clear prompts alone did not buy me reliable judgments. I spelled out Green/Yellow rules for both Cortex and the critic, then added deference language so the model would stop owning status color—and the critic still re-litigated color against normal `#825`. What helped was putting the status-color rule in code: structured evidence from `get_project` / `get_activity`, a deterministic Python check, and a merge that still requires the LLM critic for other quality and safety failures (never silencing a legitimate critic fail). Fourteen API-free tests passed around that merge. What remains unresolved is end-to-end reliability: I still have not demonstrated a full happy path that lands on `HITL CHECKPOINT / SUCCESS STOP`.

## Aha moment

A safe stop can be the correct outcome. I had been treating revision-cap holds as “the demo failed,” when they were often Cortex refusing to pretend the draft was finished. Shipping an agent means separating three questions: Did the task complete? Is the output good? Did we stay safe? Task completion and output quality can still be open while safety (hold, don’t publish, escalate) is doing its job. Where a rule is crisp—Green only when `on_track` + no Sev-1 + no launch hold—I would enforce it in code next time and keep the LLM for the messier checks, instead of hoping the prompt will hold the line alone.

## What you'd do differently

I'd design the validation architecture earlier, separating rules that software can enforce from judgments that genuinely require an LLM. I'd also test the critic independently before connecting it to the revision loop, so inconsistent feedback couldn't repeatedly send the drafter in circles. Finally, I'd validate proposed backlog stories against PRD scope before adding them to the approval queue. That would help Cortex catch preventable errors earlier while keeping humans responsible for consequential decisions.
