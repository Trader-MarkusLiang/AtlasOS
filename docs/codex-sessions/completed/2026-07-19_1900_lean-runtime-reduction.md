# 2026-07-19 Lean Runtime Reduction (ISSUE-2026-063)

## Scope

Executed the approved lean-runtime reduction plan (v2, rebased onto the GPT-side real-time brief
closure repair, committed separately as `1a2eb7b`).

## Changes

1. **Lean cognition mode** (`runtime/decision_loop.py`, `runtime/atlas_runtime_daemon.py`,
   `runtime/cognition/__init__.py`, `ui/pages/settings.py`):
   - `DecisionLoopConfig.cognition_mode` (`lean` default / `full` legacy). Lean keeps fusion,
     state controller, regime memory, LLM decision (via `run_state_runtime`), atomic Brief
     publication, and forecast ledger; it skips the symbolic chain (CIL, world model, LMSE, MPCE,
     MLE, UMIC, LLM feedback, structural co-evolution, self-organization).
   - `AtlasRuntimeDaemonConfig.cognition_mode` (`auto` default) with resolution:
     CLI `--cognition-mode` > `system.cognition_mode` in user config > `lean`.
   - Full mode behavior byte-identical (only `if events:` -> `elif events:` after the lean branch).
2. **Market data resilience** (`tools/market_data/market_data_provider.py`):
   - Persistent JSON cache `runtime/state/market_cache.json` (atomic write, 500-entry cap,
     successes only), `set_persistent_cache_path()` override.
   - Stale fallback labeled `data_freshness: CACHED` + `stale_age_seconds` + `cache_source:
     persistent`; ~2-day cutoff then original failure behavior.
   - Rate-limit backoff 60s -> 300s -> 900s per provider with cross-provider failover; in-memory.
3. **Entry consolidation**: `deployment/atlas_os.plist` now launches
   `python3 -m runtime.atlas_runtime_daemon` (args mirror the live daemon). Deprecated in place
   (kept for validator imports): `runtime/atlas_daemon.py`, `runtime/atlas_host.py`, `web/app.py`,
   `web/dashboard_observability.py`. Deviation from plan: no physical move to `runtime/legacy/`
   because four validation scripts import these modules.
4. **Cleanup**: removed `prompt_d_*` soak logs, `prompt_d_real_soak.sqlite`, old config backup
   (all gitignored local residue).
5. **Docs**: README/VERSION/CHANGELOG updated; `AGENTS.md` single-user governance simplification
   (Issue-first kept, IP numbering + release gate suspended with restoration trigger); new
   `docs/architecture/Atlas_OS_Lean_Runtime_v1.6.md`.
6. **Validator alignment**: scripts that assert full-pipeline telemetry now set
   `cognition_mode="full"` explicitly (`validate_task_aware_multi_llm_routing_v1_5`,
   `validate_prompt_c_completion`, `validate_goal_07_autonomous_operations`).
   `validate_goal_07` `recovery.daemon_restart` assertion updated from `decision_briefs >= 2` to
   `>= 1`: after the repair's material-delta gate, an identical second tick is deduplicated by
   design (verified pre-existing at repair commit `1a2eb7b` via clean worktree baseline).

## Verification

- `py_compile` on all touched files: PASS.
- Lean single cycle (throwaway db): brief published, cognition_state = {fusion, controller,
  memory, mode}; full single cycle: trust_score + llm_feedback applied as before.
- Market data: cache write / stale fallback labeling / backoff schedule / >2d cutoff / corrupt
  cache tolerance — all PASS (throwaway script, no repo residue).
- Regression: `validate_realtime_brief_closure` PASS, `validate_runtime_daemon_v0_1` PASS,
  `validate_task_aware_multi_llm_routing_v1_5` PASS, `validate_prompt_c_completion` PASS,
  `validate_home_intelligence_surface` PASS, `validate_autonomous_runtime_v0_2` PASS,
  `validate_goal_07_autonomous_operations` PASS (after assertion alignment).
- UI smoke: /home /markets /portfolio all HTTP 200 on the running UI.

## Notes

- Live daemon (UI-spawned) still runs pre-v1.6 code in memory; a restart is required for lean mode
  and data resilience to take effect (not restarted in this session).
- Atlas Core remains v2.1 RC; no CDE, Decision Contract, portfolio, or trading semantics changed.
