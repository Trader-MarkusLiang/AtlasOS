# GOAL 00 — REPOSITORY TRUTH BASELINE

## Objective

Establish an evidence-based understanding of the actual Atlas OS system.

Do not trust prior reports.

## Required Audit

Inspect:

- README
- roadmap
- VERSION
- CHANGELOG
- runtime/
- runtime/cognition/
- runtime/llm/
- runtime/telemetry/
- runtime/config/
- ui/
- 99_Verification/
- current branch history

Classify major capabilities:

- ACTIVE
- PARTIAL
- UI_ONLY
- MOCK_ONLY
- DISCONNECTED
- STALE_DOC
- NOT_IMPLEMENTED

## Required Focus

Verify:

- real daemon execution
- real scheduler execution
- real DecisionLoop
- real LLM routing
- real market ingestion
- real portfolio context
- real forecast lifecycle
- real self-iteration
- real daily cycle
- UI-to-runtime path

## Deliverables

Create:

99_Verification/GOAL_00_Truth_Baseline_Report.md

Update:

docs/goals/status/GOAL_STATUS.json

## Acceptance

Goal is complete only when:

- actual execution paths are mapped
- stale claims are identified
- fixture-only claims are separated
- current blockers are explicit
- next Goal can use a reliable baseline

## Transition

When PROVEN_COMPLETE:

Automatically proceed to:

GOAL_01_USER_ACTIVATION
