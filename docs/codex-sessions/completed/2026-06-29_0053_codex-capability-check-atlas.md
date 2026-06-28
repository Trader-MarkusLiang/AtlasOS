# Codex Capability Check For Atlas Session

## Metadata

- Date: 2026-06-29 00:53 AEST
- Session id: 019f0e3d-capability-check-atlas
- Project: Atlas OS
- Workspace: `/Users/markus/AtlasOS`
- Task: Check current Codex App project-instruction, routing, memory, role-loading, and project-organization capabilities for Atlas OS.
- Status: completed
- Branch if relevant: main

## User Request Summary

The user asked for a capability check based on current Codex App behavior and official Codex
documentation, without guessing future or undocumented features. The requested areas were project
instructions, conversation routing, project memory, role loading, recommended Atlas architecture,
and a support matrix.

## Work Done

- Used the `openai-docs` skill because the request asks about Codex product capabilities.
- Fetched the current Codex manual with
  `/Users/markus/.codex/skills/.system/openai-docs/scripts/fetch-codex-manual.mjs`.
- Read relevant manual sections:
  - Custom instructions with `AGENTS.md`
  - Customization
  - Config basics
  - Project config files
  - Project documentation controls
  - Agent Skills
  - Memories
  - Codex app features
  - Subagents
- Checked the Atlas workspace for existing project instruction/config files; no root `AGENTS.md`,
  `.codex/config.toml`, `CLAUDE.md`, `PROJECT.md`, or `instructions.md` was found at the checked
  depth.

## Decisions

- Treat official `AGENTS.md` discovery as the primary project-level instruction mechanism.
- Treat Skills as the best mechanism for reusable Atlas workflows and role-like procedures.
- Treat Memories as optional local recall, not authoritative project memory.
- Treat custom subagents as explicit parallel-worker roles, not automatic routing for normal user
  prompts.
- Mark unsupported or undocumented terms as `Unknown` rather than inferring behavior.

## Current State

- Atlas OS currently relies on conversation-level instructions and repository markdown files.
- Atlas should add a compact root `AGENTS.md` and repo-scoped `.agents/skills` if the user wants
  future conversations to require minimal prompting.

## Verification Results

- Official Codex manual was fetched fresh during this session.
- The answer should cite official Codex manual source pages rather than memory or assumptions.
- No Atlas framework files were changed.

## Resume Instructions

1. Read this session log.
2. If implementing the recommendation, create a concise `/Users/markus/AtlasOS/AGENTS.md`.
3. Then create focused repo skills under `/Users/markus/AtlasOS/.agents/skills/` for Research,
   Repository, Portfolio, Daily, and Architecture workflows.

## Open Questions

- Whether the user wants Codex to implement the recommended `AGENTS.md` and Atlas skills now.
