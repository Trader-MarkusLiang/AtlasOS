# ISSUE-2026-051 — UI Cognitive Control Center Redesign Needed

Date: 2026-07-06
Status: Accepted for implementation
Category: User Experience

## Source

User request: Atlas OS UI v2.0 Apple / OpenAI Grade Cognitive Control Center Redesign.

## Problem

The current Atlas UI has a functional control-plane shell, but it still carries too much
engineering-dashboard weight. The interface needs a clearer cognitive-control center hierarchy
with one primary workspace, secondary context panels, and reduced visual noise.

## Constraints

- Do not modify runtime, cognition, decision logic, event stream, LMSE, MPCE, MLE, UMIS, trust, or
  causal computation.
- Do not change backend execution semantics.
- Limit changes to UI / frontend redesign, settings surface, visual hierarchy, and workflow view.

## Acceptance Criteria

- Dashboard uses a three-zone cognitive control center:
  - left control and configuration panel,
  - center single-focus workspace,
  - right intelligence panel,
  - minimal bottom execution timeline.
- Center panel has one primary focus and no equal-weight debug layout.
- Navigation is simplified to Dashboard, Workflow, Roadmap, and Settings.
- Settings page includes LLM API config, asset config editor, and runtime parameters.
- Empty states are product-grade guidance text rather than raw Unknown values.
- Workflow graph is minimalist, highlights the active path, and supports node explanations.
- Boundary scan confirms cognition and runtime execution files were not modified for this UI change.

## Linked Improvement Candidate

IP-2026-051 — UI Cognitive Control Center v2.0
