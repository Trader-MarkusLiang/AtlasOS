# ISSUE-2026-050 — UI Control Plane Redesign Needed

Date: 2026-07-06
Status: Accepted for implementation
Category: User Experience

## Source

User request: Atlas OS UI v1.3 Control Plane UX Redesign.

## Problem

The current Atlas UI exposes runtime information, but it still reads like an engineering dashboard.
The system needs a production-grade AI control-plane layout with clearer navigation, configuration
surfaces, workflow graph, and cleaner inspector/timeline structure.

## Constraints

- Do not modify runtime / cognition / decision logic.
- Do not modify event stream or causal engine.
- Do not change backend execution semantics.
- Do not introduce heavy frontend frameworks.
- Limit changes to UI structure, layout, configuration forms, visualization, and navigation.

## Acceptance Criteria

- Dashboard uses sidebar-based navigation.
- Settings page exists and can save local config.
- LLM API config and asset config are editable.
- Workflow graph renders pipeline nodes.
- Dashboard has mode switcher and execution timeline.
- Boundary scan confirms runtime and cognition remain unchanged.

## Linked Improvement Candidate

IP-2026-050 — UI Control Plane v1.3
