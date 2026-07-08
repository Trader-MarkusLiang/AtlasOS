# Atlas OS Frontend Information Architecture Report

Date: 2026-07-08

Branch: `codex/frontend-master-upgrade`

Commit baseline: `3f8d6e7 frontend: audit current product experience`

## Scope

This report documents the IA repair after the frontend baseline. The work is UI-only and keeps
runtime/cognition boundaries intact.

## New Product Shell

Implemented shared product shell components:

- `ui/components/app_shell.py`
- `ui/components/global_sidebar.py`
- `ui/components/global_topbar.py`
- `ui/components/runtime_status_indicator.py`
- `ui/components/language_toggle.py`
- `ui/components/context_inspector.py`
- `ui/design/tokens.py`

## Global Navigation

Primary:

- Home
- Ask Atlas
- Portfolio
- Markets
- Predictions
- Learning
- Workflow
- Roadmap

Secondary:

- Dev Registry
- Settings
- Setup
- System Guide

## Route Mapping

All HTML routes now render through the shared shell:

- `/`
- `/home`
- `/dashboard`
- `/chat`
- `/portfolio`
- `/markets`
- `/predictions`
- `/learning`
- `/workflow`
- `/roadmap`
- `/dev-registry`
- `/settings`
- `/setup`
- `/system-guide`
- `/replay`
- `/control`

JSON routes remain JSON-only:

- `/state`
- `/roadmap?format=json`
- `/roadmap.json`
- `/markets?format=json`
- `/predictions?format=json`

## Boundary Check

`rg` found no direct `runtime.cognition` imports under `ui/`.

The UI continues to consume runtime state, portfolio context, market state, forecast ledger, LLM
provider registry, and telemetry readers as read-only product surfaces.

## IA Result

Result: `PASS`

Primary pages now share one app shell, sidebar, topbar, language toggle, runtime status, provider
status, freshness indicator, and contextual inspector.

Remaining risk: `ui/app_server.py` is still large and should eventually be split further, but the
route-level shell inconsistency is closed.
