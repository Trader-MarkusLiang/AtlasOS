# Atlas OS Ordinary User Acceptance Report

Date: 2026-07-08

## Method

Actual HTTP route checks were run against a temporary UI server. No Python-file editing was required
for the checked routes.

## Task Results

| Task | Evidence | Result | Confusion / Risk |
|---|---|---|---|
| Open Atlas | `/` HTTP 200, 3777 bytes | PASS | Home exists. |
| Understand what it does | Home copy exists | PARTIAL | Needs browser visual QA for first-glance clarity. |
| Switch Chinese / English | Existing i18n validation PASS | PASS | Not all new pages are fully key-based i18n. |
| Configure LLM | `/settings` existing provider UI validation PASS | PASS | Real Keychain save still needs live smoke. |
| Test connection | `/llm/provider/test` existing validation PASS | PASS | Depends on provider credentials/network. |
| Choose model | `/llm/provider/models` validation PASS | PASS | Unsupported providers degrade. |
| Configure portfolio percentages | `/settings` + `/portfolio` render | PASS | User must understand percentage-only privacy. |
| Start runtime | Control endpoint exists; daemon smoke run by CLI | PARTIAL | UI start not fully red-team tested in this pass. |
| See live/stale/simulated data | `/markets?format=json` labels `NOT_CONFIGURED` | PASS | Live data not proven. |
| Receive Atlas Brief | 50-cycle soak created 50 decision briefs | PASS_ACCELERATED | No real unattended day. |
| Ask a question | `/chat/send` existing UI validation PASS | PASS | Not visually tested. |
| Understand market state | `/state` and Home expose state | PARTIAL | Plain-language copy can improve. |
| Understand portfolio impact | Portfolio page and brief exposure lines differ by context | PASS | Impact remains exposure/risk, not action authority. |
| Inspect top risks | DecisionPacket risk and brief risk section | PARTIAL | Top risk ranking not separately visualized. |
| Inspect predictions | `/predictions?format=json` HTTP 200 | PASS | UI lifecycle controls still minimal. |
| Understand confidence | Home/DecisionPacket confidence exposed | PARTIAL | Explanation text could be stronger. |
| Find Roadmap / Workflow / Settings | Routes verified/previous validations PASS | PASS | Navigation exists. |
| Stop runtime | Endpoint exists; not full process-kill tested from UI | PARTIAL | Needs manual UI QA. |

## Verdict

Ordinary-user acceptance is PARTIAL. The product is usable for internal alpha testing but not yet
ready for Release Candidate labeling.
