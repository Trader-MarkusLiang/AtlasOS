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

Return:

1. Date.
2. Trade Today: YES / NO.
3. One-sentence conclusion.
4. AI Bottleneck Index changes.
5. Capital Relay read.
6. Today's Actions using Atlas vocabulary.
7. Risk Level.
8. Waiting Triggers.
9. Unknown / Unverified items.

## forbidden_actions

- Do not add new frameworks.
- Do not edit databases unless the user explicitly asks.
- Do not commit.
- Do not expose or commit real private holdings.
- Do not turn an unconfirmed signal into an action.
