# Atlas OS Local Position Valuation Privacy Boundary

Date: 2026-07-14

Linked Issue: `ISSUE-2026-061`

Linked IP: `IP-2026-061`

## Classification

Local portfolio valuation infrastructure. It is not a cognition Engine, prediction model, trading
Engine, broker adapter, Decision Contract extension, or CDE authority.

## Data Paths

The existing cognition path remains percentage-only:

```text
ignored local configuration
-> build_portfolio_context()
-> DecisionLoop / cognition / LLM-safe context
```

The private Home path is separate:

```text
ignored local configuration
-> validated private position inputs
-> latest normalized market observations
-> deterministic local valuation
-> privacy-filtered localhost Home projection
-> Home HTML
```

## Sensitive Fields

- `average_cost_price`
- `quantity`
- total position cost
- current market value
- unrealized PnL amount
- exact account value
- execution price or history
- broker data

These fields may exist only in ignored local configuration and ephemeral local valuation results.
They must not enter general `/state`, EventStream, cognition state, Decision Contract, LLM prompts,
telemetry, snapshots, replay, runtime logs, verification evidence, or Git.

## Allowed Derived Context

The initial implementation keeps exact and derived cost/PnL values entirely in deterministic local
UI processing. It does not add gain/drawdown classifications to cognition or LLM context. Review
priority and Atlas posture continue to come from existing evidence, portfolio, and CDE boundaries.

## Mathematical Rules

- Use decimal arithmetic for user-entered financial values.
- Do not calculate return without valid same-currency cost and real usable latest price.
- Do not calculate amount metrics without quantity.
- Do not calculate aggregate current weight without complete normalized values and explicit cash
  treatment.
- Never silently equate CNY, HKD, or USD and never hard-code FX.
- Missing, failed, simulated, stale, or identity-mismatched observations remain explicit states.

## API Boundary

General `/state` stays private-field-free. A dedicated localhost-only Home valuation endpoint may
return only fields authorized by local display preferences. It must reject non-loopback clients,
avoid cache persistence, and never log raw request or response values.

## Decision Boundary

Cost and PnL can clarify drawdown attention, concentration, capital efficiency, rebalance friction,
and review urgency in the user interface. They do not directly change regime labels, causal weights,
trust, hypotheses, CDE authority, or Atlas action posture.
