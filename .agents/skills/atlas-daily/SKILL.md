---
name: atlas-daily
description: Use for generating the Atlas Daily Report, daily dashboard, daily signal triage, daily risk review, and watch-trigger summary. Do not use for framework creation, database edits, or commits.
---

# Atlas Daily

## when_to_use

Use this skill when the user asks for:

- Daily Atlas report.
- Daily dashboard.
- Daily market or signal triage.
- Daily risk, waiting triggers, or watchlist summary.
- A concise answer to whether today's information changes Atlas action.

## required_reads

- `03_Trading_OS/Daily_Dashboard_Template.md`
- `00_Core/Seven_Layer_Reasoning.md`
- `00_Core/Trading_Discipline.md`
- `04_Current_State/Bottleneck_Map_v1.md`
- `04_Current_State/AI_Capital_Map_v1.md`
- `04_Current_State/Current_Holdings_Strategy.md`
- `02_Databases/Alpha_Radar.md`
- `02_Databases/Risk_Radar.md`
- `06_Portfolio/Portfolio_Rules.md`

## output_format

Default output is Decision Brief.

Return by default:

1. Date.
2. Trade Today: YES / NO.
3. One-sentence conclusion.
4. Today's Action using Atlas vocabulary.
5. Portfolio Impact.
6. Risk Changes.
7. Waiting Triggers.
8. Today's Learning.

Hide Research View, Knowledge View, and Repository View unless the user asks for them.

Research View may include evidence, Seven Layer Reasoning, counter argument, and signal assessment.

Knowledge View may include pattern, confidence, case, theory candidate, and knowledge proposal.

Repository View may include sync, repository, Git, commit, tag, audit, database, and merge details.

## forbidden_actions

- Do not add new frameworks.
- Do not edit databases unless the user explicitly asks.
- Do not commit.
- Do not expose or commit real private holdings.
- Do not turn an unconfirmed signal into an action.
