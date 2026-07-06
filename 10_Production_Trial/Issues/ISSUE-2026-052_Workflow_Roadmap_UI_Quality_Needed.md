# ISSUE-2026-052 — Workflow and Roadmap UI Quality Needed

Date: 2026-07-06
Status: Accepted for implementation
Category: User Experience

## Source

User reported that the Workflow and Roadmap pages are poorly designed and implemented. Screenshots
show `/roadmap` rendering raw JSON in the browser and `/workflow` rendering an unstyled dark block
with plain links.

## Problem

The dashboard redesign improved the primary control center, but Workflow and Roadmap remain below
product quality. They should be readable, guided, and visually consistent with the Atlas OS v2.0
cognitive control center.

## Constraints

- UI / frontend only.
- Do not modify runtime, cognition, decision logic, event stream, LMSE, MPCE, MLE, UMIS, trust, or
  causal computation.
- Preserve machine-readable roadmap access through explicit JSON mode.

## Acceptance Criteria

- `/workflow` renders a polished product-grade workflow page, not plain links.
- `/workflow` shows active path, stage cards, stage detail, and boundary information.
- `/roadmap` renders a polished roadmap page by default in the browser, not raw JSON.
- Roadmap JSON remains accessible through `/roadmap?format=json` and `/roadmap.json`.
- Pages follow the Atlas OS v2.0 visual system.
- UI pages do not import cognitive modules.

## Linked Improvement Candidate

IP-2026-052 — Workflow and Roadmap UI Polish
