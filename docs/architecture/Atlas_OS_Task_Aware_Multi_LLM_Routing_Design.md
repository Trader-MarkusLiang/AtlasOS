# Atlas OS Task-Aware Multi-LLM Routing Design

Date: 2026-07-13
Linked Issue: `ISSUE-2026-060`
Linked IP: `IP-2026-060`
Track: Runtime/UI v1.5
Core impact: None

## Boundary

Provider Registry remains the only catalog for provider connections, health, models, and secrets.
Task routes reference provider IDs and never duplicate credentials.

```text
Provider Registry
  -> Task Routing Policy
       -> Workhorse: strict Evidence Packet
       -> Research: strict Research Synthesis Packet
       -> Decision: existing validated DecisionPacket
  -> Provider Router
  -> Role telemetry
```

The task-routing layer sits outside deterministic cognition. Original events may be copied into a
bounded, sanitized `task_context`, but Workhorse and Research output is never written back into
Event Fusion, regime state, causal weights, trust, structural state, CDE, or portfolio state.

## Roles

### Workhorse

Runs only when a real runtime responsibility contains useful text or structured source material.
It extracts claims, source references, query intent, and unknowns into a strict non-authoritative
Evidence Packet. It cannot recommend an action.

### Research

Runs for user questions, proactive research cycles, and material evidence changes. It receives the
bounded Evidence Packet plus existing cognition/portfolio context and returns synthesis,
counter-evidence, causal factors, hypotheses, and uncertainty. It cannot set the regime or action.

### Decision

Receives the unchanged Decision Contract context plus bounded research synthesis. It is the only
role parsed by the existing Decision Contract and the only fresh validated output eligible for
existing LLM feedback.

## Cadence And Deduplication

- The daemon tick remains 60 seconds.
- A pure heartbeat with no meaningful input delta makes no LLM call.
- Workhorse runs only when bounded task context contains useful source/query material.
- Research runs for a changed user/proactive/material context.
- Decision runs when a new user query, proactive cycle, material event, or changed decision context
  requires a brief.
- Stable-input hashes exclude timestamps and generated IDs so unchanged observations can reuse
  bounded task results.

## Configuration

`llm_task_routes` is stored beside `llm_registry` in ignored local user configuration. Each role
contains `enabled`, `provider_id`, `model`, `fallback_chain`, `timeout_seconds`,
`max_output_tokens`, and optional `reasoning_effort`. The legacy active provider remains the safe
compatibility default.

## Failure Policy

- A failed Workhorse call yields an explicit unavailable Evidence Packet; Research may continue
  from deterministic context.
- A failed Research call yields an explicit unavailable synthesis; Decision may continue through
  its existing contract context.
- A failed Decision chain yields the existing neutral DecisionPacket failsafe.
- Provider errors, fallback attempts, unknown usage, and unknown cost remain visible.

## Telemetry And Cost Truth

Telemetry records role, provider, model, start/end time, latency, status, fallback, trigger, prompt
hash, usage when returned, cache status, and DecisionPacket ID when relevant. Estimated cost is
computed only when provider pricing metadata exists; otherwise it is `Unknown`.

## Release Gates

- Cognitive-isolation regression.
- Role routing/fallback/failure tests.
- No-delta premium-call suppression proof.
- User-query and proactive-cycle runtime traces.
- Secret scan and safe API projection.
- zh/en browser validation.
- At least one real Decision provider call before `LIVE_PROVEN` classification.
