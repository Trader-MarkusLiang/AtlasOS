# Atlas OS Home Bilingual Dynamic Output Report

Date: 2026-07-09 22:20 CST

## Purpose

Prove that Home localization works for dynamic cognitive output, not just static i18n chrome.

## Dynamic Sources Covered

The localized projection covers:

- `last_decision_packet.regime_state`
- `last_decision_packet.recommended_action`
- `last_decision_packet.risk_level`
- `last_decision_packet.attention_state`
- `last_decision_packet.liquidity_state`
- `last_decision_packet.causal_summary`
- `last_decision_packet.reasoning_trace`
- `market_intelligence.channels`
- `market_intelligence.observations`
- `proactive_update_state.market_channels_to_refresh`
- `proactive_update_state.research_focus`
- `proactive_update_state.timestamp`
- `proactive_update_state.next_due_at`

## Chinese Mode Result

Chinese mode is now Chinese-dominant:

- Hero primary label is Chinese.
- English appears only as a smaller secondary technical label where useful.
- Action labels render as Chinese first, English second.
- Causal summary is generated from structured state as three concise Chinese reason sections.
- Right inspector renders Chinese section titles and Chinese body text.
- Factor badges are Chinese first with secondary English technical notation.
- Refresh channels are localized.
- Asset-specific refresh descriptions are localized.
- Primary UI does not show raw ISO timestamps.
- Raw English DecisionPacket evidence is hidden by default under expert details.

## English Mode Result

English mode remains clean:

- Hero, action, causal summary, inspector, factor badges, freshness channels, and asset rows render
  in English.
- Chinese labels do not leak into primary English content.
- Expert details still preserve raw source evidence.

## Validator Evidence

Validator:

```bash
python3 99_Verification/validate_home_localization_v2.py
```

Latest result file:

```text
99_Verification/artifacts/home_localization/home_localization_validator_result.json
```

Privacy note: raw rendered HTML and JSON artifacts are local verification evidence and are ignored
by Git because they can include private portfolio context from the Home page.

Current gate result:

| Gate | Result |
|---|---|
| A Chinese hero | PASS |
| B secondary English label | PASS |
| C localized action | PASS |
| D Chinese causal summary | PASS |
| E Chinese right inspector | PASS |
| F Chinese factor badges | PASS |
| G Chinese freshness channels | PASS |
| H Chinese asset descriptions | PASS |
| I no raw ISO primary UI | PASS |
| J raw English hidden by default | PASS |
| K expert evidence accessible | PASS |
| L English mode clean | PASS |
| M zh/en parity | PASS |

## Browser E2E Evidence

Exact 24-step browser E2E result:

```text
99_Verification/artifacts/home_localization/home_localization_e2e_result.json
```

Screenshots:

- `99_Verification/artifacts/home_localization/e2e_final_01_english_home_1440.png`
- `99_Verification/artifacts/home_localization/e2e_final_04_chinese_home_1440.png`
- `99_Verification/artifacts/home_localization/e2e_final_13_expert_open.png`
- `99_Verification/artifacts/home_localization/e2e_final_responsive_1440.png`
- `99_Verification/artifacts/home_localization/e2e_final_responsive_1280.png`
- `99_Verification/artifacts/home_localization/e2e_final_responsive_1024.png`

Privacy note: screenshots are local-only artifacts for this run and are not pushed to the remote
repository when they may contain private portfolio context.

24-step status:

| Step | Requirement | Result |
|---:|---|---|
| 1 | Open Home in English | PASS |
| 2 | Verify English hero | PASS |
| 3 | Switch Chinese | PASS |
| 4 | Verify Chinese hero | PASS |
| 5 | Verify secondary English technical label | PASS |
| 6 | Verify action localized | PASS |
| 7 | Verify causal summary Chinese | PASS |
| 8 | Verify right inspector Chinese | PASS |
| 9 | Verify factor badges Chinese | PASS |
| 10 | Verify refresh channels Chinese | PASS |
| 11 | Verify asset rows localized | PASS |
| 12 | Verify timestamps human-readable | PASS |
| 13 | Expand expert details | PASS |
| 14 | Verify raw source evidence remains accessible | PASS |
| 15 | Collapse expert details | PASS |
| 16 | Switch English | PASS |
| 17 | Verify English page | PASS |
| 18 | Verify no Chinese leakage | PASS |
| 19 | Test 1440 | PASS |
| 20 | Test 1280 | PASS |
| 21 | Test 1024 | PASS |
| 22 | Test long Chinese wrapping | PASS |
| 23 | Reload page | PASS |
| 24 | Confirm language persists | PASS |

## Evidence Preservation

Raw evidence remains accessible but hidden by default. The expert details screenshot proves that
source evidence contains raw fields such as `last_decision_packet`, English `causal_summary`, raw
backend statuses, and ISO timestamps only after explicit expansion.
