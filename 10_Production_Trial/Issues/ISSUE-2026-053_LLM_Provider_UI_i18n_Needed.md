# ISSUE-2026-053 — LLM Provider Runtime and UI i18n Needed

Date: 2026-07-06
Status: Accepted for implementation
Category: User Experience

## Source

User requested Atlas OS v1.4: real multi-provider LLM runtime configuration, Apple/OpenAI-grade UI
control surface refinement, and EN/CN internationalization.

## Problem

Atlas UI has a clean control-center shell, but provider configuration is still single-provider and
the runtime router does not yet use a configurable provider registry with fallback. The UI also
needs a persistent EN/CN language toggle and reduced debug-style clutter.

## Constraints

- UI / configuration / LLM adapter only.
- Do not modify Event Fusion.
- Do not modify CIL, LMSE, MPCE, MLE, Decision Contract semantics, or runtime cognition algorithms.
- Do not introduce trading execution, prediction logic, ML, DL, or RL.
- Do not commit real API keys or local runtime config.

## Acceptance Criteria

- LLM providers can be configured as multiple entries.
- Runtime routing can use the configured provider registry and fallback chain.
- API keys are stored only in local ignored config and are not exposed in UI/API output.
- Settings page supports add/remove provider, key input, base URL, model, fallback chain, and test
  connection.
- Dashboard remains a single-focus cognitive control surface.
- EN/CN language toggle persists in local UI config.
- No cognitive core files are modified.

## Linked Improvement Candidate

IP-2026-053 — LLM Provider Runtime + UI i18n v1.4
