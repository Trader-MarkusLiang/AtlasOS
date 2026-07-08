# Atlas OS Frontend Master Baseline

Date: 2026-07-08 22:35-22:58 CST

Branch: `codex/frontend-master-upgrade`

HEAD: `d6871a1 cleanroom: prove CR08 real-duration stability`

Audit mode: fresh current-repository frontend audit before redesign.

## Scope

This baseline audits the real current Atlas OS frontend against the Frontend Master Goal. It does
not implement the redesign and does not modify cognition, runtime scheduler semantics, Decision
Contract semantics, CDE authority, trading execution, broker integration, or portfolio mutation.

Allowed scope for later repair remains UI/product layer plus minimum read-only API adapters where
needed.

## Sources Inspected

- `README.md`
- `VERSION.md`
- `CHANGELOG.md`
- `00_Core/Atlas_Core.md`
- `00_Core/Atlas_Principles.md`
- `00_Core/Seven_Layer_Reasoning.md`
- `99_Verification/Audit_Methodology.md`
- `99_Verification/Release_Gate.md`
- `ui/app_server.py`
- `ui/pages/`
- `ui/components/`
- `ui/i18n/i18n.py`
- `web/`
- `runtime/state_store.py`
- `runtime/portfolio_context.py`
- `runtime/market_intelligence.py`
- `runtime/forecast_ledger.py`
- `runtime/llm/provider_registry.py`
- `runtime/telemetry/replay_engine.py`

## Current Running State

- Existing unrelated listeners before audit:
  - port `5000`: `ControlCe`
  - port `8000`: `Python`
- Audit UI instance started on `127.0.0.1:8765`.
- Audit UI process:
  - PID `96265`
  - command `Python`
  - listening on `127.0.0.1:8765`
- Current worktree had unrelated pre-existing verification artifacts:
  - modified `99_Verification/artifacts/goal_07_autonomous_operations/operations_result.json`
  - untracked `99_Verification/artifacts/goal_01_user_activation/`

## Evidence Artifacts

Fresh artifacts were created under:

`99_Verification/artifacts/frontend_master/`

Key files:

- `http_route_audit.json`
- `browser_visual_audit_1440.json`
- `responsive_audit.json`
- `home_1440.png`
- `dashboard_1440.png`
- `portfolio_1440.png`
- `markets_1440.png`
- `predictions_1440.png`
- `learning_1440.png`
- `workflow_1440.png`
- `roadmap_1440.png`
- `dev_registry_1440.png`
- `settings_1440.png`
- `setup_1440.png`
- `system_guide_1440.png`

## Route Audit Summary

All required routes returned HTTP 200 during audit:

- `/`
- `/setup`
- `/dashboard`
- `/portfolio`
- `/markets`
- `/predictions`
- `/learning`
- `/workflow`
- `/roadmap`
- `/dev-registry`
- `/settings`
- `/system-guide`

This means the current frontend is not broadly broken. The main issue is product experience,
information architecture, visualization quality, navigation consistency, and ordinary-user clarity.

## Page Classification

| Route | Current H1 / First Signal | Classification | Exact Defects |
|---|---|---|---|
| `/` | `NEUTRAL` | `FUNCTIONAL_BUT_ENGINEERING_STYLE`, `WEAK_VISUAL_HIERARCHY`, `MISSING_VISUALIZATION`, `INCONSISTENT_NAV` | Home still violates the master goal by using the action/state as the hero. It does not first answer what changed, why it matters, portfolio impact, watch triggers, or invalidation. It has no SVG/canvas visualizations and uses a standalone local nav instead of a global shell. |
| `/setup` | `设置 Atlas OS` | `FUNCTIONAL_BUT_ENGINEERING_STYLE`, `TEXT_HEAVY`, `INCONSISTENT_NAV`, `MIXED_LANGUAGE` | Setup is useful but only 7 visible steps, not the required 10-step onboarding. It lacks clear progress/back-next structure. It is not inside the global shell. Some provider/model/base URL language remains mixed. |
| `/dashboard` | `ATTENTION_EXPANSION` in browser audit | `CARD_OVERLOAD`, `RAW_DATA_LEAK`, `WEAK_VISUAL_HIERARCHY`, `INCONSISTENT_NAV`, `STALE_SERVER_RISK` | `/dashboard` uses a different shell than Home and Settings. 1440px screenshot shows horizontal overflow; 1280px also overflows. HTTP audit found `Unknown`, `null`, and `{}` literals in generated HTML. It has many panels competing with the center focus. |
| `/portfolio` | `组合上下文` | `FUNCTIONAL_BUT_ENGINEERING_STYLE`, `TEXT_HEAVY`, `MISSING_VISUALIZATION`, `INCONSISTENT_NAV` | Portfolio is table-first and text-first. It has one table, no SVG/canvas, no exposure treemap/bubble map, no risk cluster graph, no interactive theme visualization, and no in-page ordinary asset editor. |
| `/markets` | `市场智能` | `FUNCTIONAL_BUT_ENGINEERING_STYLE`, `TEXT_HEAVY`, `MISSING_VISUALIZATION`, `RAW_DATA_LEAK`, `INCONSISTENT_NAV` | Markets leads with status/degraded/events and channel tables. It exposes `events_enqueued`-style runtime concepts and observations rather than a market landscape. It has two tables, no trajectory, no attention-vs-liquidity phase view, and no theme landscape. |
| `/predictions` | `预测账本` | `FUNCTIONAL_BUT_ENGINEERING_STYLE`, `MISSING_VISUALIZATION`, `RAW_DATA_LEAK`, `TEXT_HEAVY`, `INCONSISTENT_NAV` | Predictions is ledger/table-first. It lacks calibration chart, outcome summary visualization, confidence reliability buckets, largest-miss story cards, and timeline. The create form writes raw JSON into a `<pre>` result after submission. |
| `/learning` | `学习与责任链` | `TEXT_HEAVY`, `MISSING_VISUALIZATION`, `WEAK_VISUAL_HIERARCHY`, `INCONSISTENT_NAV` | Learning is only three metric cards. It does not show the required Before -> Reality -> Error -> Trust Update -> Hypothesis Reweight -> Current View flow, and has no trust evolution, hypothesis competition, or belief-change visualization. |
| `/workflow` | `From event to bounded feedback.` | `FUNCTIONAL_BUT_ENGINEERING_STYLE`, `MISSING_VISUALIZATION`, `INCONSISTENT_NAV`, `MIXED_LANGUAGE` | Workflow is improved and clickable, but it is a standalone English page with only eight internal stages. It does not show the full required chain from External Information through Self-Iteration and Decision Brief, has no pan/zoom, and does not show live/degraded state per node. |
| `/roadmap` | `master goal complete: production trial candidate, not release candidate` | `FUNCTIONAL_BUT_ENGINEERING_STYLE`, `CARD_OVERLOAD`, `WEAK_VISUAL_HIERARCHY`, `INCONSISTENT_NAV`, `MIXED_LANGUAGE` | Roadmap is first-class compared with older pages, but it uses a long machine-like current-stage phrase as H1, has 22 card-like elements at 1440px, does not share the global shell, and has no zh/en parity. |
| `/dev-registry` | `Atlas OS Development Registry` | `FUNCTIONAL_BUT_ENGINEERING_STYLE`, `CARD_OVERLOAD`, `TEXT_HEAVY`, `INCONSISTENT_NAV`, `MIXED_LANGUAGE` | Dev Registry renders useful evidence but still resembles an audit table. It has two tables, many boxes, an English-only shell, and no consistent global status/provider/freshness controls. |
| `/settings` | `Atlas OS` | `FUNCTIONAL_BUT_ENGINEERING_STYLE`, `CARD_OVERLOAD`, `RAW_DATA_LEAK`, `TEXT_HEAVY`, `INCONSISTENT_NAV`, `MIXED_LANGUAGE` | Settings is powerful but very dense: 56 KB HTML and 4,336px page height at 1440px; 6,912px at 1024px. Portfolio JSON and weights JSON are primary controls, which violates the ordinary-user requirement. Several labels remain English in Chinese mode. |
| `/system-guide` | `Atlas OS System Guide` | `TEXT_HEAVY`, `INCONSISTENT_NAV`, `MIXED_LANGUAGE` | System Guide is readable but English-only, standalone, and text-heavy. It still shows `UNKNOWN` as a literal teaching label while the master goal says primary UI should not expose `Unknown`/`UNKNOWN` states. |

## Quantitative Findings

From `browser_visual_audit_1440.json`:

- Home H1 is `NEUTRAL`.
- Dashboard has horizontal overflow at 1440px: `scrollWidth=1713`, `clientWidth=1440`.
- Dashboard has horizontal overflow at 1280px: `scrollWidth=1564`, `clientWidth=1280`.
- Table-first pages:
  - `/portfolio`: 1 table
  - `/markets`: 2 tables
  - `/predictions`: 1 table
  - `/dev-registry`: 2 tables
- Pages with no SVG/canvas visualization at 1440px:
  - `/`
  - `/setup`
  - `/portfolio`
  - `/markets`
  - `/predictions`
  - `/learning`
  - `/workflow`
  - `/roadmap`
  - `/settings`
  - `/system-guide`
- Settings page length:
  - 4,336px scroll height at 1440px
  - 6,912px scroll height at 1024px

From `http_route_audit.json`:

- `/` H1: `NEUTRAL`
- `/dashboard` generated HTML includes repeated `Unknown`, `null`, and `{}` literals.
- `/settings` generated HTML includes `null` and `{}` literals.
- `/predictions` generated HTML includes `null` and exposes a JSON response surface.

## Architecture / Boundary Findings

Current UI server imports runtime state and read-only productization modules:

- `runtime.state_store`
- `runtime.forecast_ledger`
- `runtime.llm.provider_registry`
- `runtime.portfolio_context`
- telemetry readers

The server does not directly import Event Fusion, CIL, LMSE, MPCE, MLE, UMIS, CDE, or Decision
Contract mutation paths during normal page rendering. This is acceptable for UI-layer work.

Risk: `ui/app_server.py` has grown into a large mixed routing, CSS, JS, state, and rendering file.
This increases stale-server and inconsistent-shell risk because each page has its own standalone
HTML/CSS rather than a shared product shell.

## Product Experience Findings

### Global Shell

Status: not implemented as required.

Evidence:

- `/`, `/dashboard`, `/settings`, `/workflow`, `/roadmap`, `/dev-registry`, `/system-guide`,
  `/portfolio`, `/markets`, `/predictions`, and `/learning` each render their own shell or local
  navigation.
- Runtime status/provider/data freshness/language are not globally visible on every page.
- Active route is inconsistent across pages.

### Decision-First Home

Status: failed.

Evidence:

- First viewport H1 is still `NEUTRAL`.
- The first viewport does not lead with a plain-language market change.
- Portfolio relevance, watch triggers, invalidation, freshness, and expert details are not arranged
  as the required product brief.

### Visual Intelligence

Status: partial to failed.

Evidence:

- The dashboard contains some SVG-based explainability views.
- Most primary product pages are table/card/text first.
- Required visualizations missing or incomplete:
  - portfolio exposure map
  - risk cluster graph
  - market regime trajectory
  - attention vs liquidity relationship
  - prediction calibration chart
  - trust evolution timeline
  - hypothesis competition
  - learning evolution flow

### Ordinary-User UX

Status: partial.

Evidence:

- Setup supports form-based provider and asset entry, which is good.
- Settings still exposes Portfolio JSON and Weights JSON as primary controls.
- Markets and Predictions expose runtime/ledger concepts before plain-language explanation.
- Home does not answer the user's first five questions in the required order.

### Bilingual Product Parity

Status: partial.

Evidence:

- `ui/i18n/i18n.py` covers many Home/Setup/Portfolio/Markets/Predictions/Learning/Settings strings.
- Workflow, Roadmap, Dev Registry, and System Guide are mostly hard-coded English.
- Chinese mode still surfaces English technical labels such as Provider, Base URL, Runtime mode,
  Portfolio JSON, Weights JSON, and system-stage copy.

### Responsive Baseline

Status: partial.

Evidence:

- Dashboard overflows horizontally at 1440px and 1280px.
- Dashboard becomes very tall at 1024px.
- Settings becomes very tall at 1024px.
- Other pages avoid horizontal overflow but mostly because they are simple table/text pages.

### Accessibility Baseline

Status: not formally audited yet.

Initial risks:

- Many standalone pages lack consistent landmarks and shared navigation semantics.
- Some visual/status indicators depend on color and text density.
- Charts/visualization alternatives are mostly absent because the visualizations themselves are
  absent.
- Keyboard journey has not yet been executed.

## Required Repair Priority

### P0

1. Build one global app shell shared across primary pages.
2. Replace Home giant `NEUTRAL` hero with decision-first brief.
3. Hide raw `Unknown`, `null`, `{}`, raw JSON, and internal trace surfaces from primary UI.
4. Fix Dashboard horizontal overflow.

### P1

1. Rebuild Portfolio as visual-first exposure/risk cognition.
2. Rebuild Markets as landscape/regime/freshness view, not debug tables.
3. Rebuild Predictions as accountability/calibration experience.
4. Rebuild Learning as belief-change and self-correction story.
5. Expand Workflow to the full system map with live/degraded state and meaningful interaction.
6. Normalize Roadmap and Dev Registry into the same shell with clearer hierarchy.
7. Replace Settings JSON-first asset controls with ordinary forms and progressive advanced mode.

### P2

1. Complete zh/en parity for all primary pages.
2. Add responsive checks at 1440px, 1280px, and 1024px after each major layout change.
3. Add accessibility report with keyboard, focus, contrast, form-label, and chart-summary checks.
4. Add stale UI/build-version guard where safe.

## Baseline Verdict

Current frontend classification:

`FUNCTIONAL_BUT_ENGINEERING_STYLE`

with major sub-findings:

- `WEAK_VISUAL_HIERARCHY`
- `INCONSISTENT_NAV`
- `MISSING_VISUALIZATION`
- `CARD_OVERLOAD`
- `TEXT_HEAVY`
- `RAW_DATA_LEAK`
- `MIXED_LANGUAGE`
- `STALE_SERVER_RISK`

Not classified as globally `BROKEN`, because all required routes render and many runtime/config
paths exist.

Not classified as `PRODUCT_READY`, because the ordinary-user product journey and required visual
intelligence standard are not met.

## Next Step

Proceed to the information architecture and shared app-shell design before changing page colors.

Next required artifact:

`99_Verification/Atlas_OS_Frontend_Information_Architecture_Report.md`
