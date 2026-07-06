# Atlas Production Trial

Atlas Production Trial is the operating period after RC and before Final.

Architecture is frozen during Production Trial.

Allowed:

- Daily real usage.
- Bug fixes.
- Usability polish.
- Issue recording.
- Weekly review.
- Improvement candidate discussion.

Forbidden:

- New Engine.
- AES implementation.
- Workflow redesign.
- Architecture expansion.
- Direct implementation from a new idea.

Core rule:

```text
No Issue, No Iteration.
```

没有 Issue，就不进入迭代。

## Directory Map

| Directory | Purpose |
|---|---|
| `Issues/` | Raw Production Trial issues observed from real usage. |
| `Weekly_Reviews/` | Weekly operating reviews of repeated and critical issues. |
| `Improvement_Candidates/` | Repeated issue patterns being considered for IP conversion. |
| `Accepted_Issues/` | Issues accepted for discussion or IP conversion. |
| `Rejected_Issues/` | Issues rejected, deferred, or recorded for traceability. |
| `Architecture/` | Proposed architecture and roadmap documents that are not implementation authority. |

## Operating Rule

Every future Atlas iteration must reference at least one Issue.

An Issue is not an Improvement Proposal. An Issue becomes an IP only after discussion,
prioritization, and user approval.

## Current Architecture Roadmap

- `Architecture/Atlas_OS_v0.4_Cognitive_Market_OS_Roadmap.md`

The v0.4 roadmap is proposed direction only. It does not authorize DSA integration, runtime
refactoring, causal-engine implementation, CDE changes, trading execution, or portfolio automation.

Implemented runtime trials must remain bounded by their accepted Issues and IPs. `IP-2026-029`
adds a local Causal Intelligence Layer trial only; it does not authorize CDE formula changes,
Decision Brief strategy changes, trading execution, Buy / Sell output, machine learning, or
portfolio automation.

`IP-2026-030` adds a local Market World Model Layer trial only. Its scenario trajectories are
interpretable structural simulations, not forecasts, trading authority, CDE authority, portfolio
automation, or Buy / Sell output.

`IP-2026-031` adds a local Latent Market Structure Engine trial only. Its attractor and phase-space
outputs are interpretable structure diagnostics, not prediction output, trading authority, CDE
authority, portfolio automation, or Buy / Sell output.

`IP-2026-032` adds a local Market Physics Constraint Engine trial only. Its conservation,
entropy, invariant, and stability outputs are constraint diagnostics, not forecasting output,
trading authority, CDE authority, portfolio automation, or Buy / Sell output.

`IP-2026-033` adds a local Market Law Emergence Engine trial only. Its emergent law and adaptive
constraint outputs are interpretable diagnostics, not prediction output, trading authority, CDE
authority, portfolio automation, black-box optimization, or Buy / Sell output.

`IP-2026-034` adds a local Unified Market Intelligence Core trial only. Its unified state,
closed-loop feedback, self-referential causality, co-evolution, and internal interpretation-weight
outputs are interpretable cognition diagnostics, not prediction output, trading authority, CDE
authority, portfolio automation, signal-generator behavior, black-box prediction, or Buy / Sell
output.

`IP-2026-035` adds a local Bidirectional Perception Loop trial only. Its perception weight fields
and input deformation affect EventStream priority and perception metadata before Fusion, but remain
bounded observation-layer diagnostics. They are not prediction output, trading authority, CDE
authority, portfolio automation, Event Fusion core logic changes, or Buy / Sell output.
