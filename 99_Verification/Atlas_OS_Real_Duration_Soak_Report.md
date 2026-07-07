# Atlas OS Real Duration Soak Report

Date: 2026-07-08

## Verdict

Classification: `PARTIAL`.

Prompt D ran a real wall-clock daemon soak. It was **not** a 2-hour, 4-hour, or 24-hour proof.

## Command Shape

```text
python3 runtime/atlas_runtime_daemon.py \
  --interval 10 \
  --max-cycles 6 \
  --disable-market-refresh \
  --db-path runtime/state/prompt_d_real_soak.sqlite \
  --log-path runtime/logs/prompt_d_real_soak.jsonl
```

No `--no-sleep` flag was used.

## Result

| Metric | Value |
|---|---:|
| Wall-clock span | about 3m46s |
| Cycles | 6 |
| Tick errors | 0 |
| Decision briefs | 6 |
| Forecast records | 6 |
| State transitions | 6 |
| System logs | 18 |
| DB size | 462,848 bytes |

Tick durations:

```text
37791 ms, 18045 ms, 44071 ms, 44214 ms, 51764 ms, 18051 ms
```

## Downgrade

This is real-duration evidence but short-horizon only. Stability remains unproven for 2h, 4h, 24h,
or unattended overnight use.
