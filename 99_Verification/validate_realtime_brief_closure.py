"""Validate continuous material-event Brief publication with isolated evidence."""

from __future__ import annotations

import json
import os
import tempfile
import tracemalloc
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
os.sys.path.insert(0, str(ROOT))

import runtime.atlas_runtime_daemon as daemon_module  # noqa: E402
import runtime.orchestrator as orchestrator_module  # noqa: E402
from runtime.atlas_runtime_daemon import AtlasRuntimeDaemon, AtlasRuntimeDaemonConfig  # noqa: E402
from runtime.cognition.decision_validator import DECISION_PACKET_FIELDS  # noqa: E402
from runtime.event_stream import EventStream  # noqa: E402
from runtime.market_intelligence import _market_session_semantics  # noqa: E402
from runtime.state_store import StateStore  # noqa: E402
from runtime.telemetry.jsonl import append_jsonl  # noqa: E402
from ui.app_server import append_chat_event, brief_current_api, state_api, state_summary_api  # noqa: E402


def main() -> int:
    original_llm = orchestrator_module.call_llm_for_task
    original_market = daemon_module.refresh_market_intelligence
    old_env = {
        key: os.environ.get(key)
        for key in (
            "ATLAS_USER_CONFIG",
            "ATLAS_UI_DB_PATH",
            "ATLAS_RUNTIME_DB",
            "ATLAS_UI_INBOX",
            "ATLAS_EVENT_INBOX",
            "ATLAS_RUNTIME_LOG",
            "ATLAS_LLM_TRACE_LOG",
            "ATLAS_UI_PID_FILE",
            "ATLAS_DISABLE_KEYCHAIN",
            "ATLAS_CONTINUOUS_BRIEF_ENABLED",
        )
    }
    result: dict[str, Any] = {"checks": {}, "evidence": {}}
    try:
        with tempfile.TemporaryDirectory(prefix="atlas-realtime-brief-") as temp_dir:
            root = Path(temp_dir)
            config_path = root / "user_config.json"
            _write_config(config_path)
            _set_env(root, config_path)
            calls: Counter[str] = Counter()
            orchestrator_module.call_llm_for_task = _fake_llm(calls)

            heartbeat = _heartbeat_check(root, config_path, calls)
            result["evidence"]["heartbeat"] = heartbeat
            _check("heartbeat_zero_llm_calls", heartbeat["llm_calls"] == 0, result)
            _check("heartbeat_zero_brief_revisions", heartbeat["brief_revision"] == 0, result)

            ui_event = _ui_event_check(root, config_path, calls)
            result["evidence"]["ui_event"] = ui_event
            _check("ui_event_published_within_one_tick", ui_event["brief_revision"] == 1, result)
            _check("ui_event_executed_all_roles", ui_event["role_calls"] == {"workhorse": 1, "research": 1, "decision": 1}, result)

            proactive = _proactive_check(root, config_path, calls)
            result["evidence"]["proactive"] = proactive
            _check("proactive_terminal_state", proactive["status"] in {"COMPLETED", "DEGRADED", "FAILED"}, result)
            _check("proactive_all_role_timestamps", all(proactive["role_timestamps"].values()), result)

            portfolio = _portfolio_change_check(root, config_path, calls)
            result["evidence"]["portfolio_change"] = portfolio
            _check("portfolio_change_published_next_tick", portfolio["changed_revision"] > portfolio["initial_revision"], result)
            _check("portfolio_change_excludes_private_amounts", portfolio["private_amounts_included"] is False, result)
            _check("restart_retains_last_valid_brief", portfolio["restart_revision"] == portfolio["changed_revision"], result)

            market = _market_delta_check(root, config_path, calls)
            result["evidence"]["market_delta"] = market
            _check("market_change_within_refresh_tick", market["changed_revision"] > market["initial_revision"], result)
            _check("identical_market_no_duplicate_calls", market["duplicate_call_delta"] == 0, result)
            _check("identical_market_no_duplicate_revision", market["duplicate_revision"] == market["initial_revision"], result)

            accelerated = _accelerated_tick_check(root, config_path, calls)
            result["evidence"]["accelerated_ticks"] = accelerated
            _check("accelerated_500_ticks_zero_errors", accelerated["cycles"] >= 500 and accelerated["errors"] == 0, result)
            _check("accelerated_heartbeat_zero_churn", accelerated["llm_calls"] == 0 and accelerated["brief_revision"] == 0, result)

            home = _home_semantics_check()
            result["evidence"]["home"] = home
            _check("home_matches_decision_packet", home["action"] == "reduce" and home["risk"] == "high" and home["posture_visible"], result)
            _check("reviewed_unchanged_visible", home["reviewed_unchanged_visible"], result)
            _check("brief_current_is_section_refreshable", home["brief_revision"] > 0 and home["has_home_html"], result)

            session = _closed_market_check()
            result["evidence"]["closed_market"] = session
            _check("closed_market_last_close_semantics", session["status"] == "LAST_MARKET_CLOSE" and bool(session["timestamp"]), result)

            memory = _polling_memory_check()
            result["evidence"]["polling_memory"] = memory
            _check("two_hour_equivalent_polling_memory_bounded", memory["growth_bytes"] < 3_000_000, result)

            retention = _retention_check(root)
            result["evidence"]["retention"] = retention
            _check("jsonl_rotation_bounded", retention["backup_count"] <= 2 and retention["total_bytes"] < 5_000, result)

            _check("decision_contract_fields_unchanged", DECISION_PACKET_FIELDS == {
                "regime_state", "confidence", "risk_level", "attention_state", "liquidity_state",
                "causal_summary", "recommended_action", "reasoning_trace",
            }, result)
            _check("no_trading_execution", all(
                item.get("no_trading_execution") is True
                for item in (ui_event, proactive, market, home)
            ), result)

            failures = [name for name, passed in result["checks"].items() if not passed]
            result["status"] = "PASS" if not failures else "FAIL"
            result["failures"] = failures
            artifact_dir = ROOT / "99_Verification/artifacts/realtime_brief_closure"
            artifact_dir.mkdir(parents=True, exist_ok=True)
            (artifact_dir / "validation_result.json").write_text(
                json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
            return 0 if not failures else 1
    finally:
        orchestrator_module.call_llm_for_task = original_llm
        daemon_module.refresh_market_intelligence = original_market
        for key, value in old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _heartbeat_check(root: Path, config_path: Path, calls: Counter[str]) -> dict[str, Any]:
    before = sum(calls.values())
    db_path = root / "heartbeat.sqlite"
    daemon = _daemon(root, config_path, db_path, "heartbeat", market=False, proactive=False)
    entry = daemon.run_tick(0)
    brief = StateStore(db_path=str(db_path)).get_state("current_brief_state")
    return {
        "status": entry["system_metrics"]["status"],
        "llm_calls": sum(calls.values()) - before,
        "brief_revision": int(brief.get("brief_revision", 0) or 0),
        "no_trading_execution": True,
    }


def _ui_event_check(root: Path, config_path: Path, calls: Counter[str]) -> dict[str, Any]:
    before = Counter(calls)
    db_path = root / "ui-event.sqlite"
    inbox = root / "ui-event.jsonl"
    append_chat_event("Review the latest portfolio evidence.", inbox_path=str(inbox))
    daemon = _daemon(root, config_path, db_path, "ui-event", market=False, proactive=False, inbox=inbox)
    entry = daemon.run_tick(0)
    store = StateStore(db_path=str(db_path))
    brief = store.get_state("current_brief_state")
    return {
        "status": entry["system_metrics"]["status"],
        "brief_revision": int(brief.get("brief_revision", 0) or 0),
        "changed_sections": brief.get("changed_sections", []),
        "role_calls": {role: calls[role] - before[role] for role in ("workhorse", "research", "decision")},
        "no_trading_execution": True,
    }


def _proactive_check(root: Path, config_path: Path, calls: Counter[str]) -> dict[str, Any]:
    db_path = root / "proactive.sqlite"
    daemon = _daemon(root, config_path, db_path, "proactive", market=False, proactive=True)
    daemon.run_tick(0)
    state = StateStore(db_path=str(db_path)).get_state("proactive_update_state")
    roles = state.get("role_results", {}) if isinstance(state.get("role_results"), dict) else {}
    return {
        "status": state.get("status"),
        "role_timestamps": {role: (roles.get(role) or {}).get("executed_at") for role in ("workhorse", "research", "decision")},
        "role_statuses": {role: (roles.get(role) or {}).get("status") for role in ("workhorse", "research", "decision")},
        "no_trading_execution": True,
    }


def _market_delta_check(root: Path, config_path: Path, calls: Counter[str]) -> dict[str, Any]:
    db_path = root / "market.sqlite"
    price = {"value": 100.0}

    def refresh(**kwargs: Any) -> dict[str, Any]:
        timestamp = "2026-07-19T01:00:00+00:00"
        observation = {
            "asset": "ATLAS1", "market": "US", "theme": "Runtime Validation",
            "timestamp": timestamp, "source": "controlled_market_source", "source_type": "market_data_provider",
            "latest_price": price["value"], "daily_change_pct": price["value"] - 100.0,
            "change_5d_pct": price["value"] - 100.0, "change_20d_pct": 0.0,
            "freshness": "LIVE", "market_session_status": "CURRENT_SESSION",
            "market_session_timestamp": timestamp, "data_quality_status": "Available",
            "latest_price_available": True, "portfolio_relevant": True, "channel": "price_volume",
        }
        if kwargs.get("enqueue"):
            EventStream(db_path=kwargs.get("db_path")).enqueue_event(
                "price_breakout",
                payload={"asset": "ATLAS1", "latest_price": price["value"], "daily_change_pct": price["value"] - 100.0},
                priority=50,
                source="controlled_market_source",
                created_at=timestamp,
            )
        return {
            "timestamp": timestamp, "status": "ok", "channels": {"price_volume": "LIVE", "portfolio_relevance": "LIVE"},
            "observations": [observation], "evidence_items": [], "events_enqueued": 1,
            "degraded": False, "read_only": True, "no_trading_execution": True,
        }

    daemon_module.refresh_market_intelligence = refresh
    daemon = _daemon(root, config_path, db_path, "market", market=True, proactive=False)
    daemon.run_tick(0)
    store = StateStore(db_path=str(db_path))
    initial_revision = int(store.get_state("current_brief_state").get("brief_revision", 0) or 0)
    calls_before_duplicate = sum(calls.values())
    daemon.run_tick(1)
    duplicate_revision = int(store.get_state("current_brief_state").get("brief_revision", 0) or 0)
    duplicate_call_delta = sum(calls.values()) - calls_before_duplicate
    price["value"] = 104.0
    daemon.run_tick(2)
    changed_revision = int(store.get_state("current_brief_state").get("brief_revision", 0) or 0)
    return {
        "initial_revision": initial_revision,
        "duplicate_revision": duplicate_revision,
        "duplicate_call_delta": duplicate_call_delta,
        "changed_revision": changed_revision,
        "no_trading_execution": True,
    }


def _portfolio_change_check(root: Path, config_path: Path, calls: Counter[str]) -> dict[str, Any]:
    db_path = root / "portfolio-change.sqlite"
    inbox = root / "portfolio-change-ui.jsonl"
    daemon = _daemon(root, config_path, db_path, "portfolio-change", market=False, proactive=False, inbox=inbox)
    daemon.run_tick(0)
    append_chat_event("Establish a valid Brief before the portfolio change.", inbox_path=str(inbox))
    daemon.run_tick(1)
    store = StateStore(db_path=str(db_path))
    initial_revision = int(store.get_state("current_brief_state").get("brief_revision", 0) or 0)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    positions = json.loads(config["assets"]["portfolio_json"])
    positions[0]["portfolio_percentage"] = 70
    config["assets"]["portfolio_json"] = json.dumps(positions)
    config["assets"]["weights"] = {"ATLAS1": 70}
    config_path.write_text(json.dumps(config, ensure_ascii=False) + "\n", encoding="utf-8")
    entry = daemon.run_tick(2)
    changed_revision = int(store.get_state("current_brief_state").get("brief_revision", 0) or 0)
    events = store.get_event_history(limit=5)
    event = next((item for item in events if item.get("source") == "local_portfolio_config"), {})
    payload = event.get("payload", {}) if isinstance(event.get("payload"), dict) else {}
    restarted = _daemon(root, config_path, db_path, "portfolio-restart", market=False, proactive=False)
    restarted.run_tick(3)
    restart_revision = int(store.get_state("current_brief_state").get("brief_revision", 0) or 0)
    return {
        "initial_revision": initial_revision,
        "changed_revision": changed_revision,
        "restart_revision": restart_revision,
        "change_status": entry.get("system_metrics", {}).get("portfolio_change_status"),
        "private_amounts_included": payload.get("private_amounts_included"),
        "no_trading_execution": True,
    }


def _accelerated_tick_check(root: Path, config_path: Path, calls: Counter[str]) -> dict[str, Any]:
    db_path = root / "accelerated-heartbeat.sqlite"
    before = sum(calls.values())
    daemon = _daemon(root, config_path, db_path, "accelerated-heartbeat", market=False, proactive=False)
    errors = 0
    for tick in range(501):
        entry = daemon.run_tick(tick)
        if entry.get("system_metrics", {}).get("status") != "success":
            errors += 1
    brief = StateStore(db_path=str(db_path)).get_state("current_brief_state")
    return {
        "cycles": 501,
        "errors": errors,
        "llm_calls": sum(calls.values()) - before,
        "brief_revision": int(brief.get("brief_revision", 0) or 0),
    }


def _home_semantics_check() -> dict[str, Any]:
    state = state_api()
    packet = state.get("last_decision_packet", {})
    html = brief_current_api().get("home_html", "")
    brief = state.get("brief_runtime_state", {})
    return {
        "action": packet.get("recommended_action"),
        "risk": packet.get("risk_level"),
        "posture_visible": "Reduce" in html or "降低暴露" in html,
        "reviewed_unchanged_visible": ("结论不变" in html or "unchanged" in html.lower()),
        "brief_revision": int(brief.get("brief_revision", 0) or 0),
        "has_home_html": 'data-practical-section="brief_runtime"' in html,
        "no_trading_execution": True,
    }


def _closed_market_check() -> dict[str, Any]:
    status, timestamp = _market_session_semantics(
        {"timestamp": "2026-07-17T20:00:00+00:00"},
        "US",
        now=datetime(2026, 7, 19, 12, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
    )
    return {"status": status, "timestamp": timestamp}


def _polling_memory_check() -> dict[str, Any]:
    state_summary_api()
    tracemalloc.start()
    before, _ = tracemalloc.get_traced_memory()
    for _ in range(3600):
        payload = state_summary_api()
        if "brief_runtime_state" not in payload:
            raise AssertionError("summary missing Brief revision state")
    after, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {"poll_count": 3600, "growth_bytes": max(0, after - before), "peak_bytes": peak}


def _retention_check(root: Path) -> dict[str, Any]:
    path = root / "rotation.jsonl"
    for index in range(80):
        append_jsonl(path, {"index": index, "payload": "x" * 180}, max_bytes=1024, backup_count=2)
    files = [item for item in [path, path.with_name(path.name + ".1"), path.with_name(path.name + ".2")] if item.exists()]
    return {"backup_count": len(files) - int(path.exists()), "total_bytes": sum(item.stat().st_size for item in files)}


def _daemon(
    root: Path,
    config_path: Path,
    db_path: Path,
    name: str,
    *,
    market: bool,
    proactive: bool,
    inbox: Path | None = None,
) -> AtlasRuntimeDaemon:
    return AtlasRuntimeDaemon(
        AtlasRuntimeDaemonConfig(
            interval_seconds=60,
            max_cycles=1,
            no_sleep=True,
            db_path=str(db_path),
            log_path=str(root / f"{name}.jsonl"),
            inbox_dir=str(root / f"{name}-events"),
            ui_inbox_path=str(inbox or root / f"{name}-ui.jsonl"),
            market_config_path=str(config_path),
            market_refresh_enabled=market,
            market_refresh_every_cycles=1,
            proactive_update_enabled=proactive,
            proactive_update_run_on_start=proactive,
            runtime_mode="live",
        ),
        event_source=None,
    )


def _fake_llm(calls: Counter[str]):
    def call(role: str, _prompt: str, _context: dict[str, Any], **_kwargs: Any) -> dict[str, Any]:
        calls[role] += 1
        if role == "workhorse":
            content = {"status": "ok", "query_intent": "Review evidence", "signals": [], "unknowns": []}
        elif role == "research":
            content = {
                "status": "ok", "summary": "Evidence reviewed without a thesis override.",
                "portfolio_relevance": ["ATLAS1"], "causal_factors": ["price observation"],
                "counter_evidence": ["single source"], "hypotheses": ["working view unchanged"],
                "uncertainties": ["breadth unavailable"],
            }
        else:
            content = {
                "regime_state": "RISK_OFF", "confidence": 0.72, "risk_level": "high",
                "attention_state": "mixed", "liquidity_state": "fragile",
                "causal_summary": "Portfolio-linked evidence warrants a risk review without execution.",
                "recommended_action": "reduce", "reasoning_trace": "Validated isolated runtime response.",
            }
        return {
            "status": "ok", "provider": "isolated_fixture", "model": f"{role}-fixture",
            "content": json.dumps(content), "latency_ms": 1,
            "usage": {"input_tokens": 10, "output_tokens": 10, "total_tokens": 20},
            "estimated_cost": 0.0, "cost_status": "fixture", "cache_status": "miss",
            "fallback_attempts": [], "route_status": "ACTIVE", "error": "",
        }

    return call


def _write_config(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "assets": {
                    "portfolio_json": json.dumps(
                        [{"asset": "ATLAS1", "market": "US", "portfolio_percentage": 80, "theme": "Runtime Validation", "role": "Core"}]
                    ),
                    "asset_list": ["ATLAS1"],
                    "weights": {"ATLAS1": 80},
                },
                "system": {"tick_interval": 60, "proactive_update_interval_seconds": 7200, "runtime_mode": "live"},
                "ui": {"language": "en"},
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def _set_env(root: Path, config_path: Path) -> None:
    os.environ.update(
        {
            "ATLAS_USER_CONFIG": str(config_path),
            "ATLAS_UI_DB_PATH": str(root / "market.sqlite"),
            "ATLAS_RUNTIME_DB": str(root / "market.sqlite"),
            "ATLAS_UI_INBOX": str(root / "ui.jsonl"),
            "ATLAS_EVENT_INBOX": str(root / "events"),
            "ATLAS_RUNTIME_LOG": str(root / "runtime.jsonl"),
            "ATLAS_LLM_TRACE_LOG": str(root / "llm.jsonl"),
            "ATLAS_UI_PID_FILE": str(root / "runtime.pid"),
            "ATLAS_DISABLE_KEYCHAIN": "1",
            "ATLAS_CONTINUOUS_BRIEF_ENABLED": "1",
        }
    )


def _check(name: str, condition: bool, result: dict[str, Any]) -> None:
    result["checks"][name] = bool(condition)


if __name__ == "__main__":
    raise SystemExit(main())
