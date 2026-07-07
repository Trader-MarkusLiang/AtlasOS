# Atlas OS LLM Provider Red-Team Report

Date: 2026-07-08

## Executable Evidence

Command:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 99_Verification/validate_morning_red_team.py
```

Provider failure injection results:

- Active provider HTTP 500 -> fallback.
- Empty provider response -> fixed and fallback.
- Malformed JSON -> fallback.
- Missing OpenAI-compatible key -> fallback.
- Safe registry view hides encrypted/keychain secret fields.

Observed fallback chain:

```text
bad500 -> empty -> malformed -> good
```

Final provider: `good`.

## Repairs

- `runtime/llm/provider_router.py` now rejects empty provider content with `empty_response`.
- Validation fake keys no longer use real-looking `sk-` prefixes.

## Residual Risks

- Real providers with 401/403/429/timeout were not all live-tested with external services.
- Real macOS Keychain save needs one user-approved local provider save smoke.
