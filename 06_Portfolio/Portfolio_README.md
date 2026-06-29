# Atlas Portfolio Layer

Atlas Portfolio Layer turns research into capital management. It does not replace the Living
Database, Trading OS, or Execution Review.

Atlas Portfolio is not:

- A PMS.
- Accounting software.
- Wealth management software.
- A balance tracker.

Atlas Portfolio is a Capital Allocation OS.

It manages:

- Allocation.
- Exposure.
- Thesis.
- Risk.
- Capital Scale Tier.
- Management Mode.
- Execution Complexity.
- Liquidity Sensitivity.

It does not manage:

- Money.
- Balance.
- Net worth.
- Currency amount.
- Account value.

## Scale-Aware Privacy

Atlas is wealth-blind, but scale-aware.

Atlas does not need the user's exact total assets. It may record an abstract Capital Scale Tier so
the Portfolio Layer can judge management complexity.

Capital Scale Tier is not wealth ranking. It is a proxy for:

- Allocation complexity.
- Execution complexity.
- Liquidity sensitivity.
- Risk-budget discipline.
- Review cadence.

Git-tracked Portfolio files must never record exact account value, net worth, balance, currency
amount, cost basis, market value, or position amount.

## Consistency Rules

Consistency First.

All Portfolio Decisions must pass Portfolio Consistency Check before Portfolio Action.

Atlas must stop and ask for user confirmation if:

- Deployment + Cash Allocation does not equal 100%.
- Bucket Exposure total exceeds Deployment.
- Holding Weight total does not equal Bucket Exposure.
- Global Portfolio account weights are declared but do not equal 100%.
- Weight format is mixed or not expressed as percentage with at most one decimal place.

Failure output:

```text
Portfolio Data Inconsistent
Need User Confirmation
```

Atlas must not auto-correct inconsistent portfolio data.

## Responsibility Boundary

| Layer | Responsibility |
|---|---|
| Living Database | Research |
| Portfolio | Capital |
| Execution | Trade |
| Review | Learning |

Responsibilities must not be mixed:

- Living Database records company research, evidence, risks, and signals.
- Portfolio records capital state, position lifecycle, priority, conviction, and capital action.
- Portfolio records scale tier and complexity only as abstract privacy-preserving fields.
- Execution records actual trade actions and results.
- Review converts outcomes into learning and updates research.

## Operating Loop

```text
Research
 ↓
Trading
 ↓
Portfolio
 ↓
Execution
 ↓
Review
 ↓
Research
```

## Git Rule

Real holdings must not enter Git.

- Git stores only `Portfolio_Template.yaml`.
- Real local portfolio data belongs in `portfolio.local.yaml`.
- `portfolio.local.yaml` must stay ignored by Git.

## Portfolio Review Checklist

### Daily

- Is there a new Alpha Signal?
- Is there a new Order?
- Is there a new Risk?
- Does any position require allocation change?

### Weekly

- Should Priority change?
- Should Conviction change?
- Should Second Growth Curve be updated?

### Monthly

- Review profit.
- Review loss.
- Review mistaken judgments.
- Review correct judgments.
- Review `Execution_Log.md`.
