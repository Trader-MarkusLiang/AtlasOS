# Atlas OS Live Runtime Failure Injection Report

Date: 2026-07-08

## Verdict

Classification: `REAL_RUNTIME_PROVEN` for tested failures, `PARTIAL` for exact provider timeout.

## Failure Cases

| Case | Result |
|---|---|
| Primary provider failure | MoreCode returned HTTP 401; router fell back to ARK |
| Provider fallback | ARK returned valid raw content through router |
| Market refresh failure | AAPL yfinance rate limit produced degraded market state, daemon stayed success |
| Missing optional market channel | breadth/news/macro/narrative remained `NOT_CONFIGURED`, not fake zero |
| Malformed inbox event | bad JSONL skipped; valid event handled |
| Corrupt telemetry final line | telemetry reader returned invalid record and continued |
| UI restart | stale UI server restarted; missing routes recovered |
| Daemon start/stop | `/control/start` and `/control/stop` worked |
| Stale PID | stale pid file removed |

## Evidence Highlights

Malformed inbox daemon result:

```text
daemon_rc: 0
tick_status: success
events handled: simulated attention, prompt_d_failure attention, heartbeat
processed file: events.jsonl.processed
```

Provider fallback:

```text
morecode -> HTTP 401
ark -> ok
latency: 10051 ms
```

Market degraded:

```text
price_volume: FAILED
portfolio_relevance: LIVE
proof_mode: DEGRADED_PROVIDER_PROOF
daemon_rc: 0
```

## Limit

An exact slow network timeout against the active provider was not separately held open because the
local provider failure path already produced fallback and the daemon stayed alive.
