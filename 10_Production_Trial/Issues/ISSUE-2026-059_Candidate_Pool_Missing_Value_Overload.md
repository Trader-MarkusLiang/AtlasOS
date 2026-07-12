# ISSUE-2026-059 — Candidate Pool Missing-Value Overload

## Status

Resolved

## Date First Seen

2026-07-13

## Affected Area

Decision Brief / UX / Market Evidence

## Problem

Home truthfully marks unsupported candidate market confirmation, numeric score, and CDE authority as
missing, but repeats those missing values across every candidate row. The repetition makes the whole
Home surface appear data-empty even when portfolio quotes, official evidence, and runtime inference
are available. Portfolio quote fallback also lacks multi-day history, so real holdings show missing
5/20/60-day changes.

## Decision

- Add a bounded Tencent daily-history fallback to the existing market-data provider.
- Keep candidate research priority separate from market confirmation and CDE authority.
- Show supported candidate fields by default and collapse candidates that still need identity/data
  validation.
- Summarize unsupported capabilities once instead of repeating `Data Missing` in every cell.

## Guardrails

- Do not invent valuation, market confirmation, numeric candidate scores, or CDE authority.
- Do not fetch data from the UI rendering path.
- Do not change cognition, Decision Contract, or trading semantics.

## Resolution Evidence

- Tencent daily-history fallback returned usable 5/20/60-day changes for all three configured
  holdings through the normal market-intelligence path.
- Home now shows two validated candidates first; six candidates needing identity or market-data
  verification remain collapsed by default.
- Unsupported numeric candidate scores and CDE authority are summarized once instead of repeated
  in every candidate row.
- Chinese desktop and 390px mobile browser checks found zero `Data Missing` / `数据缺失` labels,
  no horizontal overflow, and no fabricated candidate values.
- Investor Home, Goal 03, Home intelligence, and zh/en localization validators pass when run
  serially. These validators change a shared UI language setting and must not run concurrently.
