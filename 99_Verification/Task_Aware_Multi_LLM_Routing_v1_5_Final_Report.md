# Task-Aware Multi-LLM Routing v1.5 Final Report

Date: 2026-07-13

Linked Issue: `ISSUE-2026-060`

Linked IP: `IP-2026-060`

Implementation commit: `c671297`

Scope: Runtime/UI provider orchestration only. Atlas Core remains v2.1 RC.

## Result

Atlas now has three independently configurable LLM roles over the existing Provider Registry:

- Workhorse: strict, non-authoritative Evidence Packet preparation.
- Research: strict synthesis, portfolio relevance, counter-evidence, and uncertainty packet.
- Decision: existing Decision Contract and validated DecisionPacket only.

Workhorse and Research outputs are stored only as bounded task state and brief metadata. They are
not written into Event Fusion, regime state, trust, causal weights, CDE, portfolio state, or the
LLM feedback input. Failed or cached Decision packets are marked non-fresh and cannot trigger LLM
feedback.

## Requirement Evidence

| Requirement | Evidence | Classification |
| --- | --- | --- |
| Three configurable roles | `runtime/llm/task_routing.py`, Settings role cards, `/llm/task-routes` | REAL_RUNTIME_PROVEN |
| Independent provider/model policy | Route resolution and provider-swap isolation tests | CONTROLLED_FIXTURE_PROVEN |
| Role-specific fallback | Primary failure, role-local fallback, and all-fallback failure tests | CONTROLLED_FIXTURE_PROVEN |
| Workhorse responsibility | UI query and proactive events invoke strict Evidence Packet parsing | CONTROLLED_FIXTURE_PROVEN; adapter LIVE_PROVEN |
| Research responsibility | UI query and proactive cycle invoke strict Research Synthesis parsing | LIVE_PROVEN |
| Decision authority | Existing Decision Contract parser validates final packet | LIVE_PROVEN |
| No premium call per tick | Heartbeat trace adds zero LLM telemetry rows and reuses no feedback | CONTROLLED_FIXTURE_PROVEN |
| Two-hour proactive cycle | Daemon start-due plan at 7200 seconds invokes all required roles | CONTROLLED_FIXTURE_PROVEN |
| Ask Atlas path | UI inbox -> daemon -> EventStream -> DecisionLoop -> three roles -> brief | CONTROLLED_FIXTURE_PROVEN and live-provider exercised |
| Telemetry | Role, provider, model, times, latency, status, fallback, trigger, hash, usage, cost, cache, packet ID | REAL_RUNTIME_PROVEN |
| Secret safety | Keychain reference retained; fixture secret absent from config and telemetry | REAL_RUNTIME_PROVEN |
| zh/en task UI | Desktop and 390px browser checks, role labels and authoritative Decision marker | REAL_RUNTIME_PROVEN |
| Cognitive isolation | No Core/CDE/cognition implementation diff; layer regressions pass | CONTROLLED_FIXTURE_PROVEN |

## Runtime Traces

### Complete Controlled Runtime Trace

```text
UI inbox event
-> EventStream
-> DecisionLoop and unchanged cognition layers
-> Workhorse / work-model / strict Evidence Packet
-> Research / research-model / strict Research Synthesis Packet
-> Decision / decision-model / Decision Contract validation
-> recommended_action=observe
-> persisted Decision Brief
-> role telemetry
```

All three calls returned 160 provider-reported tokens in the fixture. Workhorse and Research traces
recorded `feedback_applied=false`. The Decision trace carried a `brief-*` DecisionPacket ID.

### Live MoreCode Runtime Trace

A fresh isolated UI-inbox daemon tick used the normal runtime path:

| Role | Model | Status | Latency | Tokens | Cost status |
| --- | --- | --- | ---: | ---: | --- |
| Workhorse | `deepseek-v4-flash` | transient failsafe in full tick | 16,349 ms | Unknown | pricing_not_configured |
| Research | `kimi-k2.6` | ok | 23,252 ms | 12,134 | pricing_not_configured |
| Decision | `gpt-5.5` | ok | 6,359 ms | 8,500 | pricing_not_configured |

The Decision response produced a valid packet with `recommended_action=observe`, `risk_level=low`,
`confidence=0.32`, `decision_packet_fresh=true`, and a populated DecisionPacket ID. The brief was
persisted without raw LLM output.

The transient Workhorse failure degraded safely. A subsequent live probe using the same strict
Workhorse prompt and a minimal proactive context succeeded through MoreCode in 6,025 ms with 696
provider-reported tokens and valid JSON. No cost number is claimed because provider pricing metadata
is not configured.

### No-Change Trace

```text
heartbeat-only cycle
-> unchanged LLM trace count
-> Workhorse not called
-> Research not called
-> Decision skipped_no_meaningful_delta
-> decision_packet_fresh=false
-> llm_feedback_status=not_applied_no_fresh_decision
```

## Failure Matrix

The isolated verifier covers `401`, `429`, timeout, empty response, malformed JSON, model not found,
role-local fallback success, and all-fallback failure. A Decision chain with malformed output and no
fallback produced a non-fresh neutral failsafe and did not enter cognitive feedback.

## Browser Evidence

- Canonical UI: `http://127.0.0.1:8765/settings`
- Desktop: 1280px viewport, three visible role cards, no horizontal overflow, no console warnings.
- Mobile: 390 x 844 emulation, three 316px role cards, no horizontal overflow.
- Chinese labels: 执行模型 / 研究模型 / 决策模型.
- English labels: Workhorse / Research / Decision.
- Decision marker: `ACTIVE · Authoritative synthesis`.
- Workhorse Test Route: `ok · morecode · 5047ms`.
- Language restored to Chinese after parity validation.

## Regression Evidence

Passed:

- task-aware multi-LLM routing v1.5
- Goal 01 ordinary-user activation
- Goal 02 live-LLM failure matrix
- Decision Contract + LLM Router v0.2
- runtime observability v0.3.1
- LLM cognitive feedback v0.3
- trust calibration v0.3.2
- CIL v0.5, World Model v0.6, LMSE v0.7, MPCE v0.8, MLE v0.9, UMIS v1.0
- structural co-evolution v0.4 and causal self-discovery v0.7
- Goal 03 market intelligence, Goal 04 portfolio cognition, Goal 05 forecast accountability,
  Goal 06 self-iteration reality
- provider secret storage, provider UI i18n, control plane, cognitive control center,
  Getting Started, and productization backbone

Two pre-existing non-goal validators remain red and are not used as completion evidence:

- `validate_autonomous_runtime_v0_2.py` uses a stale repository-wide keyword scan and flags
  `market_evidence_sources.py` as a direct LLM reference.
- `validate_practical_brief_home.py` fails against unrelated dirty Home snapshot artifacts and old
  chain-order/text expectations already present before this Goal.

These failures do not contradict the task-routing execution, cognition-boundary, provider, or
Settings evidence above. They remain explicit test-debt rather than being rewritten to pass.

## Security And Boundary Conclusion

- No API key is present in Git-tracked configuration, API responses, or task telemetry.
- Local MoreCode credentials remain Keychain-first.
- Local `runtime/config/user_config.json` remains ignored and uncommitted.
- No cognition Engine, trading execution, broker integration, or autonomous agent swarm was added.
- Atlas Core, Decision Contract semantics, CDE, trust algorithms, and portfolio authority were not
  modified.

PROVEN_COMPLETE
