# ISSUE-2026-012 — Portfolio Context Source Inconsistency

## Status

Accepted

## Origin

Production Trial / Strategic Candidate Dashboard Test

## Date First Seen

2026-06-30

## Date Last Seen

2026-06-30

## Frequency

1

## Affected Area

Decision Brief / Portfolio / CDE / Strategic Candidate Dashboard / UX

## Problem

Atlas output showed portfolio context such as China Deployment and Cash / Dry Powder values, but the
current portfolio context may have been different or stale. This creates a serious risk because CDE
authority, deployment status, and portfolio action depend on accurate portfolio data.

## Context

The defect appeared during a Korea AI / DRAM candidate dashboard test. Atlas used local portfolio
context values without explicitly showing source, last update, consistency state, exposure sum, or
decision limitation.

## Impact

High

## Evidence

Production Trial output did not provide enough freshness metadata for the portfolio source used in
the Decision Brief and Strategic Candidate Dashboard.

## Root Cause Hypothesis

Portfolio Context Injection exists, but it does not yet require source freshness disclosure and
sum validation in every Decision Brief / Strategic Candidate Dashboard.

## Possible Solutions

- Require Portfolio Source.
- Require Portfolio Last Updated.
- Require Portfolio Consistency.
- Require Exposure Sum and Cash / Dry Powder.
- Require Decision Limitation when context is missing, stale, inconsistent, or conflicting.

## Priority

P1

## Decision

Accepted

## Linked IP

None

## Notes

This is a lightweight Production Trial fix. It does not add a new Engine or modify private
portfolio data.
