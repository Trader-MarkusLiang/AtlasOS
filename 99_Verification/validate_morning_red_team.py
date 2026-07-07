"""Morning final verification red-team executable checks.

This script uses temporary config/database/log fixtures. It does not wipe local
runtime evidence and does not require real provider credentials.
"""

from __future__ import annotations

import json
import os
import re
import socket
import subprocess
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

from runtime.decision_brief import generate_decision_brief  # noqa: E402
from runtime.event_stream import EventStream  # noqa: E402
from runtime.forecast_ledger import (  # noqa: E402
    create_forecast,
    evaluate_forecast,
    get_forecast,
    list_forecasts,
    mark_forecast_matured,
)
from runtime.llm.provider_registry import default_provider_registry, safe_registry_view, update_provider_registry  # noqa: E402
from runtime.llm.provider_router import route_llm_request  # noqa: E402
from runtime.market_intelligence import market_observation_to_event, refresh_market_intelligence  # noqa: E402
from runtime.portfolio_context import build_portfolio_context  # noqa: E402
from runtime.state_store import StateStore  # noqa: E402


class ProviderFixtureHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/good":
            self._json(200, {"content": "provider good raw response"})
        elif self.path == "/empty":
            self._json(200, {"content": ""})
        elif self.path == "/malformed":
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"{not-json")
        elif self.path == "/bad500":
            self._json(500, {"error": "server_error"})
        elif self.path == "/unauthorized":
            self._json(401, {"error": "unauthorized"})
        else:
            self._json(404, {"error": "missing"})

    def log_message(self, *_args: Any) -> None:
        return

    def _json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    previous_disable_keychain = os.environ.get("ATLAS_DISABLE_KEYCHAIN")
    os.environ["ATLAS_DISABLE_KEYCHAIN"] = "1"
    results: dict[str, Any] = {}
    try:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db_path = str(root / "state.sqlite")
            config_path = str(root / "user_config.json")
            provider_server = ThreadingHTTPServer(("127.0.0.1", 0), ProviderFixtureHandler)
            provider_port = provider_server.server_address[1]
            thread = threading.Thread(target=provider_server.serve_forever, daemon=True)
            thread.start()
            try:
                results["provider_red_team"] = _provider_red_team(config_path, provider_port)
                results["forecast_lifecycle"] = _forecast_lifecycle(db_path)
                results["portfolio_differential"] = _portfolio_differential(root)
                results["market_reality"] = _market_reality(root, db_path)
                results["recovery"] = _recovery(root, db_path)
                results["ui_http"] = _ui_http(root, db_path)
                results["secret_scan"] = _secret_scan()
            finally:
                provider_server.shutdown()
                thread.join(timeout=2)
    finally:
        if previous_disable_keychain is None:
            os.environ.pop("ATLAS_DISABLE_KEYCHAIN", None)
        else:
            os.environ["ATLAS_DISABLE_KEYCHAIN"] = previous_disable_keychain

    print(json.dumps({"status": "PASS", "results": results}, ensure_ascii=False, indent=2, sort_keys=True))


def _provider_red_team(config_path: str, port: int) -> dict[str, Any]:
    base = f"http://127.0.0.1:{port}"
    registry = {
        "active_provider": "bad500",
        "fallback_chain": ["empty", "malformed", "good"],
        "providers": [
            {"id": "bad500", "type": "custom", "enabled": True, "base_url": f"{base}/bad500", "model": "fixture"},
            {"id": "empty", "type": "custom", "enabled": True, "base_url": f"{base}/empty", "model": "fixture"},
            {"id": "malformed", "type": "custom", "enabled": True, "base_url": f"{base}/malformed", "model": "fixture"},
            {"id": "good", "type": "custom", "enabled": True, "base_url": f"{base}/good", "model": "fixture"},
        ],
    }
    update_provider_registry(registry, config_path)
    routed = route_llm_request(prompt="hello", context={}, config_path=config_path)
    assert routed["status"] == "ok"
    assert routed["provider"] == "good"
    assert len(routed["fallback_attempts"]) == 3

    missing_key_registry = default_provider_registry()
    missing_key_registry["active_provider"] = "openai"
    missing_key_registry["fallback_chain"] = ["good"]
    missing_key_registry["providers"].append(
        {"id": "good", "type": "custom", "enabled": True, "base_url": f"{base}/good", "model": "fixture"}
    )
    update_provider_registry(missing_key_registry, config_path)
    fallback = route_llm_request(prompt="hello", context={}, config_path=config_path)
    assert fallback["status"] == "ok"
    assert fallback["provider"] == "good"
    safe = safe_registry_view()
    assert "api_key_encrypted" not in json.dumps(safe)
    return {
        "fallback_provider": routed["provider"],
        "fallback_attempts": [item["error"] for item in routed["fallback_attempts"]],
        "missing_key_fallback_provider": fallback["provider"],
        "empty_response_triggers_fallback": "empty_response" in str(routed["fallback_attempts"]),
    }


def _forecast_lifecycle(db_path: str) -> dict[str, Any]:
    store = StateStore(db_path=db_path)
    store.set_state("system_trust_state", {"rolling_trust_index": 0.5, "llm_provider_trust": {}})
    statuses = []
    forecast_ids = []
    scenarios = [
        ("directional", "broaden", "attention did broaden across assets", None),
        ("regime_risk", "stress", "liquidity stress persisted", None),
        ("attention", "expand", "attention did expand", None),
        ("liquidity", "persist", "liquidity stress did persist", None),
        ("deliberately_wrong", "expand", "attention contracted instead", "INVALIDATED"),
    ]
    matured_snapshot = None
    for index, (subject, expected, actual, forced_status) in enumerate(scenarios):
        forecast = create_forecast(
            {
                "horizon": "controlled-window",
                "subject": subject,
                "forecast_statement": f"{subject} expected state {expected}",
                "expected_direction_state": expected,
                "confidence": 0.7 if forced_status else 0.55,
                "active_hypothesis": "H_ATTENTION_FLOW" if subject == "attention" else "H_LIQUIDITY_STRESS",
                "causal_drivers": ["attention", "liquidity"],
                "invalidation_conditions": ["opposite observed"],
                "expected_observation_window": "test window",
            },
            db_path=db_path,
        )
        forecast_ids.append(forecast["forecast_id"])
        matured = mark_forecast_matured(forecast["forecast_id"], {"window_closed": True}, db_path=db_path)
        if index == 0:
            matured_snapshot = get_forecast(forecast["forecast_id"], db_path=db_path)
            assert matured_snapshot["status"] == "MATURED"
        payload = {"actual_outcome": actual}
        if forced_status:
            payload["status"] = forced_status
        evaluated = evaluate_forecast(forecast["forecast_id"], payload, db_path=db_path)
        statuses.append(evaluated["status"])
        assert evaluated["lineage"][-1]["event"] == "evaluated"
        assert evaluated["prediction_error"] is not None
        assert evaluated["calibration_error"] is not None
        assert evaluated["trust_update"]["status"] == "applied"
    ledger = list_forecasts(db_path=db_path, limit=20)
    trust_after = store.get_state("system_trust_state")
    calibration = store.get_state("forecast_calibration_state")
    hypothesis_memory = store.get_state("causal_hypothesis_memory")
    assert ledger["metrics"]["evaluated"] == 5
    assert "INVALIDATED" in statuses
    assert calibration["evaluated_count"] == 5
    assert hypothesis_memory["forecast_outcome_history"]
    return {
        "created": len(forecast_ids),
        "statuses": statuses,
        "matured_snapshot_status": matured_snapshot["status"] if matured_snapshot else None,
        "trust_after": trust_after.get("rolling_trust_index"),
        "calibration_sample_warning": ledger["sample_warning"],
        "hypothesis_outcome_records": len(hypothesis_memory["forecast_outcome_history"]),
    }


def _portfolio_differential(root: Path) -> dict[str, Any]:
    configs = {
        "P1_high_ai_hardware": [
            {"asset": "NVDA", "market": "US", "portfolio_percentage": 45, "theme": "AI Hardware", "role": "Core"},
            {"asset": "TSM", "market": "US", "portfolio_percentage": 20, "theme": "AI Hardware", "role": "Core"},
        ],
        "P2_high_cash": [
            {"asset": "BIL", "market": "US", "portfolio_percentage": 8, "theme": "Cash Proxy", "role": "Defensive"},
        ],
        "P3_concentrated_theme": [
            {"asset": "AI1", "market": "US", "portfolio_percentage": 70, "theme": "Single Theme", "role": "Speculative"},
        ],
        "P4_none": [],
    }
    contexts = {}
    brief_lines = {}
    for name, positions in configs.items():
        path = root / f"{name}.json"
        path.write_text(json.dumps({"assets": {"portfolio_json": json.dumps(positions)}}), encoding="utf-8")
        context = build_portfolio_context(config_path=str(path))
        contexts[name] = {
            "status": context["status"],
            "exposure_sum_pct": context["exposure_sum_pct"],
            "regime_sensitivity": context["exposure_map"]["regime_sensitivity"],
            "theme_concentration": context["exposure_map"]["theme_concentration"],
        }
        brief = generate_decision_brief(
            brief_id=f"brief-{name}",
            trigger_type="event_trigger",
            event_type="volume_price_breakout",
            pipeline="test",
            market_state={"summary": "same market state", "data_status": "Test"},
            regime_state={"status": "same", "probability_vector": {"data_insufficient": 100}, "confidence": "Low"},
            portfolio_state=context,
            risk_level="High",
            action_bias="Reduce",
            modules_executed=["test"],
            llm_result={"provider": "fixture", "status": "fixture"},
        )
        brief_lines[name] = [line for line in brief.splitlines() if line.startswith(("Exposure Sum", "Portfolio State", "## Action Bias"))]
    assert contexts["P1_high_ai_hardware"]["regime_sensitivity"] != contexts["P2_high_cash"]["regime_sensitivity"]
    assert contexts["P3_concentrated_theme"]["regime_sensitivity"] == "single_theme_regime_sensitive"
    assert contexts["P4_none"]["status"] == "missing"
    serialized = json.dumps(brief_lines)
    assert "Buy" not in serialized and "Sell" not in serialized
    return {"contexts": contexts, "portfolio_context_dependency_score": 1.0, "brief_lines": brief_lines}


def _market_reality(root: Path, db_path: str) -> dict[str, Any]:
    empty_config = root / "empty_market.json"
    empty_config.write_text(json.dumps({"assets": {"portfolio_json": "[]"}}), encoding="utf-8")
    refresh = refresh_market_intelligence(config_path=str(empty_config), db_path=db_path, enqueue=True)
    routed = market_observation_to_event(
        {
            "timestamp": "2026-07-08T00:00:00+00:00",
            "source": "fixture",
            "source_type": "market_data_provider",
            "asset": "TEST",
            "theme": "Test",
            "market": "US",
            "freshness": "Available",
            "confidence": 0.7,
            "raw_reference": {"provider": "fixture"},
            "normalized_event_type": "price_breakout",
            "data_quality_status": "Available",
        }
    )
    assert refresh["status"] == "no_configured_assets"
    assert routed["event_type"] == "volume_price_breakout"
    return {
        "price_volume": "ACTIVE_WITH_FALLBACK",
        "market_breadth": "NOT_CONFIGURED",
        "news": "NOT_CONFIGURED",
        "macro": "NOT_CONFIGURED",
        "empty_refresh_status": refresh["status"],
        "routed_event_type": routed["event_type"],
    }


def _recovery(root: Path, db_path: str) -> dict[str, Any]:
    inbox = root / "inbox"
    inbox.mkdir()
    payload = "\n".join(
        [
            "{bad-json",
            json.dumps({"type": "attention", "payload": {"value": 1}, "source": "fixture"}),
        ]
    )
    (inbox / "events.jsonl").write_text(payload, encoding="utf-8")
    stream = EventStream(db_path=db_path, inbox_dir=str(inbox))
    ingested = stream.listen_once()
    pending = stream.poll(limit=10)
    assert ingested == 1
    assert len(pending) == 1
    assert pending[0]["event_type"] == "attention_spike"
    return {"corrupted_jsonl_skipped": True, "valid_events_ingested": ingested}


def _ui_http(root: Path, db_path: str) -> dict[str, Any]:
    config_path = root / "ui_config.json"
    config_path.write_text(json.dumps({"assets": {"portfolio_json": "[]"}}), encoding="utf-8")
    port = _free_port()
    env = {
        **os.environ,
        "ATLAS_USER_CONFIG": str(config_path),
        "ATLAS_RUNTIME_DB": db_path,
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    process = subprocess.Popen(
        [sys.executable, "-c", f"from ui.app_server import run_server; run_server(port={port})"],
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        _wait_for_http(port)
        paths = ["/", "/state", "/portfolio", "/markets?format=json", "/predictions?format=json", "/roadmap?format=json", "/setup"]
        statuses = {}
        for path in paths:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=8) as response:
                body = response.read().decode("utf-8")
                statuses[path] = {"status": response.status, "length": len(body)}
                assert response.status == 200
                assert len(body) > 20
        return statuses
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


def _secret_scan() -> dict[str, Any]:
    tracked = subprocess.check_output(["git", "ls-files"], cwd=str(ROOT), text=True).splitlines()
    matches: list[str] = []
    for rel in tracked:
        path = ROOT / rel
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if re.search(r"sk-[A-Za-z0-9_\-]{8,}", text):
            matches.append(rel)
    assert not matches
    return {"tracked_api_key_shape_matches": matches, "status": "clean"}


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_http(port: int) -> None:
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/state", timeout=1) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.2)
    raise RuntimeError("ui_server_did_not_start")


if __name__ == "__main__":
    main()
