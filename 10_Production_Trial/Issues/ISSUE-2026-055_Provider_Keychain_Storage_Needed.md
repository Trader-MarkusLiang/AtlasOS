# ISSUE-2026-055 — Provider Keychain Storage Needed

Date: 2026-07-08
Status: Accepted / Partially Implemented
Category: Engineering

## Source

Security review during overnight productization sprint.

## Problem

`runtime/llm/provider_registry.py` stores provider keys through local application-side protection
beside runtime configuration. This is useful for local development but should not be described as
production-grade secret storage.

## Constraints

- Do not commit API keys or local runtime config.
- Do not expose raw secrets in UI, logs, telemetry, or `/state`.
- Preserve existing local fallback compatibility until Keychain migration is implemented.

## Impact

Medium.

## Evidence

The provider registry supports masked UI views and local key storage, but the sprint audit found it
is not macOS Keychain-backed.

## Root Cause Hypothesis

The provider runtime was built quickly as a local adapter and optimized for no-secret UI exposure,
not OS-native secret storage.

## Possible Solutions

- Add macOS Keychain-backed storage via the system `security` command.
- Keep current local storage as explicit fallback named `local_secret_storage`.
- Add a migration path that does not display or log existing keys.

## Priority

P1

## Decision

Implemented Keychain-first storage path for newly saved keys, with local fallback explicitly marked
as `local_secret_storage`. Validation covers fallback using a fake key and confirms safe UI views do
not expose secrets. A real macOS Keychain smoke test with an actual provider key remains required
before closing this Issue.

## Linked IP

None

## Notes

Validation:

- `PYTHONDONTWRITEBYTECODE=1 python3 99_Verification/validate_provider_secret_storage.py` — PASS.
- `PYTHONDONTWRITEBYTECODE=1 python3 99_Verification/validate_llm_provider_ui_i18n_v1_4.py` — PASS.
