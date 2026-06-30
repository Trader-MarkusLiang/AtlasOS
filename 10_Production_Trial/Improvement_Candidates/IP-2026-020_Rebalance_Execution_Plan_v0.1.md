# IP-2026-020 — Rebalance Execution Plan v0.1

## Category

Portfolio / Execution Support / CDE Support / Domestic Market Data Integration

## Origin

ISSUE-2026-020 — Rebalance Execution Plan Missing

## Problem

Atlas can produce Portfolio Context, Domestic Market Snapshot, Strategic Candidate Dashboard, and
CDE boundary language, but it lacks a structured output layer for rebalance, switching, migration,
and cash redeployment questions.

## Root Cause

The system had data and rules, but not a standardized way to combine them into staged execution
guidance that preserves CDE authority, anomaly checks, and user confirmation.

## Expected Improvement

Create a lightweight Rebalance Execution Plan v0.1 that converts:

- Current Portfolio Context.
- Domestic Market Snapshot.
- Strategic Candidate Dashboard.
- CDE boundary.
- User rebalance intent.

into a staged, explainable, non-automatic execution plan.

## Affected Modules

- `tools/market_data/data_anomaly_check.py`
- `06_Portfolio/Rebalance_Execution_Plan_v0.1.md`
- `AGENTS.md`
- `.agents/skills/atlas-portfolio/SKILL.md`
- `.agents/skills/atlas-daily/SKILL.md`
- `.agents/skills/atlas-research/SKILL.md`
- `99_Verification/Rebalance_Execution_Plan_Test_Result.md`
- `99_Verification/Audit_Report_Rebalance_Execution_Plan_v0.1.md`
- `99_Verification/Regression_Tests.md`

## Priority

P1

## Status

Implemented

## Compatibility

This IP adds an optional output layer and data anomaly check only. It does not create a new Engine,
modify CDE formulas, modify Decision Brief strategy logic, modify portfolio allocation, execute
trades, or store private amounts.
