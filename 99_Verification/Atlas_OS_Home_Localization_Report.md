# Atlas OS Home Localization Implementation Report

Date: 2026-07-09 22:20 CST

## Verdict

Implemented. Atlas OS Home now uses a UI-only cognitive localization projection for dynamic
DecisionPacket, market freshness, proactive update, and right-inspector content.

## Scope Boundary

This work stayed inside allowed presentation surfaces:

- `ui/presentation/cognitive_localization.py`
- `ui/pages/product_views.py`
- `ui/components/context_inspector.py`
- `ui/app_server.py`
- `ui/design/tokens.py`
- `ui/i18n/i18n.py`
- `99_Verification/**`

No Event Fusion, CIL, LMSE, MPCE, MLE, UMIS, CDE, Decision Contract semantics, forecast semantics,
portfolio logic, trading authority, or runtime reasoning logic was modified.

## Implementation Summary

### Locale-Aware Presentation Adapter

Created `ui/presentation/cognitive_localization.py` as the dynamic cognitive-output presentation
layer. It builds a localized, read-only UI projection from existing state and keeps raw source
evidence intact.

Implemented mappings and helpers for:

- canonical market concepts;
- actions;
- risk levels;
- causal factors;
- refresh channels;
- backend status values;
- market labels;
- asset refresh descriptions;
- proactive update focus items;
- human-readable timestamps.

The adapter avoids fragile paragraph replacement as the main mechanism. It extracts canonical
concepts from structured runtime state and DecisionPacket fields, then renders concise localized
presentation fields.

### Home Rebuild

Updated `ui/pages/product_views.py::home_content()` to render:

- localized hero state;
- secondary English technical label in smaller typography;
- localized action label;
- localized risk label;
- concise localized causal summary;
- localized data freshness;
- localized proactive update plan;
- raw evidence only inside collapsed expert details.

### Right Inspector

Updated `ui/components/context_inspector.py` to render the localized inspector projection:

- `为什么会这样` / `Why this happened`;
- three structured reason sections;
- localized top causal factor badges;
- localized portfolio status.

### Live Polling Path

Updated `ui/app_server.py::state_api()` to append:

```json
ui_presentation
```

This payload is generated from runtime state at request time and consumed by browser-side polling.
The browser update path now reads `state.ui_presentation` for dynamic labels, causal summaries,
factor badges, trust/stability text, and the event stream action label.

### Raw Evidence Preservation

The original DecisionPacket and runtime state are still available in Home under:

```html
<details class="expert-details">
```

The collapsed expert section preserves source evidence such as `last_decision_packet`,
`market_intelligence`, `causal_summary`, raw backend status strings, and ISO timestamps.

## Verification

Commands run:

```bash
python3 -m py_compile ui/presentation/cognitive_localization.py ui/components/context_inspector.py ui/pages/product_views.py ui/app_server.py ui/design/tokens.py ui/i18n/i18n.py 99_Verification/validate_home_localization_v2.py
python3 99_Verification/validate_home_localization_v2.py
```

Latest validator result:

```json
{
  "status": "PASS"
}
```

Artifacts:

- `99_Verification/artifacts/home_localization/home_zh_validator.html`
- `99_Verification/artifacts/home_localization/home_en_validator.html`
- `99_Verification/artifacts/home_localization/home_localization_validator_result.json`

## Defects Fixed

- `HERO_ENGLISH_LEAK`
- `LONG_ENGLISH_PARAGRAPH`
- `ACTION_NOT_LOCALIZED`
- `FACTOR_LABEL_NOT_LOCALIZED`
- `INSPECTOR_MIXED_LANGUAGE`
- `RAW_ISO_TIMESTAMP`
- `DYNAMIC_OUTPUT_BYPASSES_I18N`

## Residual Risk

The localization layer is intentionally a presentation projection. It does not translate arbitrary
future raw model paragraphs as source truth. If a future runtime field introduces a new canonical
concept, the UI will fall back to a localized generic state and keep raw text under expert details
until the concept map is extended.
