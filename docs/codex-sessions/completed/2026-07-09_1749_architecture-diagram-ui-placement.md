# Codex Session — Architecture Diagram UI Placement

## Metadata

- Date: 2026-07-09 17:49 CST
- Session id: codex-desktop-2026-07-09-1749
- Project: Atlas OS
- Workspace: `/Users/markus/AtlasOS`
- Task: Review newly added Atlas OS architecture diagrams and place them in the frontend
- Status: completed
- Branch: `codex/frontend-master-upgrade`

## User Request Summary

User added two newly generated Atlas OS architecture diagrams to the project directory, one Chinese
and one English, and asked Codex to review them and place them in the frontend where appropriate.

## Work Done

- Reviewed the new diagram assets:
  - `docs/assets/atlas-os-architecture-cn-20260709.png`
  - `docs/assets/atlas-os-architecture-20260709.png`
- Added a safe UI static asset route for files under `docs/assets`.
- Added a full architecture-map section to the Workflow page.
- Added a Roadmap page entry that links to the Workflow architecture section and the full-size map.
- Added EN/CN copy for the architecture map section.
- Added responsive styling so the large diagram is scrollable and can be opened full-size without
  disrupting the Decision Brief-first Home layout.
- Follow-up polish:
  - Reordered Workflow so the full architecture diagram appears before the compact Global System
    Map.
  - Reframed Workflow as Architecture Overview first, Active Runtime Path second.
  - Added jump links from the Workflow hero to the architecture map and active path sections.
  - Added a stronger visual hierarchy for the architecture card while keeping Home untouched.

## Verification

- `python3 -m py_compile ui/app_server.py ui/pages/product_views.py ui/design/tokens.py ui/i18n/i18n.py`
- `GET /assets/atlas-os-architecture-20260709.png` returned `200 image/png`.
- `GET /assets/atlas-os-architecture-cn-20260709.png` returned `200 image/png`.
- Browser verification on `http://127.0.0.1:8765/workflow` confirmed:
  - architecture card exists
  - image loads completely
  - displayed image uses the current UI language
  - image natural size is `1536x1024`
- Browser verification on `http://127.0.0.1:8765/roadmap` confirmed:
  - Roadmap architecture entry exists
  - links point to `/workflow#architecture-map` and the localized full-size asset.
- Follow-up verification:
  - `python3 -m py_compile ui/pages/product_views.py ui/design/tokens.py ui/i18n/i18n.py ui/app_server.py`
  - Workflow HTML order assertion passed:
    `workflow-hero-panel -> architecture-map -> global-system-map -> workflow-node-detail`
  - `GET /assets/atlas-os-architecture-cn-20260709.png` returned `200 image/png`.

## Decisions

- Place the full diagram in Workflow because it explains system architecture and execution flow.
- Add only a lightweight Roadmap entry because Roadmap should remain lifecycle/maturity-focused.
- Do not add the diagram to Home, preserving Home as the Decision Brief-first surface.
- Do not modify runtime, cognition, Decision Contract, or market-processing behavior.

## Current State

- The UI server was restarted via the existing local LaunchAgent on port `8765`.
- Workflow and Roadmap now expose the architecture diagrams.
- The new image assets remain uncommitted at the time of this log unless a later Git task commits
  them.

## Resume Instructions

1. Inspect `ui/pages/product_views.py`, `ui/design/tokens.py`, `ui/i18n/i18n.py`, and
   `ui/app_server.py`.
2. Visit `http://127.0.0.1:8765/workflow` and scroll to the architecture section.
3. Visit `http://127.0.0.1:8765/roadmap` and check the architecture entry.
4. If committing later, include both `docs/assets/atlas-os-architecture-*.png` files.

## Open Questions

- None.
