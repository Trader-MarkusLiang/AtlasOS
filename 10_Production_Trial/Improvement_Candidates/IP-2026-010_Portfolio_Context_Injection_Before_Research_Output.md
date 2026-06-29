# IP-2026-010 — Portfolio Context Injection Before Research Output

## Category

Portfolio / Research / Capital Deployment

## Origin

ISSUE-2026-010 — Research Output Missed Existing Portfolio Context

## Problem

When user provides industry or thematic information, Atlas may generate a valid research brief but
fail to map the information to the user's existing portfolio first.

## Root Cause

The output sequence allowed Research to present thematic conclusions before injecting current
account context, holdings, cash / Dry Powder, existing thesis exposure, and CDE authority.

## Expected Improvement

Before any Research / Decision Brief output, Atlas must inject current Portfolio Context.

The user should immediately see:

- Current account context.
- Current holdings.
- Current cash / Dry Powder.
- Existing thesis exposure.
- Direct / indirect / no exposure mapping.
- CDE authority impact.

## Affected Modules

- `AGENTS.md`
- `.agents/skills/atlas-research/SKILL.md`
- `.agents/skills/atlas-portfolio/SKILL.md`
- `.agents/skills/atlas-daily/SKILL.md`
- `08_Daily_Operating_Cycle/Decision_Brief_Template.md`
- `99_Verification/Regression_Tests.md`

## Priority

P1

## Status

Accepted

## Acceptance Test

Input:

MLCC X opinion about Rubin, Murata, Samsung, Yageo, and MLCC price hikes.

Expected output must include:

1. Current Portfolio Context.
2. Existing Portfolio Mapping.
3. China Account deployment / cash.
4. Holding-by-holding impact:
   - 泰金新能
   - 德福科技
   - 东山精密
   - Cash
5. CDE authority result.
6. No new MLCC position unless direct evidence exists.
7. Research candidates separated from current holdings.
8. No immediate Accumulate.

Fail condition:

If Atlas outputs only MLCC research candidates and does not map existing holdings, test FAIL.

## Implementation Boundary

No new Engine.

No IDA.

No Research redesign.

No private portfolio data commit.
