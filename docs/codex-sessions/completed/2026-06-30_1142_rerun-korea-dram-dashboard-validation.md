# Rerun Korea DRAM Dashboard Validation Session

## Metadata

- Date: 2026-06-30
- Session id: 2026-06-30_1142_rerun-korea-dram-dashboard-validation
- Project: Atlas OS
- Workspace: `/Users/markus/AtlasOS`
- Task: Reprocess Korea AI / DRAM investment and A-share candidate screenshot with current Atlas OS.
- Status: completed
- Branch: main

## User Request Summary

The user asked to rerun the prior Korea AI / DRAM investment plus A-share candidate screenshot using
the latest Atlas OS rules, explicitly checking Portfolio Source, Portfolio Last Updated, Exposure
Sum, Portfolio Consistency, Decision Limited behavior, candidate code/name validation, correct
identification of `688008 澜起科技`, Strategic Candidate Dashboard fields, Top 3 score explanations,
and Research Priority versus Trading Authority separation.

## Constraints

- Do not update repository databases or private portfolio.
- Do not invent K-line, valuation, order, or market confirmation data.
- Treat screenshot candidates as needing validation unless separately verified.

## Work Done

- Read latest atlas-research, atlas-portfolio, atlas-daily, AGENTS, Decision Brief Template, and
  local portfolio file.
- Ran YAML-based portfolio sum validation:
  - Tiger exposure 70% + cash 30% = 100%, PASS.
  - China exposure 84% + cash 16% = 100%, PASS.
- Browsed for current Korea AI / DRAM investment verification.

## Decisions

- No trade action.
- No precise CDE authority because user asked for validation and candidate dashboard rather than
  deployment; account is already highly deployed and no direct evidence authorizes deployment.
- Candidate identities from screenshot will be marked Needs Validation unless code/name can be
  independently verified.
- `688008 澜起科技` must be used; `润起科技` must not be treated as valid.

## Current State

- Final Decision Brief and Strategic Candidate Dashboard were delivered.
- Session completed and moved from active to completed on 2026-06-30.

## Resume Instructions

1. Keep Research Priority separate from Trading Authority.
2. Keep K-line, valuation, order, and market confirmation as Data Missing / Needs Verification
   unless sourced.
3. Do not commit unless user requests repository update.

## Open Questions

- None.
