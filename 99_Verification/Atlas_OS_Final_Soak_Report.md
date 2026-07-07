# Atlas OS Final Soak Report

Date: 2026-07-08

## Type

Accelerated soak only. Not 24-hour proof.

## Command

```bash
PYTHONDONTWRITEBYTECODE=1 ATLAS_USER_CONFIG="$tmpdir/config.json" \
python3 runtime/atlas_runtime_daemon.py \
  --max-cycles 50 \
  --no-sleep \
  --db-path "$tmpdir/state.sqlite" \
  --log-path "$tmpdir/runtime.log" \
  --market-config-path "$tmpdir/config.json" \
  --market-refresh-every-cycles 1
```

## Result

- Exit code: 0.
- Real time: 1.39 seconds.
- Maximum resident set size: 30,310,400 bytes.
- Runtime log lines: 50.
- `system_logs`: 100.
- `decision_briefs`: 50.
- `events`: 51.
- `state_transitions`: 50.
- `tick_errors`: 0.
- Market statuses: `no_configured_assets` x 50.

## Verdict

PASS_ACCELERATED. Real soak evidence is still missing.
