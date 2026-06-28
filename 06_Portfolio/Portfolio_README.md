# Atlas Portfolio Layer

Atlas Portfolio Layer turns research into capital management. It does not replace the Living
Database, Trading OS, or Execution Review.

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
