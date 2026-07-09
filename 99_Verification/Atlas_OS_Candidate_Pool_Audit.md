# Atlas OS Candidate Pool Audit

Date: 2026-07-10 CST

## Verdict

`PRESENT_AND_CONNECTED`

The candidate pool exists in the repository and is now restored to the Home surface and the
presentation-only `/candidates` / `/research-candidates` routes.

## Source

Authoritative source:

- `02_Databases/AI_Shovel_100.md`

Audited structures:

- `Priority S: Portfolio / Core Holdings`
- `Priority A: Atlas Core Research Pool`
- `Priority B: Watch Pool`

Current parsed result:

- Total candidates: 27
- Portfolio-related: 7
- High priority: 20
- New: 0
- Changed recently: 6

## UI Surfaces

| Surface | Status | Evidence |
|---|---|---|
| Home candidate zone | `PASS` | `#home-research-candidates` renders Top 5 candidates and filter buttons. |
| Full candidate route | `PASS` | `/candidates` and `/research-candidates` render the same presentation-only pool. |
| Candidate detail | `PASS` | Browser E2E opened a candidate detail row and verified thesis/risk detail text. |
| Candidate filters | `PASS` | All / portfolio-related / high-priority / new / changed-recently controls exist. |
| ZH/EN labels | `PASS` | Static validator generated `validator_candidates_zh.html` and `validator_candidates_en.html`. |

## Safety Checks

Candidate ranking is not shown as trading authority.

Evidence:

- Home contains the safety line: candidate ranking is research priority only.
- Browser E2E hard check: `no_buy_sell_in_candidate_section: true`.
- Validator checks for both Home and candidates page assert no `Buy` / `Sell` text.
- Allowed candidate statuses remain presentation statuses: `Observe`, `Research`, `Watch`,
  `Elevated`, `Deprioritized`.

## Limitations

- Candidate source rows are repository-backed research records, not live market rankings.
- Portfolio relationship is a presentation mapping from the source row and configured local
  portfolio context; it is not a capital action.
- Candidate changes are derived from existing source metadata and priority structure; no new
  ranking semantics were created.

