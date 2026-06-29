# Release Gate

Only release when all gates pass.

| Gate | Requirement | Status |
|---|---|---|
| Structure | Repository, directories, version, changelog, release tag | PASS |
| Knowledge | Required knowledge modules present and coverage reported | PASS |
| Reasoning | Required reasoning cases match Atlas consensus | PASS |
| Trading | Trading OS can output ranking, relay, position, risk, waiting conditions | PASS |
| Regression | Required regression cases pass | PASS |
| Production Trial Validation | Architecture remains frozen during Production Trial, multiple consecutive Decision Briefs require no major redesign, no critical regression appears, and user confirms production usability | PENDING |

## Release Lifecycle

```text
Alpha
 ↓
RC
 ↓
Production Trial
 ↓
Final
```

Production Trial means:

- Architecture frozen.
- Daily real usage.
- Only bug fixes.
- Only usability improvements.
- No new Engine.
- No workflow redesign.

Do not hardcode fixed Production Trial numbers. Use real operating quality:

- Decision quality remains stable.
- Capital discipline remains intact.
- Explainability remains clear.
- Traceability remains intact.
- User confirms production usability.

## v0.2 Alpha Decision

Release status: PASS

Release tag: `v0.2-alpha`

Notes:

- This release remains a knowledge repository.
- It does not add dashboard, agent, crawler, web frontend, API, or database program features.
