# Atlas OS Frontend Bilingual Report

Date: 2026-07-08

## Implementation

Expanded `ui/i18n/i18n.py` with global shell, navigation, status, page, flow, inspector, product
page, visualization, setup, and settings strings for English and Chinese.

Global language toggle is rendered in `ui/components/language_toggle.py` and persists through:

`POST /ui/language`

## Validation

Executed language smoke:

- `POST /ui/language {"language":"en"}` -> `{"status":"saved","language":"en"}`
- `/` H1 in English: `Atlas is waiting for a reliable market change.`
- `/settings` H1 in English: `Provider Control`
- `POST /ui/language {"language":"zh"}` -> `{"status":"saved","language":"zh"}`
- `/` H1 in Chinese: `Atlas 正在等待可靠的市场变化。`
- `/settings` H1 in Chinese: `Provider 控制`

## Coverage

Primary navigation and page titles now have EN/CN parity:

- Home
- Ask Atlas
- Portfolio
- Markets
- Predictions
- Learning
- Workflow
- Roadmap
- Dev Registry
- Settings
- Setup
- System Guide

## Remaining Risk

Some technical provider names, model IDs, runtime statuses, and evidence labels intentionally remain
as configured/provider-origin text. They are data values, not UI copy.

Result: `PASS`
