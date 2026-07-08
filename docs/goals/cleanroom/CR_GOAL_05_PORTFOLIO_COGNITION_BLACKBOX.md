# CR_GOAL_05 - PORTFOLIO COGNITION BLACK-BOX

## Objective

Prove real UI-configured portfolio context changes normal runtime output without exact monetary
amounts.

## Required Cases

- Portfolio A: AI hardware concentrated.
- Portfolio B: high cash / low exposure.
- Portfolio C: single-theme concentration.
- Portfolio D: no portfolio.

Use the same market environment.

## Required Path

```text
UI -> persisted config -> runtime load -> portfolio context -> DecisionLoop
-> Decision Brief -> UI
```

## Classification

- `BLACKBOX_PROVEN`
- `REAL_RUNTIME_PROVEN`
- `CONFIG_ONLY`
- `UI_ONLY`
- `FAILED`

