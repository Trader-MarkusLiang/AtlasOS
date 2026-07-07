# Atlas OS Active Execution Path Audit

Date: 2026-07-08

| Stage | Actual Function / Caller | Persisted Output | Classification | Notes |
|---|---|---|---|---|
| UI chat input | `ui.app_server.append_chat_event` -> `runtime/inbox/user_event.jsonl` | JSONL inbox | ACTIVE | UI does not call cognition directly. |
| Input normalization | `runtime.adapter.input_router.route_to_runtime_event` | Routed event dict | ACTIVE | Illegal fields stripped before EventStream. |
| Event queue | `runtime.event_stream.EventStream.enqueue_event` | SQLite `events` | ACTIVE | BMPL perception deformation applies before persist. |
| Corrupt inbox recovery | `runtime.event_stream._read_event_file` | Valid events only | ACTIVE_FIXED | Bad JSONL lines skipped after morning repair. |
| Market refresh | `runtime.market_intelligence.refresh_market_intelligence` via daemon | `market_intelligence_state`, EventStream events when configured | ACTIVE_WITH_FALLBACK | Price/volume only; other channels explicit missing. |
| Event Fusion | `DecisionLoop.run_once` -> `EventFusionEngine.fuse` | `cognition_state.fusion` | ACTIVE | Existing cognition core unchanged. |
| Regime Memory | `RegimeMemory.record` | `cognition_state.memory` | ACTIVE | Used by State Controller. |
| CIL / World / LMSE / MPCE / MLE / UMIS | `DecisionLoop.run_once` chained calls | `cognition_state` subfields | ACTIVE | Symbolic/non-ML. |
| Hypothesis generation/scoring | `generate_causal_hypotheses`, `score_causal_hypotheses`, `select_active_causal_structure` | `causal_hypothesis_memory` | ACTIVE | Forecast outcome memory now also stored; full reranking from outcomes remains partial. |
| Forecast ledger | `runtime.forecast_ledger` routes/API/tests | SQLite `forecast_ledger`; `forecast_calibration_state` | ACTIVE_FIXED | OPEN -> MATURED -> evaluated now proven in temp DB. |
| Decision Contract | `runtime.orchestrator._run_decision_contract` | DecisionPacket metadata | ACTIVE | LLM output parsed/validated by contract. |
| LLM Router | `runtime.llm.provider_router.route_llm_request` | LLM trace + provider health | ACTIVE_FIXED | Empty responses now fail over. |
| Feedback / Trust | `DecisionLoop.run_once`; forecast calibration update | `system_trust_state` | ACTIVE_WITH_FALLBACK | Forecast error affects trust metadata. |
| Structural update | `apply_structural_drift`, `run_self_organization_cycle` | `structural_coevolution_state` | ACTIVE | Bounded symbolic update. |
| Portfolio relevance | `runtime.portfolio_context.build_portfolio_context` | Decision Brief portfolio section, `/state` | ACTIVE | Percentage-only, read-only. |
| Decision Brief | `runtime.decision_brief.generate_decision_brief` | SQLite `decision_briefs` | ACTIVE | Standard Atlas vocabulary only. |
| UI output | `ui.app_server` routes | HTTP HTML/JSON | ACTIVE | Real HTTP 200 smoke. |

Critical path repairs made:

- Provider router rejects empty provider responses.
- EventStream skips malformed JSONL lines.
- Forecast Ledger gained maturity, lineage, trust/calibration metadata.
- Test fake keys no longer use real-looking `sk-` prefix.
