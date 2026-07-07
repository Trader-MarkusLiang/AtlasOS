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
import json
import signal
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from runtime.daily_cycle import current_daily_cycle
    from runtime.decision_loop import DecisionLoop, DecisionLoopConfig
    from runtime.event_source import SimulatedMarketEventSource, event_to_runtime_event
    from runtime.logging import utc_now_iso
    from runtime.market_intelligence import refresh_market_intelligence
    from runtime.output_logger import RuntimeOutputLogger
    from runtime.scheduler import RuntimeScheduleConfig, next_run_time
    from runtime.state_store import StateStore
    from runtime.telemetry.decision_trace_logger import log_decision_trace
    from runtime.telemetry.state_snapshot import capture_cognitive_snapshot
except ModuleNotFoundError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from runtime.daily_cycle import current_daily_cycle
    from runtime.decision_loop import DecisionLoop, DecisionLoopConfig
    from runtime.event_source import SimulatedMarketEventSource, event_to_runtime_event
    from runtime.logging import utc_now_iso
    from runtime.market_intelligence import refresh_market_intelligence
    from runtime.output_logger import RuntimeOutputLogger
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
    llm_model: str = "gpt-5.5"
    max_events_per_cycle: int = 10
    no_sleep: bool = False
    market_refresh_enabled: bool = True
    market_refresh_every_cycles: int = 5
    market_config_path: Optional[str] = None
    market_max_assets: int = 12


class AtlasRuntimeDaemon:
    """Continuously generate/fetch events and run Atlas cognition ticks."""

    def __init__(
        self,
        config: Optional[AtlasRuntimeDaemonConfig] = None,
        event_source: Optional[Any] = None,
    ) -> None:
        self.config = config or AtlasRuntimeDaemonConfig()
        self.schedule = RuntimeScheduleConfig(interval_seconds=self.config.interval_seconds)
        self.event_source = event_source or SimulatedMarketEventSource()
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
            )
        )
        self._running = False

    def run_tick(self, tick_index: int) -> Dict[str, Any]:
        """Run one isolated daemon tick and always return a loggable record."""

        started = time.time()
        raw_event: Dict[str, Any] = {}
        runtime_event: Dict[str, Any] = {}
        status = "success"
        error = None
        cycle: Dict[str, Any] = {}
        ui_events_ingested = 0
        market_refresh: Dict[str, Any] = {}

        try:
            ui_events_ingested = self._ingest_ui_inbox_events()
            market_refresh = self._refresh_market_if_due(tick_index)
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
        )
        self._write_telemetry(tick_index, entry)
        self.output_logger.log_tick(entry)
        return entry

    def run_forever(self) -> None:
        self._running = True
        tick_index = 0
        while self._running:
            self.run_tick(tick_index)
            tick_index += 1
            if self.config.max_cycles is not None and tick_index >= self.config.max_cycles:
                break
            if not self.config.no_sleep:
                time.sleep(self.schedule.interval_seconds)

    def stop(self, *_args: object) -> None:
        self._running = False

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
                        "decision_packet_action",
                        "decision_packet_risk",
                        "decision_packet_confidence",
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
                "market_refresh_status": (market_refresh or {}).get("status", "not_run"),
                "market_events_enqueued": int((market_refresh or {}).get("events_enqueued", 0) or 0),
                "market_channels": (market_refresh or {}).get("channels", {}),
                "daily_cycle": self._daily_cycle_status(),
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

    def _daily_cycle_status(self) -> Dict[str, Any]:
        result = current_daily_cycle(db_path=self.config.db_path)
        self.store.set_state("daily_cycle_state", result)
        return result

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
                },
            )
        except Exception as exc:
            entry.setdefault("telemetry", {})["status"] = "error"
            entry.setdefault("telemetry", {})["error"] = str(exc)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Atlas OS Runtime v0.1 daemon")
    parser.add_argument("--interval", type=int, default=60, choices=[10, 30, 60, 300])
    parser.add_argument("--max-cycles", type=int, default=None)
    parser.add_argument("--log-path", default=None)
    parser.add_argument("--db-path", default=None)
    parser.add_argument("--inbox-dir", default=None)
    parser.add_argument("--ui-inbox-path", default=None)
    parser.add_argument("--llm-model", default="gpt-5.5")
    parser.add_argument("--no-sleep", action="store_true", help="test mode: run cycles without sleeping")
    parser.add_argument("--disable-market-refresh", action="store_true")
    parser.add_argument("--market-refresh-every-cycles", type=int, default=5)
    parser.add_argument("--market-config-path", default=None)
    parser.add_argument("--market-max-assets", type=int, default=12)
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
        )
    )
    signal.signal(signal.SIGINT, daemon.stop)
    signal.signal(signal.SIGTERM, daemon.stop)
    daemon.run_forever()


def _select(value: Any, keys: list[str]) -> Dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    return {key: value.get(key) for key in keys}


if __name__ == "__main__":
    main()
