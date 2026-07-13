# Task-Aware Multi-LLM Routing

- Date: 2026-07-13 18:04 CST
- Session id: 019f0ead-cd83-7f81-8bef-ded7fb3d4659
- Project: Atlas OS
- Workspace: `/Users/markus/AtlasOS`
- Task: Implement and prove task-aware Workhorse, Research, and Decision LLM routing
- Status: Completed
- Branch: `codex/frontend-master-upgrade`

## User Request Summary

Upgrade Atlas Runtime from a single active provider into three independently configurable LLM task
roles while preserving cognition, Decision Contract, CDE, portfolio, and trading boundaries. Add
role-specific fallback, model choice, usage/cost telemetry, Settings UI, real call sites, failure
tests, browser validation, and evidence-based completion classification.

## Work Done

- Recorded and converted `ISSUE-2026-060` into `IP-2026-060` before implementation.
- Added `runtime/llm/task_routing.py` with role defaults, validation, safe API views, provider/model
  resolution, role-local fallback, timeout/token controls, telemetry, and honest cost handling.
- Extended Provider Registry support for GLM, Kimi, and DeepSeek and normalized provider token usage.
- Connected bounded Workhorse and Research responsibilities in `runtime/orchestrator.py` and kept
  the existing Decision Contract authoritative.
- Added stable-input caching and heartbeat no-call behavior; failed or cached Decision packets are
  non-fresh and cannot enter LLM feedback.
- Restricted cache writes and hits to successful, structurally valid role packets so transient
  provider failures remain retryable.
- Added role configuration, model suggestions, health/status metrics, Test Route controls, APIs,
  and complete task-routing zh/en labels.
- Fixed the Home holdings presentation variable lifecycle that blocked Goal 01 validation.
- Added architecture, machine-readable evidence, final verification report, changelog, and Runtime/UI
  v1.5 version metadata without changing Atlas Core.

## Verification

- `validate_task_aware_multi_llm_routing_v1_5.py`: PASS, including provider swap, role-local
  fallback, all-fallback failure, 401/429/timeout/empty/malformed/model-not-found, UI-to-runtime,
  proactive cycle, heartbeat no-call, failed-Decision isolation, telemetry, and secret masking.
- Goal 01, Goal 02, Decision Contract, observability, feedback, trust, provider secret storage,
  provider UI i18n, control plane, Getting Started, and productization regressions: PASS.
- CIL, World Model, LMSE, MPCE, MLE, UMIS, structural co-evolution, causal self-discovery, market,
  portfolio, forecast, and self-iteration regressions: PASS.
- Live MoreCode evidence: Workhorse route probe succeeded; Research and Decision succeeded through
  a normal isolated UI-inbox daemon tick; Decision produced a valid fresh DecisionPacket.
- Browser: canonical `8765` Settings page passed desktop and 390px overflow checks, zh/en parity,
  Test Route, and zero console warning/error checks.
- Keychain reference remained present after Settings save. Private config remains ignored.

## Decisions

- Provider Registry remains the only provider and secret catalog.
- Workhorse and Research are bounded adapter responsibilities, not cognition Engines.
- Only fresh validated Decision packets may enter existing LLM feedback.
- The 60-second daemon tick remains independent of LLM call cadence.
- Cost remains `Unknown` while provider pricing metadata is not configured.
- Completion classification is `PROVEN_COMPLETE` for this Goal.

## Known Non-Goal Test Debt

- `validate_autonomous_runtime_v0_2.py` has a stale repository-wide keyword scan that flags the
  market evidence source module.
- `validate_practical_brief_home.py` fails against unrelated pre-existing dirty Home artifacts and
  old chain-order/text expectations.
- These red tests are explicitly recorded in the final report and were not rewritten to manufacture
  task-routing completion.

## Current State

- Implementation commit `c671297` is pushed to `origin/codex/frontend-master-upgrade`.
- Canonical UI is available at `http://127.0.0.1:8765`.
- Temporary ports `8766` and `8877` are closed.
- The runtime daemon is not forced on by this Goal; users can start it through the existing UI.
- Local role assignment is MoreCode-backed Workhorse, Research, and Decision with private details
  kept outside Git.

## Resume Instructions

1. Read `99_Verification/Task_Aware_Multi_LLM_Routing_v1_5_Final_Report.md`.
2. Run `python3 99_Verification/validate_task_aware_multi_llm_routing_v1_5.py`.
3. Open `http://127.0.0.1:8765/settings` and inspect Task Routing.
4. Do not commit `runtime/config/user_config.json` or unrelated Home validation artifacts.

## Open Questions

- Provider pricing metadata is intentionally not configured, so monetary estimates remain Unknown.
