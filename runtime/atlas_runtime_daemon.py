"""Atlas OS macOS background runtime daemon v0.1.

Run:

    python3 runtime/atlas_runtime_daemon.py

Background mode:

    nohup python3 runtime/atlas_runtime_daemon.py &

This daemon only runs runtime infrastructure. It does not trade, connect to
brokers, change CDE logic, or modify the cognitive architecture.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

_RUNTIME_DIR = Path(__file__).resolve().parent
if sys.path and Path(sys.path[0]).resolve() == _RUNTIME_DIR:
    sys.path.pop(0)
_ROOT_DIR = _RUNTIME_DIR.parent
if str(_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(_ROOT_DIR))

try:
    from runtime.daily_cycle import dispatch_current_daily_cycle
    from runtime.decision_loop import DecisionLoop, DecisionLoopConfig
    from runtime.event_source import SimulatedMarketEventSource, event_to_runtime_event
    from runtime.logging import utc_now_iso
    from runtime.market_intelligence import refresh_market_intelligence
    from runtime.forecast_ledger import list_forecasts
    from runtime.output_logger import RuntimeOutputLogger
    from runtime.portfolio_context import build_portfolio_context
    from runtime.proactive_update import DEFAULT_PROACTIVE_UPDATE_SECONDS, build_proactive_update_plan, skipped_proactive_update_state
    from runtime.scheduler import RuntimeScheduleConfig, next_run_time
    from runtime.state_store import StateStore
    from runtime.telemetry.decision_trace_logger import log_decision_trace
    from runtime.telemetry.state_snapshot import capture_cognitive_snapshot
except ModuleNotFoundError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from runtime.daily_cycle import dispatch_current_daily_cycle
    from runtime.decision_loop import DecisionLoop, DecisionLoopConfig
    from runtime.event_source import SimulatedMarketEventSource, event_to_runtime_event
    from runtime.logging import utc_now_iso
    from runtime.market_intelligence import refresh_market_intelligence
    from runtime.forecast_ledger import list_forecasts
    from runtime.output_logger import RuntimeOutputLogger
    from runtime.portfolio_context import build_portfolio_context
    from runtime.proactive_update import DEFAULT_PROACTIVE_UPDATE_SECONDS, build_proactive_update_plan, skipped_proactive_update_state
    from runtime.scheduler import RuntimeScheduleConfig, next_run_time
    from runtime.state_store import StateStore
    from runtime.telemetry.decision_trace_logger import log_decision_trace
    from runtime.telemetry.state_snapshot import capture_cognitive_snapshot


@dataclass
class AtlasRuntimeDaemonConfig:
    interval_seconds: int = 60
    max_cycles: Optional[int] = None
    log_path: Optional[str] = None
    db_path: Optional[str] = None
    inbox_dir: Optional[str] = None
    ui_inbox_path: Optional[str] = None
    llm_model: str = "gpt5.5"
    max_events_per_cycle: int = 10
    no_sleep: bool = False
    market_refresh_enabled: bool = True
    market_refresh_every_cycles: int = 5
    market_config_path: Optional[str] = None
    market_max_assets: int = 12
    daily_cycle_now: Optional[str] = None
    proactive_update_enabled: bool = True
    proactive_update_every_seconds: int = DEFAULT_PROACTIVE_UPDATE_SECONDS
    proactive_update_run_on_start: bool = True
    runtime_mode: str = "auto"
    cognition_mode: str = "auto"


class AtlasRuntimeDaemon:
    """Continuously generate/fetch events and run Atlas cognition ticks."""

    def __init__(
        self,
        config: Optional[AtlasRuntimeDaemonConfig] = None,
        event_source: Optional[Any] = None,
    ) -> None:
        self.config = config or AtlasRuntimeDaemonConfig()
        self.schedule = RuntimeScheduleConfig(interval_seconds=self.config.interval_seconds)
        self.runtime_mode = _resolve_runtime_mode(self.config.runtime_mode, self.config.market_config_path)
        self.cognition_mode = _resolve_cognition_mode(self.config.cognition_mode, self.config.market_config_path)
        self.event_source = event_source if event_source is not None else (SimulatedMarketEventSource() if self.runtime_mode == "simulation" else None)
        self.output_logger = RuntimeOutputLogger(log_path=self.config.log_path)
        self.store = StateStore(db_path=self.config.db_path)
        self.ui_inbox_path = Path(self.config.ui_inbox_path or "runtime/inbox/user_event.jsonl")
        self.loop = DecisionLoop(
            DecisionLoopConfig(
                sleep_interval_seconds=self.schedule.interval_seconds,
                heartbeat_interval_seconds=300,
                max_events_per_cycle=self.config.max_events_per_cycle,
                log_path=None,
                db_path=self.config.db_path,
                inbox_dir=self.config.inbox_dir,
                llm_model=self.config.llm_model,
                cognition_mode=self.cognition_mode,
            )
        )
        self._running = False
        self._stop_event = threading.Event()

    def run_tick(self, tick_index: int) -> Dict[str, Any]:
        """Run one isolated daemon tick and always return a loggable record."""

        started = time.time()
        raw_event: Dict[str, Any] = {}
        runtime_event: Dict[str, Any] = {}
        status = "success"
        error = None
        cycle: Dict[str, Any] = {}
        ui_events_ingested = 0
        portfolio_change: Dict[str, Any] = {}
        market_refresh: Dict[str, Any] = {}
        proactive_update: Dict[str, Any] = {}
        daily_cycle: Dict[str, Any] = {}
        brief_update: Dict[str, Any] = {}

        try:
            ui_events_ingested = self._ingest_ui_inbox_events()
            portfolio_change = self._enqueue_portfolio_change_if_needed()
            market_refresh = self._refresh_market_if_due(tick_index)
            daily_cycle = self._daily_cycle_status()
            proactive_update = self._proactive_update_if_due(tick_index, market_refresh, daily_cycle)
            if self.event_source is not None:
                raw_event = self.event_source.get_event()
                runtime_event = event_to_runtime_event(raw_event)
                self.loop.event_stream.enqueue_event(
                    runtime_event["event_type"],
                    payload=runtime_event["payload"],
                    priority=runtime_event["priority"],
                    source=runtime_event["source"],
                    created_at=runtime_event["created_at"],
                )
            cycle = self.loop.run_once()
            proactive_update = self._finalize_proactive_update(proactive_update, cycle)
            brief_update = self._publish_brief_state_if_changed(
                cycle=cycle,
                market_refresh=market_refresh,
                proactive_update=proactive_update,
                ui_events_ingested=ui_events_ingested,
            )
        except Exception as exc:  # Keep daemon alive across single-tick failures.
            status = "failure"
            error = str(exc)

        entry = self._build_log_entry(
            tick_index=tick_index,
            raw_event=raw_event,
            runtime_event=runtime_event,
            cycle=cycle,
            status=status,
            error=error,
            duration_ms=int((time.time() - started) * 1000),
            ui_events_ingested=ui_events_ingested,
            market_refresh=market_refresh,
            proactive_update=proactive_update,
            daily_cycle=daily_cycle,
            brief_update=brief_update,
            portfolio_change=portfolio_change,
        )
        self._write_telemetry(tick_index, entry)
        self.output_logger.log_tick(entry)
        return entry

    def run_forever(self) -> None:
        self._running = True
        self._stop_event.clear()
        tick_index = 0
        while self._running:
            self.run_tick(tick_index)
            tick_index += 1
            if self.config.max_cycles is not None and tick_index >= self.config.max_cycles:
                break
            if not self.config.no_sleep:
                if self._stop_event.wait(self.schedule.interval_seconds):
                    break

    def stop(self, *_args: object) -> None:
        self._running = False
        self._stop_event.set()

    def _build_log_entry(
        self,
        *,
        tick_index: int,
        raw_event: Dict[str, Any],
        runtime_event: Dict[str, Any],
        cycle: Dict[str, Any],
        status: str,
        error: Optional[str],
        duration_ms: int,
        ui_events_ingested: int = 0,
        market_refresh: Optional[Dict[str, Any]] = None,
        proactive_update: Optional[Dict[str, Any]] = None,
        daily_cycle: Optional[Dict[str, Any]] = None,
        brief_update: Optional[Dict[str, Any]] = None,
        portfolio_change: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        cognition = self.store.get_state("cognition_state")
        latest_brief = self.store.get_latest_decision_brief()
        system_state = self.store.get_system_state()
        result = (cycle.get("results") or [{}])[0] if isinstance(cycle.get("results"), list) else {}
        return {
            "timestamp": utc_now_iso(),
            "event": {
                "raw": raw_event,
                "runtime_event_type": runtime_event.get("event_type"),
                "runtime_priority": runtime_event.get("priority"),
                "source": runtime_event.get("source"),
            },
            "cognition_summary": {
                "fusion": _select(cognition.get("fusion", {}), ["proposed_state", "attention_pressure", "liquidity_score", "stress_score"]),
                "causal": _select(cognition.get("causal", {}), ["primary_driver", "attention_meaning", "regime_transition_probability"]),
                "unified": _select(
                    cognition.get("unified_intelligence", {}).get("unified_interpretation", {}),
                    ["dominant_regime_structure", "feedback_influence_score"],
                ),
                "tick_result": _select(
                    result,
                    [
                        "state",
                        "proposed_state",
                        "transition_allowed",
                        "decision_brief_id",
                        "brief_published",
                        "forecast_id",
                        "forecast_status",
                        "result_status",
                        "decision_packet_action",
                        "decision_packet_risk",
                        "decision_packet_confidence",
                        "trust_score",
                        "forecast_calibration_feedback_status",
                        "forecast_calibration_feedback_delta",
                        "forecast_calibration_feedback_source",
                        "active_causal_hypothesis_id",
                        "causal_hypothesis_score_distribution",
                        "llm_feedback_status",
                        "llm_feedback_attention_delta",
                        "llm_feedback_causal_delta",
                        "llm_feedback_risk_delta",
                        "llm_feedback_freeze",
                        "structural_coevolution_status",
                        "structural_mutation_intensity",
                        "structural_shift_index",
                        "regime_basin_deformation",
                        "structural_trust_gate",
                        "self_organization_status",
                        "self_organization_shift_index",
                        "self_organization_regime_attractor_shift",
                        "trust_field_evolution",
                        "self_organization_trust_gate",
                    ],
                ),
            },
            "regime_state": {
                "system_state": system_state.get("current_state", "Unknown"),
                "proposed_state": system_state.get("proposed_state", "Unknown"),
                "transition_allowed": system_state.get("transition_allowed"),
            },
            "decision_brief": {
                "id": latest_brief.get("id"),
                "trigger_type": latest_brief.get("trigger_type"),
                "event_type": latest_brief.get("event_type"),
                "available": bool(latest_brief.get("content")),
                "decision_packet": latest_brief.get("metadata", {}).get("decision_packet", {}),
            },
            "system_metrics": {
                "tick_index": tick_index,
                "status": status,
                "error": error,
                "duration_ms": duration_ms,
                "events_processed": cycle.get("raw_events_processed", 0),
                "ui_events_ingested": int(ui_events_ingested),
                "portfolio_change_status": (portfolio_change or {}).get("status", "not_checked"),
                "market_refresh_status": (market_refresh or {}).get("status", "not_run"),
                "market_events_enqueued": int((market_refresh or {}).get("events_enqueued", 0) or 0),
                "market_channels": (market_refresh or {}).get("channels", {}),
                "proactive_update_status": (proactive_update or {}).get("status", "not_run"),
                "proactive_update_cycle_id": (proactive_update or {}).get("update_cycle_id"),
                "proactive_update_focus": (proactive_update or {}).get("research_focus", []),
                "proactive_update_next_due_at": (proactive_update or {}).get("next_due_at"),
                "daily_cycle": daily_cycle or {},
                "brief_update_status": (brief_update or {}).get("status", "not_run"),
                "brief_revision": (brief_update or {}).get("brief_revision"),
                "brief_changed_sections": (brief_update or {}).get("changed_sections", []),
                "next_run_time": next_run_time(self.schedule).isoformat(),
                "no_trading_execution": True,
            },
        }

    def _refresh_market_if_due(self, tick_index: int) -> Dict[str, Any]:
        """Optionally enqueue normalized market observations through EventStream."""

        if not self.config.market_refresh_enabled:
            return {"status": "disabled"}
        cadence = max(1, int(self.config.market_refresh_every_cycles or 1))
        if tick_index % cadence != 0:
            return {"status": "skipped_until_next_cadence", "cadence_cycles": cadence}
        result = refresh_market_intelligence(
            config_path=self.config.market_config_path,
            db_path=self.config.db_path,
            enqueue=True,
            max_assets=max(1, int(self.config.market_max_assets or 1)),
        )
        self.store.set_state("market_intelligence_state", result)
        return result

    def _enqueue_portfolio_change_if_needed(self) -> Dict[str, Any]:
        """Convert a safe local portfolio-context change into a next-tick runtime event."""

        portfolio = build_portfolio_context(config_path=self.config.market_config_path)
        safe_context = _portfolio_brief_input(portfolio)
        signature = _stable_digest(safe_context)
        previous = self.store.get_state("portfolio_runtime_watch_state")
        if not previous:
            self.store.set_state(
                "portfolio_runtime_watch_state",
                {"signature": signature, "established_at": utc_now_iso()},
            )
            return {"status": "baseline_established", "event_enqueued": False}
        if previous.get("signature") == signature:
            return {"status": "unchanged", "event_enqueued": False}
        event_id = self.loop.event_stream.enqueue_event(
            "portfolio_context_changed",
            payload={
                "portfolio_context": safe_context,
                "change_kind": "local_portfolio_configuration",
                "private_amounts_included": False,
                "no_trading_execution": True,
            },
            priority=70,
            source="local_portfolio_config",
            created_at=utc_now_iso(),
        )
        self.store.set_state(
            "portfolio_runtime_watch_state",
            {"signature": signature, "changed_at": utc_now_iso(), "event_id": event_id},
        )
        return {"status": "changed", "event_enqueued": True, "event_id": event_id}

    def _daily_cycle_status(self) -> Dict[str, Any]:
        result = dispatch_current_daily_cycle(
            db_path=self.config.db_path,
            config_path=self.config.market_config_path,
            now=_parse_datetime(self.config.daily_cycle_now),
        )
        self.store.set_state("daily_cycle_state", result)
        return result

    def _proactive_update_if_due(
        self,
        tick_index: int,
        market_refresh: Dict[str, Any],
        daily_cycle_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Plan and enqueue a read-only proactive context refresh when due."""

        cadence = max(60, int(self.config.proactive_update_every_seconds or DEFAULT_PROACTIVE_UPDATE_SECONDS))
        if not self.config.proactive_update_enabled:
            return {"status": "disabled", "cadence_seconds": cadence}
        previous = self.store.get_state("proactive_update_state")
        now_epoch = time.time()
        last_epoch = _float(previous.get("last_run_epoch"), 0.0)
        due = tick_index == 0 and self.config.proactive_update_run_on_start
        due = due or not last_epoch or now_epoch - last_epoch >= cadence
        next_due_at = _epoch_iso((last_epoch or now_epoch) + cadence)
        if not due:
            return skipped_proactive_update_state(
                cadence_seconds=cadence,
                last_run_at=previous.get("timestamp"),
                next_due_at=next_due_at,
            )
        market_state = market_refresh if market_refresh else self.store.get_state("market_intelligence_state")
        plan = build_proactive_update_plan(
            config_path=self.config.market_config_path,
            market_state=market_state,
            daily_cycle_state=daily_cycle_state,
            cadence_seconds=cadence,
        )
        self.loop.event_stream.enqueue_event(
            "market_event",
            payload=plan.get("event_payload", {}),
            priority=55,
            source="proactive_update",
            created_at=plan.get("timestamp"),
        )
        plan["event_enqueued"] = True
        plan["last_run_epoch"] = now_epoch
        plan["next_due_at"] = _epoch_iso(now_epoch + cadence)
        self.store.set_state("proactive_update_state", plan)
        return plan

    def _finalize_proactive_update(
        self,
        proactive_update: Dict[str, Any],
        cycle: Dict[str, Any],
    ) -> Dict[str, Any]:
        if proactive_update.get("status") != "planned":
            return proactive_update
        results = cycle.get("results", []) if isinstance(cycle.get("results"), list) else []
        result = results[0] if results and isinstance(results[0], dict) else {}
        tasks = result.get("llm_tasks", {}) if isinstance(result.get("llm_tasks"), dict) else {}
        completed_at = utc_now_iso()
        role_results = {
            role: {
                "status": (tasks.get(role) or {}).get("status", "not_called"),
                "route_status": (tasks.get(role) or {}).get("route_status", "unknown"),
                "provider": (tasks.get(role) or {}).get("provider", "unknown"),
                "model": (tasks.get(role) or {}).get("model", "unknown"),
                "latency_ms": (tasks.get(role) or {}).get("latency_ms", 0),
                "cache_status": (tasks.get(role) or {}).get("cache_status", "unknown"),
                "executed_at": completed_at,
            }
            for role in ("workhorse", "research", "decision")
        }
        statuses = {item["status"] for item in role_results.values()}
        if not result:
            status = "FAILED"
            error = cycle.get("skip_reason") or cycle.get("status") or "no_runtime_result"
        elif role_results["research"]["status"] in {"ok", "cached"} and role_results["decision"]["status"] in {
            "ok",
            "validated_decision_packet",
        }:
            status = "COMPLETED"
            error = ""
        elif statuses <= {"not_called", "unknown"}:
            status = "FAILED"
            error = "all_task_roles_unavailable"
        else:
            status = "DEGRADED"
            error = ",".join(sorted(statuses))
        finalized = {
            **proactive_update,
            "status": status,
            "completed_at": completed_at,
            "role_results": role_results,
            "decision_brief_id": result.get("decision_brief_id"),
            "brief_published": bool(result.get("brief_published")),
            "error": str(error)[:240],
        }
        self.store.set_state("proactive_update_state", finalized)
        return finalized

    def _publish_brief_state_if_changed(
        self,
        *,
        cycle: Dict[str, Any],
        market_refresh: Dict[str, Any],
        proactive_update: Dict[str, Any],
        ui_events_ingested: int,
    ) -> Dict[str, Any]:
        if str(os.environ.get("ATLAS_CONTINUOUS_BRIEF_ENABLED", "1")).strip().lower() in {"0", "false", "no"}:
            return {"status": "disabled", "changed_sections": []}
        market = market_refresh if market_refresh.get("status") == "ok" else self.store.get_state("market_intelligence_state")
        portfolio = build_portfolio_context(config_path=self.config.market_config_path)
        latest_brief = self.store.get_latest_decision_brief()
        metadata = latest_brief.get("metadata", {}) if isinstance(latest_brief, dict) else {}
        packet = metadata.get("decision_packet", {}) if isinstance(metadata, dict) else {}
        packet = packet if isinstance(packet, dict) else {}
        forecasts = list_forecasts(db_path=self.config.db_path, limit=1)
        previous = self.store.get_state("current_brief_state")
        previous_assessments = self.store.get_state("evidence_assessment_state")
        cycle_status = str(cycle.get("status") or "")
        has_runtime_delta = cycle_status not in {"", "skipped_no_material_delta"}
        has_market_refresh = market_refresh.get("status") == "ok"
        has_proactive_result = proactive_update.get("status") in {"COMPLETED", "DEGRADED", "FAILED"}
        duplicate_market_batch = cycle.get("skip_reason") == "duplicate_material_batch"
        if not previous and not (has_runtime_delta or has_market_refresh or has_proactive_result or ui_events_ingested):
            return {"status": "awaiting_material_event", "brief_revision": 0, "changed_sections": []}
        if previous and duplicate_market_batch and not (has_proactive_result or ui_events_ingested):
            return {
                "status": "no_material_delta",
                "brief_revision": previous.get("brief_revision", 0),
                "changed_sections": [],
            }
        if previous and not (has_runtime_delta or has_market_refresh or has_proactive_result or ui_events_ingested):
            return {
                "status": "no_material_delta",
                "brief_revision": previous.get("brief_revision", 0),
                "changed_sections": [],
            }
        task_state = self.store.get_state("llm_task_runtime_state")
        research_state = task_state.get("research", {}) if isinstance(task_state.get("research"), dict) else {}
        decision_signature = _decision_signature(packet)
        assessments = _assess_market_evidence(
            market=market,
            portfolio=portfolio,
            research_state=research_state,
            decision_signature=decision_signature,
            previous=previous,
            previous_assessments=previous_assessments,
        )
        candidate_overlay = _candidate_runtime_overlay(assessments)
        self.store.set_state("evidence_assessment_state", assessments)
        self.store.set_state("candidate_runtime_overlay", candidate_overlay)
        section_inputs = {
            "portfolio_state": _portfolio_brief_input(portfolio),
            "action_review": {"packet": _decision_brief_input(packet), "portfolio": _portfolio_brief_input(portfolio)},
            "core_judgment": {"packet": _decision_brief_input(packet), "assessments": assessments.get("summary", {})},
            "material_changes": {"evidence": _market_evidence_digest(market), "assessments": assessments.get("items", {})},
            "scenario_outlook": {"packet": _decision_brief_input(packet), "metrics": forecasts.get("metrics", {})},
            "candidate_delta": candidate_overlay,
            "data_freshness": _market_freshness_digest(market),
        }
        now = utc_now_iso()
        previous_sections = previous.get("sections", {}) if isinstance(previous.get("sections"), dict) else {}
        sections: Dict[str, Any] = {}
        changed: list[str] = []
        for name, value in section_inputs.items():
            content_hash = _stable_digest(value)
            old = previous_sections.get(name, {}) if isinstance(previous_sections.get(name), dict) else {}
            if old.get("content_hash") != content_hash:
                changed.append(name)
                sections[name] = {
                    "revision": int(old.get("revision", 0) or 0) + 1,
                    "updated_at": now,
                    "content_hash": content_hash,
                    "reason": _brief_update_reason(name, proactive_update, ui_events_ingested),
                    "source_ids": _section_source_ids(name, market, cycle),
                }
            else:
                sections[name] = old
        if not changed:
            return {
                "status": "no_material_delta",
                "brief_revision": previous.get("brief_revision", 0),
                "changed_sections": [],
            }
        results = cycle.get("results", []) if isinstance(cycle.get("results"), list) else []
        event_ids = [
            str(event_id)
            for result in results
            if isinstance(result, dict)
            for event_id in result.get("event_ids", [])
        ]
        state = {
            "brief_revision": int(previous.get("brief_revision", 0) or 0) + 1,
            "published_at": now,
            "trigger_ids": event_ids[:20],
            "trigger_reason": _brief_update_reason("brief", proactive_update, ui_events_ingested),
            "changed_sections": changed,
            "sections": sections,
            "decision_brief_id": latest_brief.get("id"),
            "decision_signature": decision_signature,
            "review_summary": assessments.get("summary", {}),
            "no_trading_execution": True,
        }
        if previous:
            self.store.set_state("previous_brief_state", previous)
        self.store.set_state("current_brief_state", state)
        return {"status": "published", **state}

    def _ingest_ui_inbox_events(self) -> int:
        """Ingest UI server JSONL events without calling cognition directly."""

        path = self.ui_inbox_path
        if not path.exists():
            return 0
        lines = path.read_text(encoding="utf-8").splitlines()
        count = 0
        for line in lines:
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(item, dict):
                continue
            if item.get("type") != "user_query":
                continue
            content = str(item.get("content", "")).replace("\x00", " ").strip()
            if not content:
                continue
            self.loop.event_stream.enqueue_event(
                "user_input_event",
                payload={
                    "query": content[:2000],
                    "ui_event": {
                        "timestamp": item.get("timestamp"),
                        "type": item.get("type"),
                        "source": item.get("source", "ui_chat"),
                    },
                    "interface": "ui_runtime_server",
                    "read_only_request": True,
                },
                priority=60,
                source=str(item.get("source", "ui_chat")),
                created_at=item.get("timestamp"),
            )
            count += 1
        if count:
            path.write_text("", encoding="utf-8")
        return count

    def _write_telemetry(self, tick_index: int, entry: Dict[str, Any]) -> None:
        try:
            tick_result = entry.get("cognition_summary", {}).get("tick_result", {})
            if not tick_result or not tick_result.get("brief_published"):
                return
            decision_packet = entry.get("decision_brief", {}).get("decision_packet", {})
            log_decision_trace(
                tick=tick_index,
                event=entry.get("event", {}).get("raw", {}),
                regime_state=entry.get("regime_state", {}).get("system_state", "Unknown"),
                attention_state=entry.get("cognition_summary", {}).get("fusion", {}).get("attention_pressure"),
                causal_summary=entry.get("cognition_summary", {}).get("causal", {}).get("primary_driver", "Unknown"),
                llm_decision_packet=decision_packet if isinstance(decision_packet, dict) else {},
                feedback_delta={
                    "attention": tick_result.get("llm_feedback_attention_delta"),
                    "causal": tick_result.get("llm_feedback_causal_delta"),
                    "risk": tick_result.get("llm_feedback_risk_delta"),
                },
            )
            capture_cognitive_snapshot(
                tick=tick_index,
                event=entry.get("event", {}).get("raw", {}),
                db_path=self.config.db_path,
                extra={
                    "runtime_status": entry.get("system_metrics", {}).get("status"),
                    "decision_brief_id": entry.get("decision_brief", {}).get("id"),
                    "market_refresh_status": entry.get("system_metrics", {}).get("market_refresh_status"),
                    "proactive_update_status": entry.get("system_metrics", {}).get("proactive_update_status"),
                },
            )
        except Exception as exc:
            entry.setdefault("telemetry", {})["status"] = "error"
            entry.setdefault("telemetry", {})["error"] = str(exc)


def _decision_signature(packet: Dict[str, Any]) -> str:
    confidence = _float(packet.get("confidence"), 0.0)
    return _stable_digest(
        {
            "regime_state": str(packet.get("regime_state") or "Unknown").split("/")[0].strip(),
            "recommended_action": packet.get("recommended_action"),
            "risk_level": packet.get("risk_level"),
            "confidence_band": round(confidence, 1),
        }
    )


def _decision_brief_input(packet: Dict[str, Any]) -> Dict[str, Any]:
    return {
        key: packet.get(key)
        for key in (
            "regime_state",
            "recommended_action",
            "risk_level",
            "confidence",
            "attention_state",
            "liquidity_state",
            "causal_summary",
        )
    }


def _portfolio_brief_input(portfolio: Dict[str, Any]) -> Dict[str, Any]:
    positions = portfolio.get("positions", []) if isinstance(portfolio.get("positions"), list) else []
    return {
        "status": portfolio.get("status"),
        "portfolio_consistency": portfolio.get("portfolio_consistency"),
        "exposure_sum_pct": portfolio.get("exposure_sum_pct"),
        "cash_or_unassigned_pct": portfolio.get("cash_or_unassigned_pct"),
        "positions": [
            {
                "asset": item.get("asset"),
                "market": item.get("market"),
                "portfolio_percentage": item.get("portfolio_percentage"),
                "theme": item.get("theme"),
                "role": item.get("role"),
            }
            for item in positions
            if isinstance(item, dict)
        ],
    }


def _market_evidence_digest(market: Dict[str, Any]) -> list[Dict[str, Any]]:
    evidence = market.get("evidence_items", []) if isinstance(market.get("evidence_items"), list) else []
    observations = market.get("observations", []) if isinstance(market.get("observations"), list) else []
    result = [
        {
            "evidence_id": item.get("evidence_id"),
            "headline": item.get("headline"),
            "freshness": item.get("freshness"),
            "channel": item.get("channel"),
            "affected_assets": item.get("affected_assets", []),
            "affected_themes": item.get("affected_themes", []),
        }
        for item in evidence
        if isinstance(item, dict)
    ]
    result.extend(
        {
            "asset": item.get("asset"),
            "latest_price": item.get("latest_price"),
            "daily_change_pct": item.get("daily_change_pct"),
            "change_5d_pct": item.get("change_5d_pct"),
            "change_20d_pct": item.get("change_20d_pct"),
            "freshness": item.get("freshness"),
            "data_quality_status": item.get("data_quality_status"),
        }
        for item in observations
        if isinstance(item, dict)
    )
    return result


def _market_freshness_digest(market: Dict[str, Any]) -> Dict[str, Any]:
    observations = market.get("observations", []) if isinstance(market.get("observations"), list) else []
    return {
        "status": market.get("status"),
        "channels": market.get("channels", {}),
        "observations": [
            {
                "asset": item.get("asset"),
                "freshness": item.get("freshness"),
                "latest_timestamp": item.get("latest_timestamp") or item.get("timestamp"),
                "data_quality_status": item.get("data_quality_status"),
            }
            for item in observations
            if isinstance(item, dict)
        ],
    }


def _assess_market_evidence(
    *,
    market: Dict[str, Any],
    portfolio: Dict[str, Any],
    research_state: Dict[str, Any],
    decision_signature: str,
    previous: Dict[str, Any],
    previous_assessments: Dict[str, Any],
) -> Dict[str, Any]:
    evidence = market.get("evidence_items", []) if isinstance(market.get("evidence_items"), list) else []
    observations = market.get("observations", []) if isinstance(market.get("observations"), list) else []
    positions = portfolio.get("positions", []) if isinstance(portfolio.get("positions"), list) else []
    assets = {str(item.get("asset") or "") for item in positions if isinstance(item, dict)}
    themes = {str(item.get("theme") or "") for item in positions if isinstance(item, dict)}
    research_ok = research_state.get("status") == "ok" and isinstance(research_state.get("output"), dict)
    previous_signature = str(previous.get("decision_signature") or "")
    decision_changed = bool(previous_signature and previous_signature != decision_signature)
    items: Dict[str, Any] = {}
    counts = {key: 0 for key in ("CHANGED", "UNCHANGED", "UNCERTAIN", "NEEDS_REVIEW", "NOT_RELEVANT")}
    prior_items = previous_assessments.get("items", {}) if isinstance(previous_assessments.get("items"), dict) else {}
    combined: list[tuple[str, Dict[str, Any]]] = []
    for index, item in enumerate(evidence):
        if not isinstance(item, dict):
            continue
        evidence_id = str(item.get("evidence_id") or f"evidence-{index}")
        combined.append((evidence_id, item))
    for item in observations:
        if not isinstance(item, dict) or item.get("data_quality_status") not in {"Available", "Partial"}:
            continue
        evidence_id = _observation_evidence_id(item)
        combined.append(
            (
                evidence_id,
                {
                    "headline": f"{item.get('asset')}: provider market observation",
                    "source": item.get("source"),
                    "channel": "price_volume",
                    "affected_assets": [item.get("asset")],
                    "affected_themes": [item.get("theme")],
                    "thesis_changed": "UNASSESSED",
                },
            )
        )
    for evidence_id, item in combined:
        raw_status = str(item.get("thesis_changed") or "UNASSESSED").upper()
        affected_assets = {str(value) for value in item.get("affected_assets", [])}
        affected_themes = {str(value) for value in item.get("affected_themes", [])}
        broad_channel = str(item.get("channel") or "") in {"market_breadth", "macro_policy", "liquidity_proxy", "volatility"}
        relevant = bool(assets.intersection(affected_assets) or themes.intersection(affected_themes) or broad_channel)
        prior = prior_items.get(evidence_id, {}) if isinstance(prior_items.get(evidence_id), dict) else {}
        if prior.get("status") in {"CHANGED", "UNCHANGED", "NOT_RELEVANT"}:
            status = str(prior.get("status"))
            reason = str(prior.get("reason") or "preserved_runtime_assessment")
        elif raw_status in counts:
            status = raw_status
            reason = "source_supplied_assessment"
        elif not relevant:
            status = "NOT_RELEVANT"
            reason = "no_portfolio_or_theme_mapping"
        elif not research_ok:
            status = "NEEDS_REVIEW"
            reason = "research_route_unavailable_or_incomplete"
        elif not previous_signature:
            status = "UNCHANGED"
            reason = "first_validated_runtime_baseline_established"
        elif decision_changed:
            status = "CHANGED"
            reason = "validated_decision_band_changed_after_review"
        else:
            status = "UNCHANGED"
            reason = "reviewed_without_validated_decision_band_change"
        counts[status] += 1
        items[evidence_id] = {
            "status": status,
            "reason": reason,
            "headline": item.get("headline"),
            "source": item.get("source"),
            "affected_assets": sorted(affected_assets),
            "affected_themes": sorted(affected_themes),
        }
    return {
        "assessed_at": utc_now_iso(),
        "decision_signature": decision_signature,
        "research_updated_at": research_state.get("updated_at"),
        "items": items,
        "summary": {
            **counts,
            "reviewed_count": len(items),
            "thesis_changed": counts["CHANGED"] > 0,
        },
    }


def _candidate_runtime_overlay(assessments: Dict[str, Any]) -> Dict[str, Any]:
    assets: Dict[str, Dict[str, Any]] = {}
    for evidence_id, item in assessments.get("items", {}).items():
        if not isinstance(item, dict):
            continue
        for asset in item.get("affected_assets", []):
            entry = assets.setdefault(
                str(asset),
                {"evidence_ids": [], "statuses": [], "last_reviewed_at": assessments.get("assessed_at")},
            )
            entry["evidence_ids"].append(evidence_id)
            entry["statuses"].append(item.get("status"))
    for entry in assets.values():
        statuses = set(entry.pop("statuses", []))
        entry["assessment"] = (
            "CHANGED" if "CHANGED" in statuses else "UNCERTAIN" if "UNCERTAIN" in statuses else "NEEDS_REVIEW" if "NEEDS_REVIEW" in statuses else "UNCHANGED"
        )
        entry["priority_delta"] = "review" if entry["assessment"] in {"CHANGED", "UNCERTAIN", "NEEDS_REVIEW"} else "unchanged"
        entry["reason"] = "runtime_evidence_review"
    return {
        "updated_at": assessments.get("assessed_at"),
        "assets": assets,
        "runtime_only": True,
        "knowledge_source_mutated": False,
    }


def _observation_evidence_id(observation: Dict[str, Any]) -> str:
    return "observation:{asset}:{timestamp}".format(
        asset=str(observation.get("asset") or "Unknown"),
        timestamp=str(observation.get("timestamp") or "Unknown"),
    )


def _section_source_ids(name: str, market: Dict[str, Any], cycle: Dict[str, Any]) -> list[str]:
    if name in {"material_changes", "candidate_delta", "data_freshness"}:
        return [
            str(item.get("evidence_id"))
            for item in market.get("evidence_items", [])
            if isinstance(item, dict) and item.get("evidence_id")
        ][:20]
    return [
        str(event_id)
        for result in cycle.get("results", [])
        if isinstance(result, dict)
        for event_id in result.get("event_ids", [])
    ][:20]


def _brief_update_reason(name: str, proactive_update: Dict[str, Any], ui_events_ingested: int) -> str:
    if ui_events_ingested:
        return f"ui_event:{name}"
    if proactive_update.get("status") in {"COMPLETED", "DEGRADED", "FAILED"}:
        return f"proactive_{str(proactive_update.get('status')).lower()}:{name}"
    return f"material_runtime_delta:{name}"


def _stable_digest(value: Any) -> str:
    payload = json.dumps(_stable_brief_value(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _stable_brief_value(value: Any) -> Any:
    volatile = {"timestamp", "created_at", "updated_at", "assessed_at", "last_reviewed_at"}
    if isinstance(value, dict):
        return {key: _stable_brief_value(item) for key, item in value.items() if key not in volatile}
    if isinstance(value, list):
        return [_stable_brief_value(item) for item in value]
    if isinstance(value, str):
        return value[:4000]
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Atlas OS Runtime v0.1 daemon")
    parser.add_argument("--interval", type=int, default=60, choices=[10, 30, 60, 300])
    parser.add_argument("--max-cycles", type=int, default=None)
    parser.add_argument("--log-path", default=None)
    parser.add_argument("--db-path", default=None)
    parser.add_argument("--inbox-dir", default=None)
    parser.add_argument("--ui-inbox-path", default=None)
    parser.add_argument("--llm-model", default="gpt5.5")
    parser.add_argument("--no-sleep", action="store_true", help="test mode: run cycles without sleeping")
    parser.add_argument("--disable-market-refresh", action="store_true")
    parser.add_argument("--market-refresh-every-cycles", type=int, default=5)
    parser.add_argument("--market-config-path", default=None)
    parser.add_argument("--market-max-assets", type=int, default=12)
    parser.add_argument("--daily-cycle-now", default=None, help="controlled ISO timestamp for daily-cycle validation")
    parser.add_argument("--disable-proactive-update", action="store_true")
    parser.add_argument("--proactive-update-every-seconds", type=int, default=DEFAULT_PROACTIVE_UPDATE_SECONDS)
    parser.add_argument("--no-proactive-update-on-start", action="store_true")
    parser.add_argument("--runtime-mode", choices=["auto", "simulation", "live"], default="auto")
    parser.add_argument(
        "--cognition-mode",
        choices=["lean", "full"],
        default=None,
        help="lean (default): fusion + controller + LLM only; full: legacy symbolic cognition chain",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    daemon = AtlasRuntimeDaemon(
        AtlasRuntimeDaemonConfig(
            interval_seconds=args.interval,
            max_cycles=args.max_cycles,
            log_path=args.log_path,
            db_path=args.db_path,
            inbox_dir=args.inbox_dir,
            ui_inbox_path=args.ui_inbox_path,
            llm_model=args.llm_model,
            no_sleep=args.no_sleep,
            market_refresh_enabled=not args.disable_market_refresh,
            market_refresh_every_cycles=args.market_refresh_every_cycles,
            market_config_path=args.market_config_path,
            market_max_assets=args.market_max_assets,
            daily_cycle_now=args.daily_cycle_now,
            proactive_update_enabled=not args.disable_proactive_update,
            proactive_update_every_seconds=args.proactive_update_every_seconds,
            proactive_update_run_on_start=not args.no_proactive_update_on_start,
            runtime_mode=args.runtime_mode,
            cognition_mode=args.cognition_mode if args.cognition_mode else "auto",
        )
    )
    signal.signal(signal.SIGINT, daemon.stop)
    signal.signal(signal.SIGTERM, daemon.stop)
    daemon.run_forever()


def _select(value: Any, keys: list[str]) -> Dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    return {key: value.get(key) for key in keys}


def _resolve_runtime_mode(configured: str, config_path: Optional[str]) -> str:
    mode = str(configured or "auto").strip().lower()
    if mode in {"simulation", "live"}:
        return mode
    path = Path(config_path) if config_path else None
    if path and path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            system = data.get("system", {}) if isinstance(data, dict) else {}
            selected = str(system.get("runtime_mode") or "simulation").strip().lower()
            if selected in {"simulation", "live"}:
                return selected
        except (OSError, json.JSONDecodeError):
            pass
    return "simulation"


def _resolve_cognition_mode(configured: Optional[str], config_path: Optional[str]) -> str:
    """Resolve cognition mode: explicit lean/full wins, else user config, else lean."""

    mode = str(configured or "").strip().lower()
    if mode in {"lean", "full"}:
        return mode
    candidates = []
    if config_path:
        candidates.append(Path(config_path))
    candidates.append(Path("runtime/config/user_config.json"))
    for path in candidates:
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        system = data.get("system", {}) if isinstance(data, dict) else {}
        selected = str(system.get("cognition_mode") or "").strip().lower()
        if selected in {"lean", "full"}:
            return selected
    return "lean"


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _epoch_iso(value: float) -> str:
    return datetime.fromtimestamp(value, tz=timezone.utc).isoformat()


def _float(value: Any, fallback: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


if __name__ == "__main__":
    main()
