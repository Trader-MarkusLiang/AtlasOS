# Atlas Codex Routing v0.6 Alpha Session

## Metadata

- Date: 2026-06-29 00:56 AEST
- Session id: 019f0e3e-atlas-routing-v06
- Project: Atlas OS
- Workspace: `/Users/markus/AtlasOS`
- Task: Establish project-level Codex routing with `AGENTS.md` and repo-scoped Atlas skills.
- Status: completed
- Branch if relevant: main

## User Request Summary

The user asked Codex to create a project-level routing system for Atlas OS so new conversations can
inherit Atlas core rules and choose appropriate workflows by task type. Required outputs include a
root `AGENTS.md`, five repo-scoped skills, README/CHANGELOG/VERSION updates, an audit report,
commit, and tag `v0.6-alpha`.

## Work Done

- Read `skill-creator` guidance for creating skills.
- Inspected current Git state, `VERSION.md`, `CHANGELOG.md`, `README.md`,
  `99_Verification/Audit_Methodology.md`, and `99_Verification/Release_Gate.md`.
- Confirmed current branch is `main`.
- Noted existing untracked completed session logs from earlier task-bearing turns; they should be
  included so project indexes do not reference missing Git artifacts.
- Added root `AGENTS.md` with Atlas hard rules and routing rules.
- Added five repo-scoped skills under `.agents/skills/`.
- Updated `README.md`, `VERSION.md`, and `CHANGELOG.md` for v0.6 Alpha.
- Added `99_Verification/Audit_Report_v0.6_Alpha.md`.
- Verified `AGENTS.md` is under 200 lines.
- Verified each `SKILL.md` has `name`, `description`, `when_to_use`, `required_reads`,
  `output_format`, and `forbidden_actions`.
- Verified `portfolio.local.yaml` and `06_Portfolio/portfolio.local.yaml` remain ignored.
- Committed changes with message `Add Atlas Codex project routing and skills`.
- Tagged the release as `v0.6-alpha`.

## Decisions

- Use official Codex project instruction mechanism: root `AGENTS.md`.
- Use repo-scoped skills under `.agents/skills/` for Atlas workflows.
- Do not add custom agents, hooks, bootstrap scripts, dashboards, crawlers, APIs, or automation.
- Keep `AGENTS.md` concise and route detailed behavior to skills and existing Atlas files.

## Current State

- Completed: Atlas Codex project routing and skills are implemented.
- Completed: release commit and tag were created.

## Resume Instructions

1. Read this session log.
2. Check `git status --short`.
3. Verify commit `Add Atlas Codex project routing and skills`.
4. Verify tag `v0.6-alpha`.

## Open Questions

- None.
