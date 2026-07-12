# Atlas OS Home Data Availability Repair

- Date: 2026-07-13 07:24 CST
- Session id: current Codex task
- Project: Atlas OS
- Workspace: `/Users/markus/AtlasOS`
- Task: Repair apparent all-data-missing Home presentation and portfolio history coverage
- Status: Completed
- Branch: `codex/frontend-master-upgrade`

## User Request Summary

Investigate why Home appears to contain only missing data and repair the real data and presentation
paths without fabricating unavailable evidence.

## Investigation

- Runtime is healthy and `/state` exposes 3 usable portfolio quotes, 7 evidence items, and a
  successful MoreCode inference.
- The three holdings lack 5/20/60-day data because all history providers fail before the Tencent
  quote-only fallback.
- Tencent's public daily K-line endpoint is reachable for all three configured A/H-share holdings.
- Candidate rows repeat unsupported market confirmation, numeric score, and CDE fields, producing
  most of the visible `Data Missing` labels.

## Decisions

- Extend the existing provider, not cognition or UI network behavior.
- Replace repeated missing cells with supported research-priority fields and one honest limitation.
- Keep unvalidated candidates collapsed by default.

## Current State

- Added Tencent K-line history fallback for A-share and Hong Kong holdings.
- Added the source URL mapping to runtime market intelligence.
- Reworked the candidate surface to prioritize validated candidates, show real market confirmation
  only when available, and collapse six unvalidated candidates.
- Replaced repeated missing-value cells with one capability limitation while preserving honest
  evidence gaps.
- Restored the UI to Chinese after validation.

## Verification

- All three configured holdings expose current, 5-day, 20-day, and 60-day observations.
- Desktop browser: zero `Data Missing` / `数据缺失` labels.
- Mobile browser at 390x844: zero horizontal overflow and pending candidates collapsed.
- `validate_investor_home_goal.py`: PASS.
- `validate_goal_03_market_intelligence.py`: PASS.
- `validate_home_intelligence_surface.py`: PASS.
- `validate_home_localization_v2.py`: PASS.
- Browser screenshots contain local portfolio composition and remain intentionally untracked.

## Resume Instructions

1. Keep narrative / public-attention coverage explicit as `NOT_CONFIGURED` until a bounded source
   is approved under `ISSUE-2026-056`.
2. Run localization validators serially because they share the persisted UI language setting.
3. Do not commit private runtime configuration or portfolio amounts.

## Open Questions

- US and Korean candidate history still depends on providers unavailable in the current environment;
  those candidates correctly remain in the collapsed validation queue.
