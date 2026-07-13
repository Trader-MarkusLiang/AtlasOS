# LLM Task Routing Goal Prompt

- Date: 2026-07-13 17:55 CST
- Session id: current Codex task
- Project: Atlas OS
- Workspace: `/Users/markus/AtlasOS`
- Task: Design and package a runnable Goal prompt for task-aware multi-LLM routing
- Status: Completed
- Branch: `codex/frontend-master-upgrade`

## User Request Summary

Design an Atlas-compatible upgrade that assigns lower-cost models to repetitive information work
and premium GPT or Claude models to final synthesis, then provide the complete execution mandate as
a plain-text Goal prompt.

## Work Done

- Audited the current Provider Registry, Provider Router, DecisionLoop LLM boundary, Settings UI,
  runtime cadence, Production Trial policy, and release gates.
- Defined three task roles: Workhorse, Research, and Decision.
- Preserved the deterministic cognition, CDE, Decision Contract, portfolio, and trading boundaries.
- Created `docs/goals/ATLAS_LLM_TASK_ROUTING_GOAL.txt` as a directly runnable Goal prompt.
- Did not start implementation and did not modify runtime or cognition code.

## Decisions

- Keep Provider Registry as the connection and secret catalog.
- Add task routing as infrastructure policy rather than a new cognition Engine.
- Keep the 60-second daemon tick independent from LLM invocation cadence.
- Allow only the validated Decision role output into the existing cognitive feedback path.
- Require a Production Trial Issue before implementation.

## Verification

- Confirmed the Goal file exists as plain UTF-8 text.
- Confirmed it contains architecture boundaries, configuration, cadence, UI, telemetry, tests,
  runtime evidence requirements, and completion classification.

## Resume Instructions

1. Read `docs/goals/ATLAS_LLM_TASK_ROUTING_GOAL.txt`.
2. Execute the Production Trial gate before changing runtime files.
3. Audit for duplicate Issues and allocate the next globally unique Issue ID.
4. Preserve local provider secrets and unrelated worktree changes.

## Open Questions

- None. Implementation has not been started.
