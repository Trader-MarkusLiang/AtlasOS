# Investor Home Product Acceptance Report

Date: 2026-07-12
Verdict: `PROVEN_PARTIAL`

## Product Contract

Home now follows the investor decision sequence:

1. portfolio command view and configured holdings;
2. today's decision-review need;
3. material evidence with provenance;
4. Signal -> Evidence -> Structure -> Causal -> Thesis -> Portfolio -> Counter-evidence -> Missing
   evidence -> Conditional conclusion;
5. four accountable scenarios and conditional posture;
6. candidate research priority, explicitly separate from CDE authority;
7. forecast accountability and learning evidence.

The first desktop viewport shows both portfolio state and today's review conclusion. On mobile, the
portfolio header exposes the Atlas posture and decision-review status before detailed metrics.

## Acceptance Matrix

| Requirement | Result | Evidence |
|---|---|---|
| Portfolio-first and decision-first | PASS | `portfolio_first_chain_order`; local-only browser validation |
| Honest observation quality | PASS | unavailable exclusion and missing-change checks |
| Provider identity vs inference | PASS | `/state` registry and trace summary |
| Real observation reaches Home | PASS | 3 usable portfolio observations |
| Traceable material evidence | PASS | source/timestamp/freshness/truth labels in Home |
| Portfolio-dependent scenarios | PASS | A/B/C/no-portfolio signatures differ |
| Candidate score vs CDE | PASS | score `N/A`; CDE separately unavailable |
| Normal forecast closure | PASS | material dedup + next-cycle evaluation |
| Miss changes later behavior | PASS | `REAL_RUNTIME_BEHAVIORAL_LOOP` |
| zh/en semantic structure | PASS | Home surface and localization validators |
| Desktop/mobile browser layout | PASS | no document-level horizontal overflow |
| Narrative / public attention | EXTERNAL_BLOCKER | channel remains `NOT_CONFIGURED` |

## Boundary Review

No Event Fusion, CIL, LMSE, MPCE, MLE, UMIS, CDE, or Decision Contract semantic rewrite was used.
No broker integration or trade execution was added. Candidate ranking remains research priority.

`PROVEN_PARTIAL` is required because narrative/public-attention evidence is not configured and the
strict full-history price validator remains externally degraded, even though current portfolio
quotes and official policy/announcement evidence are available.
