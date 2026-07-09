# Atlas OS Workflow Map Baseline

Date: 2026-07-09 18:40 CST

## Scope

This baseline audits the current `/workflow` route before the Workflow Map v2 rebuild.

Allowed scope for the rebuild is UI/product only:

- `ui/**`
- workflow rendering
- read-only workflow state projection
- visualization interaction
- i18n
- verification artifacts

No cognitive semantics, Decision Contract semantics, runtime scheduler behavior, CDE authority,
trading execution, broker integration, portfolio mutation, forecast semantics, or self-iteration
semantics may be modified.

## Current Route

- FastAPI `/workflow` route calls `workflow_content(state)` from `ui/pages/product_views.py`.
- Stdlib fallback `/workflow` route also calls `workflow_content(state)`.
- `ui/pages/workflow.py` still exists but is not the active product-shell route.
- `ui/components/workflow_graph.py` still defines a minimal eight-node graph for older shell use.

## Current Behavior Evidence

Baseline browser evidence:

- Screenshot: `99_Verification/artifacts/workflow_map/baseline_workflow_before_rebuild.png`
- URL: `http://127.0.0.1:8765/workflow`
- Title: `认知控制中心 - Atlas OS`
- Architecture image section present: yes
- Compact Global System Map present: yes
- Workflow nodes in compact map: 18
- Simple / Expert mode controls: missing
- Latest Tick / Full Architecture controls: missing
- Dedicated flow inspector: missing
- Legend: missing

## Current Defects

| Defect | Evidence | Status |
|---|---|---|
| STATIC_GRID | Compact map is generated as static SVG-style node rectangles with no stage model. | PRESENT |
| CROSS_ROW_FLOW_AMBIGUOUS | Nodes are arranged in rows; cross-row dependencies are not explicit. | PRESENT |
| MAIN_PATH_NOT_VISIBLE | Latest runtime tick path is inferred only by fill color; no explicit Latest Tick mode. | PRESENT |
| ACRONYM_HEAVY | LMSE / MPCE / MLE appear as primary labels. | PRESENT |
| WEAK_HIERARCHY | Nodes have equal visual weight; stages are not dominant. | PRESENT |
| INSPECTOR_DISCONNECTED | Bottom detail block shows only selected label and short description. | PRESENT |
| NO_CURRENT_TICK_PATH | Runtime tick state is not projected into node status classes. | PRESENT |
| NO_DEPENDENCY_VIEW | Click selection does not mark upstream/downstream relationships. | PRESENT |
| NO_STATE_ENCODING | ACTIVE / COMPLETED / WAITING / DEGRADED / FAILED / NOT_USED states do not exist. | PRESENT |
| NO_PROGRESSIVE_DISCLOSURE | No Simple / Expert mode; acronyms are visible by default. | PRESENT |

## Baseline Verdict

The current Workflow page does not satisfy the Workflow Map Rebuild Goal. It provides useful
architecture imagery and a compact path diagram, but it remains a mostly static visualization and
does not function as an interactive cognitive flow explorer.

Required rebuild direction:

1. Replace the static grid with five dominant stages: Input, Understand, Model, Decide, Learn.
2. Add explicit feedback loop from Learn back to Memory / World Model.
3. Add Simple and Expert modes with concept-first default labels.
4. Add Latest Tick and Full Architecture modes.
5. Add node selection, upstream/downstream highlighting, state encoding, legend, context inspector,
   zoom controls, keyboard interaction, and exact E2E validation.
