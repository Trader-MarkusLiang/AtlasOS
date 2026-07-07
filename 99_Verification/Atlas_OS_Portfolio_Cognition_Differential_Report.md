# Atlas OS Portfolio Cognition Differential Report

Date: 2026-07-08

## Method

Same market state, four different portfolio contexts:

- P1 high AI hardware exposure.
- P2 high cash / low risk exposure.
- P3 concentrated single-theme exposure.
- P4 no portfolio.

## Evidence

`validate_morning_red_team.py` produced:

- P1 exposure: 65%, regime sensitivity `single_theme_regime_sensitive`.
- P2 exposure: 8%, regime sensitivity `broad_or_unclassified`.
- P3 exposure: 70%, regime sensitivity `single_theme_regime_sensitive`.
- P4 status: `missing`.

Runtime briefs included different portfolio exposure lines. No Buy/Sell vocabulary appeared.

## Result

`portfolio_context_dependency_score`: 1.0 for the controlled fixture.

## Verdict

PASS for read-only portfolio context. This is not portfolio mutation and does not create CDE
authority.
