# ISSUE-2026-011 — Strategic Candidate Evaluation Dashboard Missing

## Status

Accepted

## Origin

Production Trial / User Feedback

## Date First Seen

2026-06-30

## Date Last Seen

2026-06-30

## Frequency

1

## Affected Area

Decision Brief / Research / Candidate Evaluation / Portfolio / UX

## Problem

Atlas Decision Brief correctly prioritizes immediate trading action, portfolio impact, and CDE
authority. However, when the user asks about industry-chain opportunities, candidate stocks,
supplier overlap, strategic beneficiaries, rankings, or watchlists, Atlas lacks a dedicated
candidate evaluation and ranking output.

As a result, Atlas can answer whether to trade today, whether to hold current positions, and
whether CDE allows deployment, but it does not clearly answer which candidate names deserve deeper
research, which names are S/A/B/C tier, which are already priced in, which have capital market
confirmation, which are only theme-driven, or which should enter Watchlist / Research Pool.

## Context

This issue appeared during Production Trial after the user asked how to view short-term,
medium-term, and long-term candidate pools and how Atlas should evaluate current and new candidate
opportunities.

## Impact

Medium

## Evidence

User feedback during Production Trial indicated that candidate pools exist across `AI_Shovel_100.md`,
`Second_Growth_Curve.md`, and local portfolio candidates, but there is no unified optional output
module for candidate evaluation.

## Root Cause Hypothesis

Decision Brief is optimized for trading discipline and current portfolio impact. Candidate
evaluation needs a separate optional output layer so research priority is not confused with trading
authority.

## Possible Solutions

- Add a lightweight optional Strategic Candidate Dashboard to Decision Brief.
- Keep current holdings and new candidates separated.
- Add research-priority scoring while preserving CDE authority as the only deployment permission.

## Priority

P2

## Decision

Convert to Improvement Proposal

## Linked IP

IP-2026-011

## Notes

This issue does not request a new Engine, research redesign, software dashboard, crawler, API, or
automation. It requests a lightweight optional output module.
