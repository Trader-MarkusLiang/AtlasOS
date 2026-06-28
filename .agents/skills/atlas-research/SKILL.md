---
name: atlas-research
description: Use for Atlas OS industry information, company research, signal judgment, seven-layer reasoning, evidence classification, and Living Database update suggestions. Do not use for Git-only maintenance or direct trade execution.
---

# Atlas Research

## when_to_use

Use this skill when the task involves:

- Industry, company, supply-chain, earnings, order, pricing, or policy information.
- Deciding whether a user-provided item is a real Atlas Signal.
- Running `Fact -> Physics -> Engineering -> Economics -> Finance -> Capital -> Trading`.
- Suggesting updates to Living Database, Alpha Radar, Risk Radar, Order Book, or Price Transmission.

## required_reads

- `00_Core/Atlas_Principles.md`
- `00_Core/Seven_Layer_Reasoning.md`
- `00_Core/Trading_Discipline.md`
- `02_Databases/AI_Shovel_100.md`
- `02_Databases/Alpha_Radar.md`
- `02_Databases/Risk_Radar.md`
- `02_Databases/Order_Book.md`
- `02_Databases/Price_Transmission.md`
- `04_Current_State/Bottleneck_Map_v1.md`
- `04_Current_State/AI_Capital_Map_v1.md`

## output_format

Return:

1. Signal classification: Fact / Signal / Evidence / Risk / Price Action / Noise.
2. Seven-layer reasoning table.
3. Affected bottleneck and current Atlas rank.
4. Evidence quality: Low / Medium / High.
5. Counter argument.
6. Required confirmation.
7. Atlas action: Research / Observe only unless a separate portfolio workflow is requested.
8. Suggested database update, if any, with target file and fields.

## forbidden_actions

- Do not directly execute trades.
- Do not use Buy / Sell language.
- Do not commit changes unless the user explicitly asks for repository work.
- Do not invent evidence; write `Unknown` or `Unverified`.
- Do not promote a signal to action without trigger and counter argument.
