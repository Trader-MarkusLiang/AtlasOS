# Atlas OS Lean Runtime v1.6

Date: 2026-07-19
Issue: `10_Production_Trial/Issues/ISSUE-2026-063_Lean_Runtime_Reduction.md`
Status: Implemented

## Why

Architecture review 2026-07-19: the default runtime cognition chain (~30 symbolic engines wired in
series) grew beyond its evidence (controlled fixtures only), while live market data retrieval was
the only red-gap area. v1.6 moves the default pipeline to a lean path and shifts complexity budget
to data resilience. Nothing is deleted; the full symbolic chain remains available behind a config
flag.

## Default (lean) pipeline

```text
EventStream (material-delta gate)
  -> EventFusionEngine.fuse()
  -> AntiOverwriteStateController.decide()
  -> RegimeMemory.record()
  -> run_state_runtime()  (Workhorse -> Research -> Decision LLM roles)
  -> atomic Brief section publication
  -> forecast ledger (registration + due evaluation)
```

The symbolic engines (CIL, world model, LMSE, MPCE, MLE, UMIC, LLM feedback, structural
co-evolution, self-organization) run only under `cognition_mode="full"`.

## Configuration

- `DecisionLoopConfig.cognition_mode`: `"lean"` (default) or `"full"`.
- CLI: `--cognition-mode {lean,full}` on `runtime.atlas_runtime_daemon` (highest priority).
- User config: `system.cognition_mode` in `runtime/config/user_config.json` (overrides the lean
  default; validated in Settings schema).
- Rollback to the legacy chain: set `cognition_mode="full"`.

## Single runtime entry

- Supported daemon: `python3 -m runtime.atlas_runtime_daemon` (also what
  `deployment/atlas_os.plist` launches and what the UI spawns).
- Deprecated in place (kept only for historical validation-script imports):
  `runtime/atlas_daemon.py`, `runtime/atlas_host.py`, `web/app.py`,
  `web/dashboard_observability.py`.

## Market data resilience

- Persistent quote cache `runtime/state/market_cache.json` (atomic writes, 500-entry cap,
  successes only).
- On provider failure / rate limit: serve the last good snapshot labeled `data_freshness: CACHED`
  with `stale_age_seconds`; entries older than ~2 days are not served (existing failure behavior
  applies instead).
- Rate-limit backoff per provider: 60s -> 300s -> 900s cap, reset on success; providers in backoff
  are skipped in favor of alternates; if all are in backoff, the stale fallback path applies.

## Boundaries (unchanged)

No CDE, Decision Contract, portfolio, broker, or trading-execution semantics changed. Missing data
is always labeled, never fabricated. The full-mode engines keep their controlled-fixture evidence
status; lean mode does not claim their validation level.
