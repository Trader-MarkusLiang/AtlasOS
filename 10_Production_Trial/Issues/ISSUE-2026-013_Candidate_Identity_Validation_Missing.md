# ISSUE-2026-013 — Candidate Identity Validation Missing

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

Research / Candidate Evaluation / Strategic Candidate Dashboard / UX

## Problem

In the Korea AI / DRAM candidate dashboard test, Atlas output included `润起科技`, but the input image
showed `688008 澜起科技`. This indicates candidate identity validation is missing.

## Context

Candidates extracted from images, screenshots, OCR, social media posts, or unstructured text can be
misread. If the code and Chinese name do not match, Atlas may pollute the research pool and produce
incorrect follow-up analysis.

## Impact

Medium

## Evidence

Screenshot source contained code `688008` and candidate `澜起科技`; output used a different candidate
name.

## Root Cause Hypothesis

Strategic Candidate Dashboard requires candidate scoring, but it does not yet require identity
validation fields before scoring screenshot/OCR candidates.

## Possible Solutions

- Require Code.
- Require Candidate.
- Require Identity Status.
- Require Source Category.
- If code and name mismatch, output `Candidate Identity Mismatch — Needs Validation`.
- Do not score mismatched candidates normally.

## Priority

P2

## Decision

Accepted

## Linked IP

None

## Notes

This is a lightweight Production Trial fix. It does not implement OCR, IDA, or a new identity
engine; it adds output discipline and validation status.
