"""Continuous event-driven decision loop for Atlas Runtime v0.2."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

try:
    from runtime.cognition.causal_intelligence_layer import infer_causal_intelligence
    from runtime.cognition.causal_graph_mutation_engine import mutate_causal_graph
    from runtime.cognition.causal_hypothesis_engine import generate_causal_hypotheses
    from runtime.cognition.causal_structure_selector import select_active_causal_structure
    from runtime.cognition.causal_self_correction_engine import apply_causal_self_correction
    from runtime.cognition.event_fusion_engine import EventFusionEngine
    from runtime.cognition.explanation_error_engine import compute_explanation_error, compute_multi_explanation_competition
    from runtime.cognition.hypothesis_memory import update_hypothesis_memory
    from runtime.cognition.hypothesis_scoring_engine import score_causal_hypotheses
    from runtime.cognition.latent_market_structure_engine import infer_latent_market_structure
    from runtime.cognition.llm_cognitive_feedback_engine import (
        apply_pending_feedback_to_fusion,
        attach_trust_weighting,
        run_cognitive_refinement_cycle,
    )
    from runtime.cognition.market_physics_constraint_engine import apply_market_physics_constraints
    from runtime.cognition.market_law_emergence_engine import infer_market_law_emergence
    from runtime.cognition.regime_memory import RegimeMemory
    from runtime.cognition.regime_explanation_alignment import align_regime_explanation
    from runtime.cognition.regime_topology_engine import evolve_regime_topology
    from runtime.cognition.self_organizing_engine import run_self_organization_cycle
    from runtime.cognition.state_controller import AntiOverwriteStateController
    from runtime.cognition.structural_drift_controller import apply_structural_drift
    from runtime.cognition.system_trust_state import update_system_trust_state
    from runtime.cognition.trust_score_engine import calibrate_confidence, compute_trust_score
    from runtime.cognition.unified_market_intelligence_core import infer_unified_market_intelligence
    from runtime.cognition.world_model_engine import simulate_market_world_model
    from runtime.event_stream import EVENT_HEARTBEAT, EventStream
    from runtime.forecast_ledger import create_forecast, latest_forecast, process_due_runtime_forecast
    from runtime.logging import log_execution, utc_now_iso
    from runtime.orchestrator import run_state_runtime
    from runtime.state_machine import RuntimeStateMachine
    from runtime.state_store import StateStore
except ModuleNotFoundError:  # pragma: no cover
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from runtime.cognition.causal_intelligence_layer import infer_causal_intelligence
    from runtime.cognition.causal_graph_mutation_engine import mutate_causal_graph
    from runtime.cognition.causal_hypothesis_engine import generate_causal_hypotheses
    from runtime.cognition.causal_structure_selector import select_active_causal_structure
    from runtime.cognition.causal_self_correction_engine import apply_causal_self_correction
    from runtime.cognition.event_fusion_engine import EventFusionEngine
    from runtime.cognition.explanation_error_engine import compute_explanation_error, compute_multi_explanation_competition
    from runtime.cognition.hypothesis_memory import update_hypothesis_memory
    from runtime.cognition.hypothesis_scoring_engine import score_causal_hypotheses
    from runtime.cognition.latent_market_structure_engine import infer_latent_market_structure
    from runtime.cognition.llm_cognitive_feedback_engine import (
        apply_pending_feedback_to_fusion,
        attach_trust_weighting,
        run_cognitive_refinement_cycle,
    )
    from runtime.cognition.market_physics_constraint_engine import apply_market_physics_constraints
    from runtime.cognition.market_law_emergence_engine import infer_market_law_emergence
    from runtime.cognition.regime_memory import RegimeMemory
    from runtime.cognition.regime_explanation_alignment import align_regime_explanation
    from runtime.cognition.regime_topology_engine import evolve_regime_topology
    from runtime.cognition.self_organizing_engine import run_self_organization_cycle
    from runtime.cognition.state_controller import AntiOverwriteStateController
    from runtime.cognition.structural_drift_controller import apply_structural_drift
    from runtime.cognition.system_trust_state import update_system_trust_state
    from runtime.cognition.trust_score_engine import calibrate_confidence, compute_trust_score
    from runtime.cognition.unified_market_intelligence_core import infer_unified_market_intelligence
    from runtime.cognition.world_model_engine import simulate_market_world_model
    from runtime.event_stream import EVENT_HEARTBEAT, EventStream
    from runtime.forecast_ledger import create_forecast, latest_forecast, process_due_runtime_forecast
    from runtime.logging import log_execution, utc_now_iso
    from runtime.orchestrator import run_state_runtime
    from runtime.state_machine import RuntimeStateMachine
    from runtime.state_store import StateStore


@dataclass
class DecisionLoopConfig:
    sleep_interval_seconds: int = 60
    heartbeat_interval_seconds: int = 300
    max_events_per_cycle: int = 5
    log_path: Optional[str] = None
    db_path: Optional[str] = None
    inbox_dir: Optional[str] = None
    llm_model: str = "gpt5.5"


class DecisionLoop:
    """Always-on event -> state -> orchestrator loop."""

    def __init__(self, config: Optional[DecisionLoopConfig] = None) -> None:
        self.config = config or DecisionLoopConfig()
        self.event_stream = EventStream(db_path=self.config.db_path, inbox_dir=self.config.inbox_dir)
        self.state_machine = RuntimeStateMachine(db_path=self.config.db_path)
        self.store = StateStore(db_path=self.config.db_path)
        self.fusion_engine = EventFusionEngine()
        self.regime_memory = RegimeMemory(db_path=self.config.db_path)
        self.state_controller = AntiOverwriteStateController()
        self._running = False
        self._last_heartbeat = 0.0

    def run_once(self) -> Dict[str, object]:
        """Run one event-loop cycle."""

        ingested = self.event_stream.listen_once()
        self._enqueue_heartbeat_if_due()
        events = self.event_stream.poll(limit=self.config.max_events_per_cycle)
        results: List[Dict[str, object]] = []

        if events:
            fusion = self.fusion_engine.fuse(events)
            previous_llm_feedback = self.store.get_state("llm_feedback_state")
            previous_structural_state = self.store.get_state("structural_coevolution_state")
            previous_self_organization_state = self.store.get_state("self_organization_state")
            previous_hypothesis_memory = self.store.get_state("causal_hypothesis_memory")
            fusion = apply_pending_feedback_to_fusion(fusion, previous_llm_feedback)
            memory_before = self.regime_memory.summary()
            causal = infer_causal_intelligence(
                fusion=fusion,
                attention_liquidity=fusion.get("attention_liquidity", {}),
                memory_summary=memory_before,
            )
            world_model = simulate_market_world_model(
                fusion=fusion,
                causal=causal,
                memory_summary=memory_before,
            )
            latent_structure = infer_latent_market_structure(
                world_model=world_model,
                causal=causal,
                memory_summary=memory_before,
            )
            physics_constraints = apply_market_physics_constraints(
                world_model=world_model,
                latent_structure=latent_structure,
                causal=causal,
                memory_summary=memory_before,
            )
            market_laws = infer_market_law_emergence(
                latent_structure=latent_structure,
                physics_constraints=physics_constraints,
                world_model=world_model,
                memory_summary=memory_before,
            )
            previous_cognition = self.store.get_state("cognition_state")
            previous_unified = {}
            if isinstance(previous_cognition, dict):
                previous_unified = previous_cognition.get("unified_intelligence", {})
            unified_intelligence = infer_unified_market_intelligence(
                fusion=fusion,
                causal=causal,
                world_model=world_model,
                latent_structure=latent_structure,
                physics_constraints=physics_constraints,
                market_laws=market_laws,
                memory_summary=memory_before,
                previous_unified_state=previous_unified if isinstance(previous_unified, dict) else {},
            )
            controller_context = dict(causal)
            controller_context["world_model"] = world_model
            controller_context["latent_structure"] = latent_structure
            controller_context["physics_constraints"] = physics_constraints
            controller_context["market_laws"] = market_laws
            controller_context["unified_intelligence"] = unified_intelligence
            previous_state = self.state_machine.current_state()
            transition = self.state_controller.decide(
                previous_state=previous_state,
                fusion=fusion,
                memory_summary=memory_before,
                causal=controller_context,
            )
            memory_after = self.regime_memory.record(
                transition["current_state"],
                fusion=fusion,
                causal=controller_context,
            )
            transition["memory_after"] = memory_after
            self.store.save_system_state(transition)
            self.store.append_state_transition(transition)
            self.store.set_state(
                "cognition_state",
                {
                    "fusion": fusion,
                    "causal": causal,
                    "world_model": world_model,
                    "latent_structure": latent_structure,
                    "physics_constraints": physics_constraints,
                    "market_laws": market_laws,
                    "unified_intelligence": unified_intelligence,
                    "controller": transition,
                    "memory": memory_after,
                    "llm_feedback": previous_llm_feedback,
                    "structural_coevolution": previous_structural_state,
                    "self_organization": previous_self_organization_state,
                },
            )
            cognition_snapshot = {
                "fusion": fusion,
                "causal": causal,
                "world_model": world_model,
                "latent_structure": latent_structure,
                "physics_constraints": physics_constraints,
                "market_laws": market_laws,
                "unified_intelligence": unified_intelligence,
                "controller": transition,
                "memory": memory_after,
                "structural_coevolution": previous_structural_state,
                "self_organization": previous_self_organization_state,
            }
            fused_event = {
                "event_id": "fusion:" + ",".join(event["event_id"] for event in events),
                "event_type": "fused_market_reality",
                "priority": max(int(event.get("priority", 0)) for event in events),
                "payload": {
                    "cognition": {
                        "fusion": fusion,
                        "causal": causal,
                        "world_model": world_model,
                        "latent_structure": latent_structure,
                        "physics_constraints": physics_constraints,
                        "market_laws": market_laws,
                        "unified_intelligence": unified_intelligence,
                        "controller": transition,
                        "memory": memory_after,
                        "structural_coevolution": previous_structural_state,
                        "self_organization": previous_self_organization_state,
                    }
                },
                "source": "event_fusion_engine",
                "created_at": utc_now_iso(),
            }
            result = run_state_runtime(
                system_state=transition["current_state"],
                event=fused_event,
                log_path=self.config.log_path,
                db_path=self.config.db_path,
                llm_model=self.config.llm_model,
            )
            for event in events:
                self.event_stream.acknowledge(event["event_id"], "handled")
            decision_packet = result.get("decision_packet", {})
            llm_feedback = run_cognitive_refinement_cycle(
                decision_packet=decision_packet if isinstance(decision_packet, dict) else {},
                cognitive_state_snapshot=cognition_snapshot,
                llm_reasoning_output=str(
                    decision_packet.get("reasoning_trace", "") if isinstance(decision_packet, dict) else ""
                ),
                previous_feedback=previous_llm_feedback if isinstance(previous_llm_feedback, dict) else {},
            )
            feedback_delta = {
                "attention": llm_feedback.get("modifiers", {}).get("attention_weight_delta"),
                "causal": llm_feedback.get("modifiers", {}).get("causal_edge_strength_delta"),
                "risk": llm_feedback.get("modifiers", {}).get("risk_confidence_delta"),
            }
            material_runtime_events = [event for event in events if _is_material_forecast_event(event)]
            runtime_forecast_outcome = (
                process_due_runtime_forecast(
                    current_state=str(transition.get("current_state") or "Unknown"),
                    current_cycle_id=str(result.get("run_id") or ""),
                    event_ids=[str(event.get("event_id")) for event in material_runtime_events],
                    db_path=self.config.db_path,
                )
                if material_runtime_events
                else {"status": "not_due", "reason": "no_real_material_observation"}
            )
            trust_score = compute_trust_score(
                cognitive_state=cognition_snapshot,
                llm_output=decision_packet if isinstance(decision_packet, dict) else {},
                feedback_delta=feedback_delta,
            )
            forecast_calibration_feedback = _forecast_calibration_feedback(
                forecast_calibration_state=self.store.get_state("forecast_calibration_state"),
                system_trust_state=self.store.get_state("system_trust_state"),
            )
            trust_score = _apply_forecast_calibration_to_trust(
                trust_score=trust_score,
                calibration_feedback=forecast_calibration_feedback,
            )
            actual_outcome_state = {
                "transition": transition,
                "controller": transition,
                "fusion": fusion,
                "memory": memory_after,
                "state": transition.get("current_state"),
            }
            explanation_error = compute_explanation_error(
                decision_explanation=decision_packet if isinstance(decision_packet, dict) else {},
                actual_outcome_state=actual_outcome_state,
                causal_graph_prediction=controller_context,
                observed_result={
                    "state": transition.get("current_state"),
                    "attention": fusion.get("attention_pressure"),
                    "liquidity": fusion.get("liquidity_score"),
                    "stress": fusion.get("stress_score"),
                    "narrative": fusion.get("narrative_intensity"),
                    "volatility": fusion.get("volatility_regime"),
                },
            )
            regime_alignment = align_regime_explanation(
                regime_label=str(transition.get("current_state", "UNKNOWN")),
                decision_explanation=decision_packet if isinstance(decision_packet, dict) else {},
                causal_model=controller_context,
                actual_outcome_state=actual_outcome_state,
            )
            previous_error_history = (
                previous_hypothesis_memory.get("explanation_error_history", [])
                if isinstance(previous_hypothesis_memory, dict)
                else []
            )
            explanation_error_history = list(previous_error_history[-8:]) + [explanation_error]
            causal_hypotheses = generate_causal_hypotheses(
                event_stream=events,
                regime_state=str(transition.get("current_state", "UNKNOWN")),
                lmse_structure=latent_structure,
                explanation_error_history=explanation_error_history,
            )
            hypothesis_scoring = score_causal_hypotheses(
                hypotheses=causal_hypotheses.get("hypotheses", []),
                explanation_error_history=explanation_error_history,
                regime_state=str(transition.get("current_state", "UNKNOWN")),
                trust_score=trust_score,
                hypothesis_memory_state=previous_hypothesis_memory if isinstance(previous_hypothesis_memory, dict) else {},
            )
            active_causal_structure = select_active_causal_structure(
                scored_hypotheses=hypothesis_scoring,
                hypotheses=causal_hypotheses.get("hypotheses", []),
                previous_selection=previous_hypothesis_memory if isinstance(previous_hypothesis_memory, dict) else {},
                trust_score=trust_score,
                regime_state=str(transition.get("current_state", "UNKNOWN")),
            )
            multi_explanation_competition = compute_multi_explanation_competition(
                explanations=[
                    {
                        "causal_summary": hypothesis.get("id"),
                        "reasoning_trace": " ".join(str(item) for item in hypothesis.get("structural_assumptions", [])),
                    }
                    for hypothesis in causal_hypotheses.get("hypotheses", [])
                    if isinstance(hypothesis, dict)
                ],
                causal_graph_variants=[
                    hypothesis.get("causal_graph_variant", {})
                    for hypothesis in causal_hypotheses.get("hypotheses", [])
                    if isinstance(hypothesis, dict)
                ],
            )
            hypothesis_memory_state = update_hypothesis_memory(
                previous_memory=previous_hypothesis_memory if isinstance(previous_hypothesis_memory, dict) else {},
                selection_state=active_causal_structure,
                scored_hypotheses=hypothesis_scoring,
                regime_state=str(transition.get("current_state", "UNKNOWN")),
                explanation_error=explanation_error,
            )
            hypothesis_memory_state["explanation_error_history"] = explanation_error_history[-12:]
            previous_explanation_feedback = (
                previous_structural_state.get("explanation_feedback", {})
                if isinstance(previous_structural_state, dict)
                else {}
            )
            causal_self_correction = apply_causal_self_correction(
                explanation_error=explanation_error,
                causal_graph=causal.get("causal_graph", {}) if isinstance(causal, dict) else {},
                trust_score=trust_score,
                regime_alignment=regime_alignment,
                previous_correction=previous_explanation_feedback.get("causal_correction", {})
                if isinstance(previous_explanation_feedback, dict)
                else {},
            )
            llm_feedback = attach_trust_weighting(llm_feedback, trust_score)
            previous_trust_state = self.store.get_state("system_trust_state")
            system_trust_state = update_system_trust_state(
                previous_state=previous_trust_state,
                trust_score=trust_score,
                provider=str(result.get("decision_packet", {}).get("provider", "runtime")),
                feedback_delta=feedback_delta,
                regime_volatility=float(fusion.get("stress_score", 0) or 0),
            )
            system_trust_state["forecast_calibration_feedback"] = forecast_calibration_feedback
            confidence_calibration = calibrate_confidence(
                (decision_packet or {}).get("confidence") if isinstance(decision_packet, dict) else 0.0,
                trust_score,
            )
            mutation_state = mutate_causal_graph(
                cil_causal_graph=causal.get("causal_graph", {}) if isinstance(causal, dict) else {},
                latent_structure=latent_structure,
                physics_constraints=physics_constraints,
                trust_score=trust_score,
                feedback_delta=feedback_delta,
                previous_graph_state=previous_structural_state.get("mutation", {})
                if isinstance(previous_structural_state, dict)
                else {},
            )
            regime_topology = evolve_regime_topology(
                latent_structure=latent_structure,
                mutation_state=mutation_state,
                trust_score=trust_score,
                feedback_delta=feedback_delta,
                previous_topology=previous_structural_state.get("regime_topology", {})
                if isinstance(previous_structural_state, dict)
                else {},
            )
            structural_coevolution_state = apply_structural_drift(
                mutated_graph=mutation_state,
                regime_topology=regime_topology,
                previous_structural_state=previous_structural_state
                if isinstance(previous_structural_state, dict)
                else {},
                trust_score=trust_score,
                explanation_correction=causal_self_correction,
            )
            self_organization_state = run_self_organization_cycle(
                cognitive_state=cognition_snapshot,
                structural_coevolution_state=structural_coevolution_state,
                system_trust_state=system_trust_state,
                trust_score=trust_score,
                feedback_delta=feedback_delta,
                previous_self_organization_state=previous_self_organization_state
                if isinstance(previous_self_organization_state, dict)
                else {},
            )
            runtime_forecast = _register_runtime_forecast(
                db_path=self.config.db_path,
                result=result,
                events=events,
                transition=transition,
                causal=causal,
                active_causal_structure=active_causal_structure,
                decision_packet=decision_packet if isinstance(decision_packet, dict) else {},
            )
            self.store.set_state("llm_feedback_state", llm_feedback)
            cognition_snapshot["llm_feedback"] = llm_feedback
            cognition_snapshot["trust_score"] = trust_score
            cognition_snapshot["forecast_calibration_feedback"] = forecast_calibration_feedback
            cognition_snapshot["explanation_error"] = explanation_error
            cognition_snapshot["regime_explanation_alignment"] = regime_alignment
            cognition_snapshot["causal_hypotheses"] = causal_hypotheses
            cognition_snapshot["hypothesis_scoring"] = hypothesis_scoring
            cognition_snapshot["active_causal_structure"] = active_causal_structure
            cognition_snapshot["multi_explanation_competition"] = multi_explanation_competition
            cognition_snapshot["hypothesis_memory"] = hypothesis_memory_state
            cognition_snapshot["causal_self_correction"] = causal_self_correction
            cognition_snapshot["system_trust_state"] = system_trust_state
            cognition_snapshot["structural_coevolution"] = structural_coevolution_state
            cognition_snapshot["self_organization"] = self_organization_state
            self.store.set_state("cognition_state", cognition_snapshot)
            self.store.set_state("system_trust_state", system_trust_state)
            self.store.set_state("structural_coevolution_state", structural_coevolution_state)
            self.store.set_state("self_organization_state", self_organization_state)
            self.store.set_state("causal_hypothesis_memory", hypothesis_memory_state)
            results.append(
                {
                    "event_ids": [event["event_id"] for event in events],
                    "event_types": [event["event_type"] for event in events],
                    "state": transition["current_state"],
                    "proposed_state": transition["proposed_state"],
                    "transition_allowed": transition["transition_allowed"],
                    "primary_driver": causal["primary_driver"],
                    "world_model_phase_transition": world_model["regime_emergence_dynamics"][
                        "phase_transition_likelihood"
                    ],
                    "latent_attractor_basin": latent_structure["regime_attractors"]["dominant_attractor_basin"],
                    "physics_stability_score": physics_constraints["system_stability_report"]["stability_score"],
                    "law_system_stability_score": market_laws["system_stability_evaluation"][
                        "law_system_stability_score"
                    ],
                    "unified_dominant_structure": unified_intelligence["unified_interpretation"][
                        "dominant_regime_structure"
                    ],
                    "unified_feedback_influence": unified_intelligence["feedback_loop_design"][
                        "feedback_influence_score"
                    ],
                    "result_status": result["status"],
                    "decision_brief_id": result["run_id"],
                    "forecast_id": runtime_forecast.get("forecast_id"),
                    "forecast_status": runtime_forecast.get("status"),
                    "forecast_registration_reason": runtime_forecast.get("reason"),
                    "forecast_outcome_id": runtime_forecast_outcome.get("forecast_id"),
                    "forecast_outcome_status": runtime_forecast_outcome.get("status"),
                    "forecast_outcome_error": runtime_forecast_outcome.get("prediction_error"),
                    "decision_packet_action": result.get("decision_packet", {}).get("recommended_action"),
                    "decision_packet_risk": result.get("decision_packet", {}).get("risk_level"),
                    "decision_packet_confidence": result.get("decision_packet", {}).get("confidence"),
                    "llm_feedback_status": llm_feedback.get("status"),
                    "llm_feedback_attention_delta": llm_feedback.get("modifiers", {}).get("attention_weight_delta"),
                    "llm_feedback_causal_delta": llm_feedback.get("modifiers", {}).get("causal_edge_strength_delta"),
                    "llm_feedback_risk_delta": llm_feedback.get("modifiers", {}).get("risk_confidence_delta"),
                    "llm_feedback_freeze": llm_feedback.get("stability", {}).get("freeze_feedback"),
                    "trust_score": trust_score,
                    "system_trust_state": system_trust_state,
                    "forecast_calibration_feedback_status": forecast_calibration_feedback.get("status"),
                    "forecast_calibration_feedback_delta": forecast_calibration_feedback.get("trust_delta"),
                    "forecast_calibration_feedback_source": forecast_calibration_feedback.get("source"),
                    "calibrated_confidence": confidence_calibration["calibrated_confidence"],
                    "confidence_adjustment_factor": confidence_calibration["confidence_adjustment_factor"],
                    "explanation_error_score": explanation_error.get("explanation_error_score"),
                    "explanation_missing_causal_links": explanation_error.get("missing_causal_links"),
                    "causal_self_correction_status": causal_self_correction.get("status"),
                    "causal_self_correction_intensity": causal_self_correction.get("correction_intensity"),
                    "causal_self_correction_edges": causal_self_correction.get("edge_weight_updates"),
                    "regime_explanation_alignment_score": regime_alignment.get("alignment_score"),
                    "regime_explanation_alignment_conflicts": regime_alignment.get("alignment_conflicts"),
                    "causal_hypothesis_count": causal_hypotheses.get("hypothesis_count"),
                    "active_causal_hypothesis_id": active_causal_structure.get("active_hypothesis_id"),
                    "causal_hypothesis_switch_allowed": active_causal_structure.get("switch_allowed"),
                    "causal_hypothesis_selection_reason": active_causal_structure.get("selection_reason"),
                    "causal_hypothesis_score_distribution": hypothesis_scoring.get("score_distribution"),
                    "causal_shadow_hypothesis_count": len(active_causal_structure.get("shadow_hypotheses", [])),
                    "explanation_divergence_index": multi_explanation_competition.get("explanation_divergence_index"),
                    "causal_conflict_score": multi_explanation_competition.get("causal_conflict_score"),
                    "model_instability_pressure": multi_explanation_competition.get("model_instability_pressure"),
                    "structural_coevolution_status": structural_coevolution_state.get("status"),
                    "structural_mutation_intensity": mutation_state.get("mutation_intensity"),
                    "structural_shift_index": mutation_state.get("structural_shift_index"),
                    "regime_basin_deformation": regime_topology.get("basin_deformation"),
                    "structural_trust_gate": structural_coevolution_state.get("trust_gate"),
                    "self_organization_status": self_organization_state.get("status"),
                    "self_organization_shift_index": self_organization_state.get("structural_shift_index"),
                    "self_organization_regime_attractor_shift": self_organization_state.get("regime_attractor_shift"),
                    "trust_field_evolution": self_organization_state.get("trust_field_evolution"),
                    "self_organization_trust_gate": self_organization_state.get("trust_gate"),
                }
            )

        cycle_record = {
            "timestamp": utc_now_iso(),
            "trigger_type": "decision_loop_cycle",
            "events_ingested": ingested,
            "events_processed": len(results),
            "raw_events_processed": len(events),
            "results": results,
            "status": "success",
        }
        log_execution(cycle_record, log_path=self.config.log_path)
        self.store.append_system_log(cycle_record)
        return cycle_record

    def run_forever(self, max_cycles: Optional[int] = None) -> None:
        """Run until stopped or max_cycles is reached."""

        self._running = True
        cycles = 0
        while self._running:
            self.run_once()
            cycles += 1
            if max_cycles is not None and cycles >= max_cycles:
                break
            time.sleep(self.config.sleep_interval_seconds)

    def stop(self, *_args: object) -> None:
        self._running = False

    def _enqueue_heartbeat_if_due(self) -> None:
        now = time.time()
        if now - self._last_heartbeat < self.config.heartbeat_interval_seconds:
            return
        self.event_stream.enqueue_event(
            EVENT_HEARTBEAT,
            payload={"heartbeat_at": utc_now_iso()},
            source="decision_loop",
        )
        self._last_heartbeat = now


def _forecast_calibration_feedback(
    *,
    forecast_calibration_state: Dict[str, Any],
    system_trust_state: Dict[str, Any],
) -> Dict[str, Any]:
    calibration = forecast_calibration_state if isinstance(forecast_calibration_state, dict) else {}
    trust = system_trust_state if isinstance(system_trust_state, dict) else {}
    latest = trust.get("latest_forecast_calibration", {})
    latest = latest if isinstance(latest, dict) else {}
    evaluated = _safe_int(calibration.get("evaluated_count"), 0)
    if evaluated <= 0 and not latest:
        return {
            "status": "not_available",
            "trust_delta": 0.0,
            "source": "no_forecast_outcomes",
            "behavioral_influence": False,
        }

    mean_error = _safe_float(calibration.get("mean_forecast_error"), 0.0)
    last_status = str(calibration.get("last_status") or latest.get("status") or "UNKNOWN").upper()
    if last_status == "INVALIDATED":
        delta = -min(0.12, 0.04 + mean_error * 0.08)
    elif last_status == "INCONCLUSIVE":
        delta = -min(0.05, 0.02 + mean_error * 0.04)
    elif last_status == "VERIFIED" and mean_error <= 0.35:
        delta = min(0.04, 0.01 + (1.0 - mean_error) * 0.025)
    else:
        delta = -min(0.03, mean_error * 0.03)
    return {
        "status": "applied",
        "trust_delta": round(delta, 4),
        "source": "forecast_calibration_state",
        "last_status": last_status,
        "mean_forecast_error": round(mean_error, 4),
        "evaluated_count": evaluated,
        "behavioral_influence": True,
        "bounded": True,
    }


def _apply_forecast_calibration_to_trust(
    *,
    trust_score: Dict[str, float],
    calibration_feedback: Dict[str, Any],
) -> Dict[str, float]:
    adjusted = dict(trust_score)
    delta = _safe_float(calibration_feedback.get("trust_delta"), 0.0)
    if not calibration_feedback.get("behavioral_influence"):
        adjusted["forecast_calibration_adjustment"] = 0.0
        return adjusted
    for key in (
        "llm_trust",
        "cognitive_trust",
        "regime_stability_trust",
        "feedback_consistency_trust",
        "global_trust_index",
    ):
        adjusted[key] = round(max(0.0, min(1.0, _safe_float(adjusted.get(key), 0.5) + delta)), 4)
    adjusted["forecast_calibration_adjustment"] = round(delta, 4)
    return adjusted


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _register_runtime_forecast(
    *,
    db_path: Optional[str],
    result: Dict[str, Any],
    events: List[Dict[str, object]],
    transition: Dict[str, Any],
    causal: Dict[str, Any],
    active_causal_structure: Dict[str, Any],
    decision_packet: Dict[str, Any],
) -> Dict[str, Any]:
    """Register a non-binding structural forecast for runtime accountability."""

    run_id = str(result.get("run_id") or "")
    if not run_id:
        return {"status": "skipped", "error": "missing_run_id"}
    material_events = [event for event in events if _is_material_forecast_event(event)]
    if not material_events:
        return {"status": "skipped", "reason": "no_material_event"}
    drivers = []
    primary = causal.get("primary_driver")
    if primary:
        drivers.append(str(primary))
    attention = causal.get("attention_meaning")
    if attention:
        drivers.append(str(attention))
    expected_state = str(transition.get("proposed_state") or transition.get("current_state") or "Unknown")
    active_hypothesis = str(active_causal_structure.get("active_hypothesis_id") or "Unknown")
    signature = _material_forecast_signature(
        expected_state=expected_state,
        active_hypothesis=active_hypothesis,
        drivers=drivers,
        event_types=[str(event.get("event_type")) for event in material_events],
    )
    previous = latest_forecast(subject="runtime_market_structure", db_path=db_path)
    if previous and str(previous.get("material_signature") or "") == signature:
        return {
            "status": "skipped",
            "reason": "unchanged_material_signature",
            "forecast_id": previous.get("forecast_id"),
            "material_signature": signature,
        }
    forecast = create_forecast(
        {
            "forecast_id": f"runtime-{run_id}",
            "horizon": "next_runtime_cycle",
            "subject": "runtime_market_structure",
            "forecast_statement": (
                "Non-binding structural runtime forecast: current causal structure remains coherent "
                "until contradicted by later observed state."
            ),
            "expected_direction_state": expected_state,
            "confidence": _safe_float(decision_packet.get("confidence"), 0.0)
            if isinstance(decision_packet, dict)
            else 0.0,
            "active_hypothesis": active_hypothesis,
            "causal_drivers": drivers,
            "invalidation_conditions": [
                "later_runtime_state_conflicts_with_expected_structure",
                "forecast_outcome_marked_invalidated_through_supported_lifecycle",
            ],
            "expected_observation_window": "next_runtime_cycle_or_user_supported_evaluation",
            "runtime_lineage": {
                "cycle_type": "decision_loop_cycle",
                "event_ids": [str(event.get("event_id")) for event in material_events],
                "event_types": [str(event.get("event_type")) for event in material_events],
                "decision_brief_id": result.get("run_id"),
                "system_state": transition.get("current_state"),
                "proposed_state": transition.get("proposed_state"),
            },
            "material_signature": signature,
            "material_reason": "material_event_or_structure_change",
        },
        db_path=db_path,
    )
    return {
        "status": forecast.get("status"),
        "forecast_id": forecast.get("forecast_id"),
        "runtime_lineage": forecast.get("runtime_lineage", {}),
        "reason": "created_material_forecast",
        "material_signature": signature,
    }


def _is_material_forecast_event(event: Dict[str, object]) -> bool:
    event_type = str(event.get("event_type") or "")
    source = str(event.get("source") or "")
    payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
    if event_type == EVENT_HEARTBEAT or source in {"proactive_update", "simulated", "controlled_fixture"}:
        return False
    if isinstance(payload, dict) and payload.get("update_kind") == "proactive_context_refresh":
        return False
    return bool(event_type)


def _material_forecast_signature(
    *,
    expected_state: str,
    active_hypothesis: str,
    drivers: List[str],
    event_types: List[str],
) -> str:
    identity = "|".join(
        [
            expected_state.strip().upper(),
            active_hypothesis.strip().upper(),
            *sorted({item.strip().lower() for item in drivers if item.strip()}),
            *sorted({item.strip().lower() for item in event_types if item.strip()}),
        ]
    )
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()[:24]
