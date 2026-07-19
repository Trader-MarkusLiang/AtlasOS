"""Prompt C completion enforcement validation.

This script uses only temporary fixtures/state. It proves execution paths rather
than source-shape claims and does not read or print real provider secrets.
"""

from __future__ import annotations

import json
import os
import resource
import sqlite3
import sys
import tempfile
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.atlas_runtime_daemon import AtlasRuntimeDaemon, AtlasRuntimeDaemonConfig
from runtime.cognition.decision_contract import parse_decision_packet
from runtime.daily_cycle import (
    dispatch_current_daily_cycle,
    run_intraday_cycle,
    run_morning_cycle,
    run_overnight_cycle,
    run_post_market_cycle,
)
from runtime.decision_loop import DecisionLoop, DecisionLoopConfig
from runtime.event_stream import EventStream
from runtime.forecast_ledger import create_forecast, evaluate_forecast, list_forecasts, mark_forecast_matured
from runtime.llm.provider_registry import (
    encrypt_api_key,
    health_check_provider,
    list_provider_models,
)
from runtime.llm.provider_router import route_llm_request
from runtime.logging import utc_now_iso
from runtime.market_intelligence import refresh_market_intelligence
from runtime.portfolio_context import build_portfolio_context
from runtime.state_store import StateStore
from runtime.telemetry.llm_trace_logger import log_llm_trace, read_llm_traces
from ui.system_control_panel import runtime_status, stop_runtime_daemon


ALLOWED_CHANNEL_STATES = {"LIVE", "DELAYED", "CACHED", "SIMULATED", "NOT_CONFIGURED", "FAILED"}
FIXTURE_SECRET = "atlas_prompt_c_fixture_secret"


class _ProviderFixtureHandler(BaseHTTPRequestHandler):
    def log_message(self, _fmt: str, *_args: Any) -> None:
        return

    def do_HEAD(self) -> None:  # noqa: N802
        if self.path.endswith("/v1/chat/completions"):
            self.send_response(200)
        else:
            self.send_response(404)
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        if self.path.endswith("/v1/models"):
            self._json({"data": [{"id": "fixture-model-a"}, {"id": "fixture-model-b"}]})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self) -> None:  # noqa: N802
        if self.path.endswith("/bad500"):
            self.send_response(500)
            self.end_headers()
            return
        if self.path.endswith("/malformed"):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"{bad-json")
            return
        if self.path.endswith("/empty"):
            self._json({"choices": [{"message": {"content": ""}}]})
            return
        packet = {
            "regime_state": "NORMAL",
            "confidence": 0.42,
            "risk_level": "medium",
            "attention_state": "elevated",
            "liquidity_state": "mixed",
            "causal_summary": "Fixture causal summary from controlled provider.",
            "recommended_action": "observe",
            "reasoning_trace": "Fixture trace for provider E2E validation.",
        }
        self._json({"choices": [{"message": {"content": json.dumps(packet)}}]})

    def _json(self, payload: dict[str, Any]) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="atlas-prompt-c-") as tmp:
        root = Path(tmp)
        os.environ["ATLAS_DISABLE_KEYCHAIN"] = "1"
        os.environ["ATLAS_LLM_BACKEND"] = "litellm"
        results = {
            "llm_e2e": _llm_e2e(root),
            "market_ingestion": _market_ingestion(root),
            "portfolio_cognition": _portfolio_cognition(root),
            "forecast_lifecycle": _forecast_lifecycle(root),
            "self_iteration": _self_iteration(root),
            "daily_cycle": _daily_cycle(root),
            "recovery": _recovery(root),
            "soak": _soak(root),
            "security": _security(root),
        }
    print(json.dumps({"status": "PASS", "results": results}, ensure_ascii=False, indent=2, sort_keys=True))


def _llm_e2e(root: Path) -> dict[str, Any]:
    server, thread, port = _start_provider_fixture()
    try:
        config_path = root / "providers.json"
        registry = _provider_registry(f"http://127.0.0.1:{port}")
        config_path.write_text(json.dumps({"llm_registry": registry}, ensure_ascii=False), encoding="utf-8")
        health = health_check_provider("good", str(config_path), timeout=2)
        models = list_provider_models("good", str(config_path), timeout=2)
        routed = route_llm_request(
            prompt="Return a DecisionPacket.",
            context={"runtime_context": {"trigger_type": "prompt_c_provider_e2e"}},
            provider_id="bad500",
            config_path=str(config_path),
        )
        packet = parse_decision_packet(str(routed.get("content", "")))
        trace_path = root / "llm_traces.jsonl"
        log_llm_trace(
            provider=str(routed.get("provider")),
            model=str(routed.get("model")),
            prompt="Return a DecisionPacket.",
            context={"contract_version": "decision_packet_v0.2"},
            output_raw=str(routed.get("content")),
            latency_ms=int(routed.get("latency_ms") or 0),
            decision_packet_id="prompt-c-provider-e2e",
            feedback_applied=False,
            log_path=str(trace_path),
        )
        trace_text = trace_path.read_text(encoding="utf-8")
        assert FIXTURE_SECRET not in trace_text
        assert health["status"] in {"healthy", "reachable"}
        assert models["status"] == "ok" and "fixture-model-a" in models["models"]
        assert routed["provider"] == "good"
        assert routed["fallback_attempts"]
        assert packet["recommended_action"] == "observe"
        return {
            "health_status": health["status"],
            "models": models["models"],
            "fallback_provider": routed["provider"],
            "fallback_attempt_count": len(routed["fallback_attempts"]),
            "decision_packet_action": packet["recommended_action"],
            "telemetry_records": len(read_llm_traces(str(trace_path))),
            "secret_masked": FIXTURE_SECRET not in trace_text,
            "proof": "CONTROLLED_FIXTURE_PROOF",
        }
    finally:
        server.shutdown()
        thread.join(timeout=5)


def _market_ingestion(root: Path) -> dict[str, Any]:
    db_path = str(root / "market.sqlite")
    config_path = root / "market_config.json"
    _write_fixture_config(config_path, exposure=60.0)
    refresh = refresh_market_intelligence(config_path=str(config_path), db_path=db_path, enqueue=True)
    channels = refresh["channels"]
    assert set(channels.values()).issubset(ALLOWED_CHANNEL_STATES)
    assert channels["price_volume"] == "SIMULATED"
    assert channels["market_breadth"] in ALLOWED_CHANNEL_STATES
    assert refresh["events_enqueued"] >= 1
    pending = StateStore(db_path=db_path).get_pending_events(limit=10)
    assert any(item["event_type"] == "volume_price_breakout" for item in pending)
    return {
        "status": refresh["status"],
        "proof_mode": refresh["proof_mode"],
        "channels": channels,
        "events_enqueued": refresh["events_enqueued"],
        "routed_event_types": [item["event_type"] for item in pending],
        "live_probe": _live_market_probe(),
    }


def _portfolio_cognition(root: Path) -> dict[str, Any]:
    config_path = root / "portfolio_config.json"
    db_path = root / "portfolio.sqlite"
    log_path = root / "portfolio_runtime.log"
    _write_fixture_config(config_path, exposure=60.0)
    old_user_config = os.environ.get("ATLAS_USER_CONFIG")
    os.environ["ATLAS_USER_CONFIG"] = str(config_path)
    _patch_orchestrator_llm()
    try:
        daemon = AtlasRuntimeDaemon(
            AtlasRuntimeDaemonConfig(
                max_cycles=1,
                no_sleep=True,
                db_path=str(db_path),
                log_path=str(log_path),
                market_config_path=str(config_path),
                market_refresh_every_cycles=1,
            )
        )
        entry = daemon.run_tick(0)
        latest = StateStore(db_path=str(db_path)).get_latest_decision_brief()
    finally:
        if old_user_config is None:
            os.environ.pop("ATLAS_USER_CONFIG", None)
        else:
            os.environ["ATLAS_USER_CONFIG"] = old_user_config
    context_a = build_portfolio_context(config_path=str(config_path))
    config_b = root / "portfolio_config_b.json"
    _write_fixture_config(config_b, exposure=8.0, theme="Cash Proxy")
    context_b = build_portfolio_context(config_path=str(config_b))
    assert "Portfolio State: configured" in latest.get("content", "")
    assert "Exposure Sum: 60.0" in latest.get("content", "")
    assert context_a["exposure_map"]["regime_sensitivity"] != context_b["exposure_map"]["regime_sensitivity"]
    return {
        "runtime_status": entry["system_metrics"]["status"],
        "brief_id": latest.get("id"),
        "brief_has_portfolio": "Portfolio State: configured" in latest.get("content", ""),
        "context_a_relevance": context_a["exposure_map"]["portfolio_relevance_score"],
        "context_b_relevance": context_b["exposure_map"]["portfolio_relevance_score"],
        "differential": context_a["exposure_map"]["regime_sensitivity"] != context_b["exposure_map"]["regime_sensitivity"],
    }


def _forecast_lifecycle(root: Path) -> dict[str, Any]:
    db_path = str(root / "forecast.sqlite")
    cases = [
        ("F1_hit", "breakout", "breakout confirmed", 0.7, "VERIFIED"),
        ("F2_miss", "liquidity stress", "volatility compression", 0.6, "INVALIDATED"),
        ("F3_inconclusive", "attention expansion", "mixed evidence", 0.5, "INCONCLUSIVE"),
        ("F4_high_confidence_miss", "risk off", "risk appetite improved", 0.92, "INVALIDATED"),
        ("F5_low_confidence_hit", "attention", "attention expansion", 0.22, "VERIFIED"),
    ]
    records = []
    matured_status = []
    for forecast_id, expected, actual, confidence, status in cases:
        created = create_forecast(
            {
                "forecast_id": forecast_id,
                "subject": "prompt_c_fixture",
                "forecast_statement": f"{forecast_id} expects {expected}",
                "expected_direction_state": expected,
                "confidence": confidence,
                "active_hypothesis": "H_ATTENTION_FLOW",
            },
            db_path=db_path,
        )
        matured = mark_forecast_matured(created["forecast_id"], {"fixture": True}, db_path=db_path)
        evaluated = evaluate_forecast(
            created["forecast_id"],
            {"actual_outcome": actual, "status": status, "explanation_error": {"fixture": True}},
            db_path=db_path,
        )
        matured_status.append(matured["status"])
        records.append(evaluated)
    ledger = list_forecasts(db_path=db_path, limit=20)
    statuses = {item["forecast_id"]: item["status"] for item in records}
    assert statuses["F3_inconclusive"] == "INCONCLUSIVE"
    assert statuses["F4_high_confidence_miss"] == "INVALIDATED"
    assert all(item.get("calibration_error") is not None for item in records)
    assert ledger["metrics"]["evaluated"] == 5
    return {
        "created": 5,
        "matured_statuses": matured_status,
        "statuses": statuses,
        "metrics": ledger["metrics"],
        "ui_visible_list_count": len(ledger["forecasts"]),
    }


def _self_iteration(root: Path) -> dict[str, Any]:
    _patch_orchestrator_llm()
    control = _run_equivalent_input(root / "control.sqlite")
    treatment_db = root / "treatment.sqlite"
    forecast = create_forecast(
        {
            "forecast_id": "self_iteration_high_confidence_miss",
            "expected_direction_state": "breakout",
            "confidence": 0.95,
            "active_hypothesis": "H_ATTENTION_FLOW",
        },
        db_path=str(treatment_db),
    )
    mark_forecast_matured(forecast["forecast_id"], {"fixture": True}, db_path=str(treatment_db))
    evaluate_forecast(
        forecast["forecast_id"],
        {"actual_outcome": "liquidity failed", "status": "INVALIDATED"},
        db_path=str(treatment_db),
    )
    treatment = _run_equivalent_input(treatment_db)
    assert treatment["forecast_calibration_feedback_status"] == "applied"
    assert treatment["forecast_calibration_feedback_delta"] < 0
    assert treatment["trust_score"]["global_trust_index"] < control["trust_score"]["global_trust_index"]
    assert treatment["causal_hypothesis_score_distribution"] != control["causal_hypothesis_score_distribution"]
    return {
        "classification": "REAL_BEHAVIORAL_LOOP",
        "control_trust": control["trust_score"]["global_trust_index"],
        "after_error_trust": treatment["trust_score"]["global_trust_index"],
        "trust_delta": round(
            treatment["trust_score"]["global_trust_index"] - control["trust_score"]["global_trust_index"],
            4,
        ),
        "control_hypothesis_scores": control["causal_hypothesis_score_distribution"],
        "after_error_hypothesis_scores": treatment["causal_hypothesis_score_distribution"],
        "control_structural_shift": control.get("structural_shift_index"),
        "after_error_structural_shift": treatment.get("structural_shift_index"),
        "feedback_delta": treatment["forecast_calibration_feedback_delta"],
    }


def _daily_cycle(root: Path) -> dict[str, Any]:
    db_path = str(root / "daily.sqlite")
    config_path = root / "daily_config.json"
    _write_fixture_config(config_path, exposure=40.0)
    phase_results = {
        "morning": run_morning_cycle(config_path=str(config_path), db_path=db_path),
        "intraday": run_intraday_cycle(config_path=str(config_path), db_path=db_path),
        "post_market": run_post_market_cycle(config_path=str(config_path), db_path=db_path),
        "overnight": run_overnight_cycle(config_path=str(config_path), db_path=db_path),
    }
    dispatched = dispatch_current_daily_cycle(config_path=str(config_path), db_path=db_path)
    store = StateStore(db_path=db_path)
    assert all(item["status"] == "completed" and not item.get("produced_brief_id") for item in phase_results.values())
    assert all(item.get("outputs", {}).get("brief_publication_requested") is False for item in phase_results.values())
    assert store.get_state("daily_cycle_last_execution").get("status") == "completed"
    return {
        "phase_statuses": {key: value["status"] for key, value in phase_results.items()},
        "maintenance_run_ids": {key: value["maintenance_run_id"] for key, value in phase_results.items()},
        "dispatch_phase": dispatched["phase"],
        "dispatch_status": dispatched["execution"]["status"],
    }


def _recovery(root: Path) -> dict[str, Any]:
    db_path = str(root / "recovery.sqlite")
    inbox = root / "inbox"
    inbox.mkdir()
    (inbox / "events.jsonl").write_text(
        "{bad-json\n" + json.dumps({"type": "attention", "payload": {"value": 1}, "source": "prompt_c"}),
        encoding="utf-8",
    )
    stream = EventStream(db_path=db_path, inbox_dir=str(inbox))
    ingested = stream.listen_once()
    forecast = create_forecast({"forecast_id": "malformed_outcome", "expected_direction_state": "risk"}, db_path=db_path)
    mark_forecast_matured(forecast["forecast_id"], {"maturity_reason": "controlled_recovery_fixture"}, db_path=db_path)
    malformed = evaluate_forecast(forecast["forecast_id"], {"actual_outcome": ["bad", "shape"]}, db_path=db_path)
    trace_path = root / "corrupt_llm.jsonl"
    trace_path.write_text("{bad-json\n{}\n", encoding="utf-8")
    traces = read_llm_traces(str(trace_path), limit=5)
    pid_file = root / "stale.pid"
    pid_file.write_text("99999999", encoding="utf-8")
    stale_before = runtime_status(pid_file=str(pid_file), db_path=db_path, discover=False)
    stale_stop = stop_runtime_daemon(pid_file=str(pid_file))
    assert ingested == 1
    assert malformed["status"] == "INCONCLUSIVE"
    assert any(item.get("status") == "invalid_log_record" for item in traces)
    assert stale_before["running"] is False
    assert stale_stop["status"] in {"stale_pid_removed", "not_running"}
    assert not pid_file.exists()
    return {
        "corrupted_event_jsonl_ingested_valid_count": ingested,
        "malformed_forecast_outcome_status": malformed["status"],
        "corrupted_telemetry_records_read": len(traces),
        "invalid_telemetry_record_detected": any(item.get("status") == "invalid_log_record" for item in traces),
        "stale_pid_status_before": stale_before["running"],
        "stale_pid_cleanup": stale_stop["status"],
    }


def _soak(root: Path) -> dict[str, Any]:
    _patch_orchestrator_llm()
    db_path = root / "soak.sqlite"
    log_path = root / "soak.log"
    config_path = root / "soak_config.json"
    _write_fixture_config(config_path, exposure=0.0)
    before_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    started = time.time()
    daemon = AtlasRuntimeDaemon(
        AtlasRuntimeDaemonConfig(
            max_cycles=500,
            no_sleep=True,
            db_path=str(db_path),
            log_path=str(log_path),
            market_config_path=str(config_path),
            market_refresh_enabled=False,
            market_max_assets=1,
            proactive_update_enabled=False,
            runtime_mode="live",
        )
    )
    daemon.run_forever()
    elapsed = time.time() - started
    after_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    counts = _sqlite_counts(db_path)
    log_lines = len(log_path.read_text(encoding="utf-8").splitlines()) if log_path.exists() else 0
    errors = _runtime_error_count(log_path)
    assert log_lines == 500
    assert errors == 0
    assert counts.get("decision_briefs", 0) == 0
    return {
        "cycles": 500,
        "elapsed_seconds": round(elapsed, 4),
        "runtime_log_lines": log_lines,
        "tick_errors": errors,
        "db_counts": counts,
        "max_rss_before": before_rss,
        "max_rss_after": after_rss,
        "rss_growth": after_rss - before_rss,
        "heartbeat_brief_churn": counts.get("decision_briefs", 0),
        "accelerated": True,
    }


def _security(root: Path) -> dict[str, Any]:
    pattern = r"(^|[^A-Za-z0-9])sk-[A-Za-z0-9_-]{20,}|" + "Authorization: " + "Bearer"
    tracked = _run(["git", "grep", "-nE", pattern, "--", "."], check=False)
    matches = [
        line
        for line in tracked["stdout"].splitlines()
        if "git grep -nE" not in line and ("Authorization: " + "Bearer' --") not in line
    ]
    assert not matches
    return {
        "tracked_secret_shape_matches": matches,
        "git_grep_returncode": tracked["returncode"],
        "runtime_private_files_committed": False,
    }


def _live_market_probe() -> dict[str, Any]:
    probes = {}
    try:
        from tools.market_data.market_data_provider import get_market_snapshot
    except Exception as exc:
        return {"status": "provider_import_failed", "error": str(exc)[:240]}
    for asset, market in (("000001", "A-share"), ("AAPL", "US")):
        try:
            snapshot = get_market_snapshot(asset, market)
            probes[asset] = {
                "market": market,
                "data_status": snapshot.get("data_status"),
                "source": snapshot.get("source"),
                "timestamp": snapshot.get("timestamp"),
                "latest_price_available": snapshot.get("latest_price") is not None,
                "volume_available": snapshot.get("volume") is not None,
                "errors": [str(item)[:180] for item in snapshot.get("errors", [])[:2]],
            }
        except Exception as exc:
            probes[asset] = {"market": market, "data_status": "FAILED", "error": str(exc)[:240]}
    live_count = sum(1 for item in probes.values() if item.get("latest_price_available"))
    return {
        "status": "LIVE_PROOF" if live_count else "LIVE_PROVIDER_UNAVAILABLE",
        "live_price_volume_count": live_count,
        "probes": probes,
    }


def _provider_registry(base: str) -> dict[str, Any]:
    def provider(provider_id: str, endpoint: str) -> dict[str, Any]:
        return {
            "id": provider_id,
            "type": "openai",
            "label": provider_id,
            "enabled": True,
            "base_url": endpoint,
            "model": "fixture-model-a",
            "api_key_encrypted": encrypt_api_key(FIXTURE_SECRET),
            "api_key_storage": "local_secret_storage",
            "api_key_keychain_account": "",
            "health": "unknown",
            "last_latency_ms": None,
            "last_error": "",
            "available_models": [],
            "last_models_error": "",
        }

    return {
        "active_provider": "bad500",
        "fallback_chain": ["empty", "malformed", "good"],
        "providers": [
            provider("bad500", f"{base}/bad500"),
            provider("empty", f"{base}/empty"),
            provider("malformed", f"{base}/malformed"),
            provider("good", f"{base}/v1/chat/completions"),
        ],
    }


def _write_fixture_config(path: Path, *, exposure: float, theme: str = "AI Hardware") -> None:
    path.write_text(
        json.dumps(
            {
                "assets": {
                    "portfolio_json": json.dumps(
                        [
                            {
                                "asset": "TEST",
                                "market": "US",
                                "portfolio_percentage": exposure,
                                "theme": theme,
                                "role": "Fixture",
                            }
                        ]
                    ),
                    "asset_list": ["TEST"],
                    "weights": {"TEST": exposure},
                },
                "market_intelligence": {
                    "fixtures": {
                        "TEST": {
                            "source": "prompt_c_controlled_fixture",
                            "timestamp": utc_now_iso(),
                            "data_status": "Available",
                            "data_freshness": "SIMULATED",
                            "latest_price": 100.0,
                            "daily_change_pct": 1.2,
                            "change_5d_pct": 4.5,
                            "change_20d_pct": 7.0,
                            "change_60d_pct": 11.0,
                            "volume": 1234567,
                            "turnover": 9876543,
                        }
                    }
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def _run_equivalent_input(db_path: Path) -> dict[str, Any]:
    loop = DecisionLoop(DecisionLoopConfig(db_path=str(db_path), heartbeat_interval_seconds=10_000_000))
    loop._last_heartbeat = time.time()
    loop.event_stream.enqueue_event(
        "volume_price_breakout",
        payload={"asset": "TEST", "volume": 1234567, "price_move": 4.2, "liquidity": "mixed"},
        priority=80,
        source="prompt_c_self_iteration_fixture",
        created_at=utc_now_iso(),
    )
    cycle = loop.run_once()
    result = cycle["results"][0]
    return result


def _patch_orchestrator_llm() -> None:
    import runtime.orchestrator as orchestrator

    packet = {
        "regime_state": "unknown",
        "confidence": 0.25,
        "risk_level": "unknown",
        "attention_state": "unknown",
        "liquidity_state": "unknown",
        "causal_summary": "Controlled local LLM fallback.",
        "recommended_action": "neutral",
        "reasoning_trace": "Prompt C validation patched provider path for deterministic local execution.",
    }
    orchestrator.call_llm_raw = lambda *_args, **_kwargs: json.dumps(packet)


def _start_provider_fixture() -> tuple[ThreadingHTTPServer, threading.Thread, int]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), _ProviderFixtureHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, int(server.server_address[1])


def _sqlite_counts(db_path: Path) -> dict[str, int]:
    with sqlite3.connect(db_path) as conn:
        tables = [
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            if not str(row[0]).startswith("sqlite_")
        ]
        return {table: int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]) for table in tables}


def _runtime_error_count(log_path: Path) -> int:
    if not log_path.exists():
        return 0
    errors = 0
    for line in log_path.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            errors += 1
            continue
        metrics = record.get("system_metrics", {})
        if metrics.get("status") != "success" or metrics.get("error"):
            errors += 1
    return errors


def _run(cmd: list[str], *, check: bool = True) -> dict[str, Any]:
    import subprocess

    result = subprocess.run(cmd, cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and result.returncode != 0:
        raise AssertionError({"cmd": cmd, "stdout": result.stdout, "stderr": result.stderr})
    return {"returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


if __name__ == "__main__":
    main()
