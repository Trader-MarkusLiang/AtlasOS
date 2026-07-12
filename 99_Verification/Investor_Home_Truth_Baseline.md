# Investor Home Truth Baseline

Date: 2026-07-12 13:03 CST

## Scope

This baseline records the live investor Home, `/state`, daemon, provider, market-intelligence,
proactive-update, and forecast-accountability state before Goal implementation.

## Claim Versus Runtime Matrix

| Product claim | Authoritative runtime evidence | Classification |
|---|---|---|
| Runtime is active | Daemon PID active for more than two days; UI launchd service active on `8765` | `REAL_RUNTIME_PROVEN` |
| Portfolio context is configured | Aggregate exposure is 80%; unassigned allocation is 20% | `REAL_RUNTIME_PROVEN` |
| Portfolio price observations are refreshed | `price_volume: FAILED`; all returned observation records are `Unavailable`, freshness `Unknown`, source `none` | `FAILED` |
| Market breadth is available | `market_breadth: NOT_CONFIGURED` | `NOT_CONFIGURED` |
| News and announcements are available | `news_announcement: NOT_CONFIGURED` | `NOT_CONFIGURED` |
| Macro and policy are available | `macro_policy: NOT_CONFIGURED` | `NOT_CONFIGURED` |
| Narrative and attention sources are available | `narrative_attention: NOT_CONFIGURED` | `NOT_CONFIGURED` |
| MoreCode is configured | LLM traces identify MoreCode and model `gpt5.5` | `CONFIGURED` |
| Latest LLM reasoning succeeded | Latest DecisionPacket is failsafe with `all_providers_failed` and confidence `0.0` | `FAILED` |
| Proactive update performs research | A two-hour plan is generated and enqueued; no source retrieval is performed by the planner | `PLANNED_ONLY` |
| Forecast lifecycle is operating | Forecast records exist, but current state has zero matured and zero evaluated outcomes | `OPEN_LOOP_RUNTIME` |
| Home evidence labels are truthful | Home tests list presence rather than observation usability in several presentation helpers | `FAILED` |

## Confirmed Defects

1. Unavailable market records can be counted as fresh, live, or usable by Home presentation logic.
2. The Home header identifies the configured provider but not the latest inference outcome.
3. Static framework snapshots and runtime observations are visually adjacent without a consistent
   investor-facing evidence classification.
4. Proactive update is a research planner, not a source retrieval path.
5. Forecast registration is not material-change gated and normal runtime does not close outcomes.

## Boundaries

- No Event Fusion, CIL, LMSE, MPCE, MLE, UMIS, CDE, or Decision Contract semantics need to change.
- Required repairs belong to presentation truth, market-source adapters, Forecast Ledger integration,
  and verification.
- No broker integration, trading execution, ML, DL, RL, or private portfolio persistence is authorized.

## Initial Verdict

`PROVEN_PARTIAL`

The current product is a functioning portfolio-aware runtime surface, but it is not yet a truthful,
multi-source, accountable investor decision product.
