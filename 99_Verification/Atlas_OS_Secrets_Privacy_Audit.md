# Atlas OS Secrets Privacy Audit

Date: 2026-07-08

## Scope

- Git tracked files.
- Runtime config/log/state paths by metadata only.
- Provider safe-view behavior.

## Evidence

- Runtime private paths are gitignored:
  - `runtime/config/user_config.json`
  - `runtime/config/user_config.json.backup-before-ccswitch-sync-20260707_0904`
  - `runtime/state/atlas_runtime.sqlite`
  - `runtime/logs/*.jsonl`
  - `runtime/inbox/user_event.jsonl`
- `validate_morning_red_team.py` secret scan found no tracked `sk-[A-Za-z0-9_-]{8,}` matches.
- `validate_provider_secret_storage.py` PASS.
- `validate_llm_provider_ui_i18n_v1_4.py` PASS.

## Findings

- No critical tracked API-key leak found.
- Provider registry is Keychain-first for new saves and local fallback is explicitly labeled
  `local_secret_storage`.
- Real Keychain save is not proven until a live local save test is run.
- Portfolio context uses percentages only and redacts account value / net worth / balance / cost
  fields in runtime state.

## Verdict

PASS_WITH_RESIDUAL_RISK.
