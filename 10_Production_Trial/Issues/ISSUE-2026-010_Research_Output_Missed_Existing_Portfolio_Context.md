# ISSUE-2026-010 — Research Output Missed Existing Portfolio Context

## Status

Accepted / Converted to IP

## Origin

Production Trial / User Feedback

## Date First Seen

2026-06-29

## Date Last Seen

2026-06-29

## Frequency

1

## Affected Area

Research

Portfolio

Capital Deployment

Decision Brief

UX

## Problem

Atlas Research output missed existing Portfolio Context.

When the user provided MLCC industry and supply-chain information, Atlas generated a valid research
brief but did not first map the signal to the user's current accounts, holdings, cash / Dry Powder,
existing thesis exposure, and CDE authority.

## Context

The user explicitly identified two defects:

1. The response did not include current portfolio context when discussing operation suggestions.
2. The response did not make clear whether Atlas had used the crystallized Atlas reasoning chain
   and framework.

## Impact

High

## Evidence

Production Trial interaction involving an MLCC X opinion about Rubin, Murata, Samsung, Yageo, and
MLCC price hikes.

The initial output focused on MLCC research candidates and did not sufficiently map:

- Current China Account deployment / cash.
- Current holdings.
- Holding-by-holding exposure.
- CDE authority impact.
- Whether a new MLCC position was permitted.

## Root Cause Hypothesis

Atlas Research can process thematic information correctly, but final output did not require
Portfolio Context Injection before Research / Decision Brief generation.

Research and Portfolio layers were sequenced too loosely in the presentation layer.

## Possible Solutions

- Add Portfolio Context Injection Rule before market, industry, company, supply-chain, pricing, or
  thematic investment outputs.
- Update AGENTS and relevant skills.
- Add compact Existing Portfolio Mapping block to Decision Brief.
- Add regression test for MLCC X opinion.

## Priority

P1

Reason:

This issue can affect portfolio interpretation, CDE authority, and trading decision quality.

## Decision

Convert to Improvement Proposal.

## Linked IP

IP-2026-010

## Notes

This is an operational Production Trial fix.

It does not add a new Engine.

It does not implement IDA.

It does not redesign Research.
