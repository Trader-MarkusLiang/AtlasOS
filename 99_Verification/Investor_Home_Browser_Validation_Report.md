# Investor Home Browser Validation Report

Date: 2026-07-12
Browser target: `http://127.0.0.1:8765/`

## Desktop

- viewport: 1440x1000;
- document width: 1440;
- horizontal overflow: none;
- portfolio command is the primary surface;
- today's action review is visible in the first viewport;
- holdings use a compact three-column evidence review at desktop width.

## Mobile

- viewport: 390x844;
- document width: 390;
- content width: 362;
- horizontal overflow: none;
- App Shell navigation compresses to an approximately 99px product header with horizontal primary navigation;
- tables and framework paths scroll inside their own containers rather than expanding the page;
- Chinese action state renders as `需要条件确认` rather than a raw runtime enum.

## Accessibility and Readability

- heading scale is constrained to three practical levels;
- long action text wraps inside its container;
- source links remain keyboard-focusable;
- mobile navigation remains reachable without hiding primary product pages;
- `prefers-reduced-motion` is honored by the shared design tokens.

Artifacts:

- `99_Verification/artifacts/investor_home/browser_layout_result.json`

Browser screenshots containing local portfolio composition remain local-only and are intentionally
excluded from Git evidence.

Result: `PASS`.
