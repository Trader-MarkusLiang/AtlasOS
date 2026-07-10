# Atlas OS User Decision Home Final Acceptance

Date: 2026-07-10

## Final Verdict

PASS.

Atlas OS Home has been rebuilt from six equal-weight intelligence modules into a single user
decision journey:

what changed -> strongest judgment -> portfolio relevance -> current decision agenda -> what would
change the view -> top research priorities.

## Hard Acceptance Matrix

| ID | Requirement | Evidence | Status |
|---|---|---|---|
| A | Home follows one decision journey | `data-home-layout="user-decision-journey"` and validator journey order check | PASS |
| B | First viewport has max four primary blocks | `data-primary-block` count is exactly 4 | PASS |
| C | One Core Judgment exists | `#home-core-judgment` count is 1 | PASS |
| D | One strongest Forward View exists | `#home-strongest-forward-view` count is 1 | PASS |
| E | Horizon and confidence visible | Validator and browser E2E steps 4-5 | PASS |
| F | Portfolio Relevance visible | Browser E2E steps 6-7 | PASS |
| G | Decision Agenda visible | Browser E2E step 8 | PASS |
| H | Maximum 3 focus items | Validator and browser E2E step 10 | PASS |
| I | Positive/negative decision triggers visible | Validator and browser E2E steps 11-12 | PASS |
| J | Only Top 3 research priorities on Home | `data-research-priority` count is 3 | PASS |
| K | Full candidate pool behind link | `/candidates` link and browser E2E step 15 | PASS |
| L | Forecast Accountability compact | Count keys limited to open/verified/invalidated/inconclusive | PASS |
| M | Expert Analysis secondary and collapsed | Browser E2E steps 20-21 | PASS |
| N | No six equal-weight intelligence modules | Old Home IDs absent; candidate table/filter absent on Home | PASS |
| O | 24-step E2E passes | `browser_e2e_results.json` status `PASS` | PASS |
| P | Human comprehension checklist passes | `Atlas_OS_Home_User_Comprehension_Report.md` | PASS |

## Defects Found

1. Old Home rendered six comparable modules.
2. Candidate pool table and filters competed with the decision path.
3. Forecast timeline was too detailed for Home.
4. Expert analysis was visible as a full peer section.
5. Initial rebuild over-scaled portfolio percentages because confidence helpers were reused for
   portfolio percentage fields.
6. Initial research-priority matching used broad theme terms and could match static candidates too
   loosely.
7. First browser E2E selector for Expert Analysis matched a nested Raw Evidence summary too.

## Defects Fixed

1. Replaced Home with a decision-first IA and exactly four first-viewport primary blocks.
2. Moved full candidate pool mechanics behind `/candidates`.
3. Replaced scenario grid with one strongest Forward View and falsification condition.
4. Added presentation-only Conviction Hierarchy.
5. Added Decision Agenda with exactly three focus items.
6. Added positive/negative decision triggers.
7. Added Top 3 research priorities with explicit candidate-priority truth label.
8. Compact Forecast Accountability now shows only required counts, recent miss, and changed-afterward.
9. Expert Analysis is secondary and collapsed by default.
10. Fixed percentage handling and current-portfolio candidate matching.
11. Re-ran browser E2E with a precise expert summary selector.

## Verification Commands

```bash
python3 -m py_compile ui/presentation/home_intelligence.py ui/pages/product_views.py ui/app_server.py
python3 99_Verification/validate_user_decision_home.py
```

Browser E2E was run against:

```text
http://127.0.0.1:8765/
```

## Evidence Artifacts

- `99_Verification/artifacts/user_decision_home/validator_results.json`
- `99_Verification/artifacts/user_decision_home/browser_e2e_results.json`
- `99_Verification/artifacts/user_decision_home/browser_home_1024.png`
- `99_Verification/artifacts/user_decision_home/home_en.html`
- `99_Verification/artifacts/user_decision_home/home_zh.html`
- `99_Verification/artifacts/user_decision_home/candidates_en.html`
- `99_Verification/artifacts/user_decision_home/candidates_zh.html`

## Boundary Confirmation

No cognitive/runtime semantics were changed. The rebuild is limited to:

- `ui/presentation/home_intelligence.py`
- `ui/pages/product_views.py`
- `99_Verification/*`

No trading execution, broker connection, CDE override, forecast semantic change, candidate semantic
change, or portfolio mutation was introduced.
