# ISSUE-2026-049 — UI Cognitive Onboarding Needed

Date: 2026-07-06
Status: Accepted for implementation
Category: User Experience

## Source

User request: Atlas OS UI v1.2 Cognitive Onboarding & Navigation Layer.

## Problem

The Atlas runtime UI exposes system state and development registry pages, but a new user may not
immediately understand:

- what Atlas OS is,
- what the runtime state means,
- where to click,
- how to find roadmap and registry pages,
- what `UNKNOWN` and `NEUTRAL` mean.

## Constraints

- Do not modify runtime / cognition / decision logic.
- Do not modify event processing.
- Do not modify trust / causal / hypothesis engines.
- Do not change backend execution semantics.
- Limit implementation to UI, frontend guidance, onboarding, and navigation hints.

## Acceptance Criteria

- First load shows onboarding modal.
- Roadmap is discoverable within one click.
- Dev Registry is visible in navigation.
- System Guide page explains state meanings and decision flow.
- Empty `UNKNOWN` state is explained in user-facing language.
- Boundary scan confirms no backend or cognitive layer changes.

## Linked Improvement Candidate

IP-2026-049 — UI Cognitive Onboarding v1.2
