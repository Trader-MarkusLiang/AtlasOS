"""Validate Atlas task-aware multi-LLM routing with isolated runtime evidence.

Linked Issue: ISSUE-2026-060.
"""

from __future__ import annotations

import json
import os
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
os.sys.path.insert(0, str(ROOT))

from runtime.atlas_runtime_daemon import AtlasRuntimeDaemon, AtlasRuntimeDaemonConfig
from runtime.decision_loop import DecisionLoop, DecisionLoopConfig
from runtime.llm.provider_registry import (
    encrypt_api_key,
    load_provider_registry,
    provider_api_key,
    safe_registry_view,
    save_provider_registry,
)
from runtime.llm.provider_router import route_llm_request
from runtime.llm.task_routing import load_task_routes, route_task_request, safe_task_routes_view, save_task_routes
from runtime.orchestrator import _parse_workhorse_packet, _run_task_with_cache, _workhorse_prompt
from runtime.state_store import StateStore
from runtime.telemetry.llm_trace_logger import read_llm_traces
from ui.app_server import append_chat_event
from ui.pages.settings import load_user_config, save_user_config


SECRET = "fixture_secret_never_log"


class FixtureHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("content-length", "0") or 0)
        raw = self.rfile.read(length).decode("utf-8")
        try:
            payload = json.loads(raw or "{}")
        except json.JSONDecodeError:
            payload = {}
        model = str(payload.get("model") or "")
        if model == "http-401":
            self._json({}, status=401)
            return
        if model == "http-429":
            self._json({}, status=429)
            return
        if model == "model-not-found":
            self._json({"error": "model_not_found"}, status=404)
            return
        if model == "timeout-model":
            time.sleep(0.25)
        if model == "malformed-model":
            body = b"{not-json"
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        content = _content_for_model(model)
        self._json(
            {
                "choices": [{"message": {"content": content}}],
                "usage": {"prompt_tokens": 120, "completion_tokens": 40, "total_tokens": 160},
            }
        )

    def log_message(self, _format: str, *_args: Any) -> None:
        return

    def _json(self, value: dict[str, Any], status: int = 200) -> None:
        body = json.dumps(value).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except BrokenPipeError:
            pass


def _content_for_model(model: str) -> str:
    if model in {"work-model", "work-fallback"}:
        return json.dumps(
            {
                "status": "ok",
                "query_intent": "Review supplied portfolio-relevant evidence.",
                "signals": [
                    {
                        "claim": "User supplied a research question.",
                        "source": "ui_chat",
                        "timestamp": "Unknown",
                        "evidence_type": "User Signal",
                        "confidence": 1.0,
                    }
                ],
                "unknowns": ["External evidence is not included in this fixture."],
            }
        )
    if model == "research-model":
        return json.dumps(
            {
                "status": "ok",
                "summary": "Evidence is limited to a user question and deterministic runtime context.",
                "portfolio_relevance": ["Review configured exposure without changing portfolio authority."],
                "causal_factors": ["No external causal evidence supplied."],
                "counter_evidence": ["No independent market source in this fixture."],
                "hypotheses": ["The question may require a later evidence refresh."],
                "uncertainties": ["Current market evidence is incomplete."],
            }
        )
    if model in {"decision-model", "decision-fallback"}:
        return json.dumps(
            {
                "regime_state": "NORMAL",
                "confidence": 0.42,
                "risk_level": "medium",
                "attention_state": "mixed",
                "liquidity_state": "unknown",
                "causal_summary": "Available evidence is incomplete and does not justify a strong action.",
                "recommended_action": "observe",
                "reasoning_trace": "Validated decision route fixture output.",
            }
        )
    if model == "empty-model":
        return ""
    return _content_for_model("decision-model")


def main() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        server = ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base_url = f"http://127.0.0.1:{server.server_address[1]}/v1/chat/completions"
        config_path = root / "user_config.json"
        trace_path = root / "llm_traces.jsonl"
        db_path = root / "runtime.sqlite"
        inbox_path = root / "user_event.jsonl"
        old_env = {key: os.environ.get(key) for key in ("ATLAS_USER_CONFIG", "ATLAS_LLM_TRACE_LOG", "ATLAS_DISABLE_KEYCHAIN")}
        os.environ["ATLAS_USER_CONFIG"] = str(config_path)
        os.environ["ATLAS_LLM_TRACE_LOG"] = str(trace_path)
        os.environ["ATLAS_DISABLE_KEYCHAIN"] = "1"
        try:
            _write_fixture_config(config_path, base_url)
            _assert_configuration(config_path)
            _assert_provider_swap_isolation(config_path)
            _assert_role_fallback_and_failures(config_path)
            _assert_failed_task_retry(config_path, root)
            _write_fixture_config(config_path, base_url)
            _assert_ui_to_runtime_roles(config_path, trace_path, db_path, inbox_path, root)
            _assert_proactive_cycle(config_path, trace_path, root)
            _assert_failed_decision_isolation(config_path, trace_path, root)
            _write_fixture_config(config_path, base_url)
            _assert_heartbeat_cost_safety(config_path, trace_path, db_path, root)
            _assert_security(config_path, trace_path)
        finally:
            server.shutdown()
            server.server_close()
            for key, value in old_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
        print("Task-Aware Multi-LLM Routing v1.5 validation PASS")


def _write_fixture_config(path: Path, base_url: str) -> None:
    providers = []
    for provider_id, model in (
        ("workhorse_primary", "work-model"),
        ("workhorse_fallback", "work-fallback"),
        ("research_primary", "research-model"),
        ("decision_primary", "decision-model"),
        ("decision_fallback", "decision-fallback"),
    ):
        providers.append(
            {
                "id": provider_id,
                "type": "openai",
                "label": provider_id.replace("_", " ").title(),
                "enabled": True,
                "base_url": base_url,
                "model": model,
                "api_key_encrypted": encrypt_api_key(SECRET),
                "api_key_storage": "local_secret_storage",
                "api_key_keychain_account": "",
                "health": "healthy",
                "last_latency_ms": 1,
                "last_error": "",
                "available_models": [model, "http-401", "http-429", "timeout-model", "empty-model", "malformed-model", "model-not-found"],
                "reasoning_effort": "",
                "timeout_seconds": 1,
                "input_cost_per_million": 1.0,
                "output_cost_per_million": 2.0,
            }
        )
    registry = {
        "active_provider": "decision_primary",
        "fallback_chain": ["decision_fallback"],
        "strict_provider_list": True,
        "providers": providers,
    }
    save_provider_registry(registry, str(path))
    save_task_routes(
        {
            "workhorse": {
                "enabled": True,
                "provider_id": "workhorse_primary",
                "model": "work-model",
                "fallback_chain": ["workhorse_fallback"],
                "timeout_seconds": 1,
                "max_output_tokens": 2000,
                "reasoning_effort": "",
            },
            "research": {
                "enabled": True,
                "provider_id": "research_primary",
                "model": "research-model",
                "fallback_chain": [],
                "timeout_seconds": 1,
                "max_output_tokens": 4000,
                "reasoning_effort": "",
            },
            "decision": {
                "enabled": True,
                "provider_id": "decision_primary",
                "model": "decision-model",
                "fallback_chain": ["decision_fallback"],
                "timeout_seconds": 1,
                "max_output_tokens": 4000,
                "reasoning_effort": "medium",
            },
        },
        str(path),
    )


def _assert_configuration(path: Path) -> None:
    registry = load_provider_registry(str(path))
    routes = load_task_routes(str(path))
    safe = safe_task_routes_view(routes, registry)
    assert set(safe) == {"workhorse", "research", "decision"}
    assert all(safe[role]["route_status"] == "ACTIVE" for role in safe)
    assert safe["workhorse"]["provider_id"] != safe["decision"]["provider_id"]
    assert "api_key_encrypted" not in json.dumps(safe_registry_view(registry))
    payload = {
        "llm_registry": safe_registry_view(registry),
        "llm_task_routes": routes,
        "system": {"tick_interval": 60, "proactive_update_interval_seconds": 7200},
        "assets": {},
        "ui": {"language": "en"},
    }
    saved = save_user_config(payload, str(path))
    assert saved["status"] == "saved"
    loaded = load_user_config(str(path))
    assert loaded["llm_task_routes"]["decision"]["provider_id"] == "decision_primary"
    preserved = load_provider_registry(str(path))
    assert all(provider_api_key(provider) == SECRET for provider in preserved["providers"])


def _assert_provider_swap_isolation(path: Path) -> None:
    original = path.read_text(encoding="utf-8")
    config = json.loads(original)
    decision_before = dict(config["llm_task_routes"]["decision"])
    config["llm_task_routes"]["workhorse"]["provider_id"] = "workhorse_fallback"
    config["llm_task_routes"]["workhorse"]["model"] = "work-fallback"
    path.write_text(json.dumps(config), encoding="utf-8")
    routes = load_task_routes(str(path))
    assert routes["workhorse"]["provider_id"] == "workhorse_fallback"
    assert routes["decision"] == decision_before
    path.write_text(original, encoding="utf-8")


def _assert_role_fallback_and_failures(path: Path) -> None:
    original = path.read_text(encoding="utf-8")
    config = json.loads(path.read_text(encoding="utf-8"))
    config["llm_task_routes"]["workhorse"]["model"] = "http-429"
    path.write_text(json.dumps(config), encoding="utf-8")
    result = route_task_request("workhorse", "fallback test", {"runtime_context": {"trigger_type": "fixture"}}, config_path=str(path))
    assert result["status"] == "ok"
    assert result["provider"] == "workhorse_fallback"
    assert result["model"] == "work-fallback"
    assert result["fallback_attempts"][0]["provider"] == "workhorse_primary"
    assert "http_429" in result["fallback_attempts"][0]["error"]

    for model, expected in (
        ("http-401", "http_401"),
        ("http-429", "http_429"),
        ("empty-model", "empty_response"),
        ("malformed-model", "malformed_response"),
        ("model-not-found", "http_404"),
        ("timeout-model", "timed out"),
    ):
        routed = route_llm_request(
            prompt="failure test",
            provider_id="workhorse_primary",
            model=model,
            fallback_chain=[],
            request_options={"timeout_seconds": 0.05, "max_output_tokens": 128, "reasoning_effort": ""},
            config_path=str(path),
        )
        assert routed["status"] == "failsafe", (model, routed)
        errors = " ".join(str(item.get("error")) for item in routed["fallback_attempts"])
        assert expected in errors, (model, errors)

    config = json.loads(original)
    config["llm_task_routes"]["workhorse"]["model"] = "http-401"
    for provider in config["llm_registry"]["providers"]:
        if provider.get("id") == "workhorse_fallback":
            provider["model"] = "http-429"
    path.write_text(json.dumps(config), encoding="utf-8")
    failed = route_task_request(
        "workhorse",
        "all fallback failure",
        {"runtime_context": {"trigger_type": "fixture"}},
        config_path=str(path),
    )
    assert failed["status"] == "failsafe"
    assert [item["provider"] for item in failed["fallback_attempts"]] == [
        "workhorse_primary",
        "workhorse_fallback",
    ]
    path.write_text(original, encoding="utf-8")


def _assert_failed_task_retry(config_path: Path, root: Path) -> None:
    original = config_path.read_text(encoding="utf-8")
    config = json.loads(original)
    config["llm_task_routes"]["workhorse"]["model"] = "empty-model"
    config["llm_task_routes"]["workhorse"]["fallback_chain"] = []
    config_path.write_text(json.dumps(config), encoding="utf-8")
    store = StateStore(db_path=str(root / "retryable-task.sqlite"))
    context = {"test": True, "runtime_context": {"trigger_type": "retryable_task_fixture"}}
    first = _run_task_with_cache(
        role="workhorse",
        prompt=_workhorse_prompt(),
        context=context,
        input_hash="stable-retry-input",
        store=store,
        parser=_parse_workhorse_packet,
    )
    assert first["status"] == "failsafe"
    assert "workhorse" not in store.get_state("llm_task_runtime_state")

    config_path.write_text(original, encoding="utf-8")
    second = _run_task_with_cache(
        role="workhorse",
        prompt=_workhorse_prompt(),
        context=context,
        input_hash="stable-retry-input",
        store=store,
        parser=_parse_workhorse_packet,
    )
    assert second["status"] == "ok"
    assert second["cache_status"] == "miss"
    third = _run_task_with_cache(
        role="workhorse",
        prompt=_workhorse_prompt(),
        context=context,
        input_hash="stable-retry-input",
        store=store,
        parser=_parse_workhorse_packet,
    )
    assert third["status"] == "cached"
    assert third["cache_status"] == "hit"


def _assert_ui_to_runtime_roles(
    config_path: Path,
    trace_path: Path,
    db_path: Path,
    inbox_path: Path,
    root: Path,
) -> None:
    if trace_path.exists():
        trace_path.unlink()
    append_chat_event("Review the latest evidence relevant to my configured portfolio.", inbox_path=str(inbox_path))
    daemon = AtlasRuntimeDaemon(
        AtlasRuntimeDaemonConfig(
            interval_seconds=60,
            max_cycles=1,
            log_path=str(root / "runtime.jsonl"),
            db_path=str(db_path),
            inbox_dir=str(root / "events"),
            ui_inbox_path=str(inbox_path),
            no_sleep=True,
            market_refresh_enabled=False,
            market_config_path=str(config_path),
            proactive_update_enabled=False,
            runtime_mode="live",
        )
    )
    entry = daemon.run_tick(0)
    assert entry["system_metrics"]["status"] == "success"
    traces = read_llm_traces(str(trace_path), limit=20)
    roles = [trace.get("task_role") for trace in traces]
    assert roles == ["workhorse", "research", "decision"], roles
    assert all(trace.get("status") == "ok" for trace in traces)
    assert all(trace.get("total_tokens") == 160 for trace in traces)
    assert all(trace.get("estimated_cost") != "Unknown" for trace in traces)
    assert all(trace.get("feedback_applied") is False for trace in traces[:2])
    decision_trace = next(trace for trace in traces if trace.get("task_role") == "decision")
    assert str(decision_trace.get("decision_packet_id", "")).startswith("brief-")
    store = StateStore(db_path=str(db_path))
    task_state = store.get_state("llm_task_runtime_state")
    assert set(task_state) >= {"workhorse", "research", "decision"}
    cognition = store.get_state("cognition_state")
    assert "workhorse" not in cognition and "research" not in cognition
    latest = store.get_latest_decision_brief()
    metadata = latest.get("metadata", {})
    assert metadata.get("decision_packet", {}).get("recommended_action") == "observe"
    assert metadata.get("decision_packet_fresh") is True
    assert set(metadata.get("llm_tasks", {})) >= {"workhorse", "research", "decision"}


def _assert_proactive_cycle(config_path: Path, trace_path: Path, root: Path) -> None:
    before = len(read_llm_traces(str(trace_path), limit=100))
    daemon = AtlasRuntimeDaemon(
        AtlasRuntimeDaemonConfig(
            interval_seconds=60,
            max_cycles=1,
            log_path=str(root / "proactive-runtime.jsonl"),
            db_path=str(root / "proactive.sqlite"),
            inbox_dir=str(root / "proactive-events"),
            ui_inbox_path=str(root / "proactive-user-events.jsonl"),
            no_sleep=True,
            market_refresh_enabled=False,
            market_config_path=str(config_path),
            proactive_update_enabled=True,
            proactive_update_every_seconds=7200,
            proactive_update_run_on_start=True,
            runtime_mode="live",
        )
    )
    entry = daemon.run_tick(0)
    assert entry["system_metrics"]["proactive_update_status"] == "planned"
    new_traces = read_llm_traces(str(trace_path), limit=100)[before:]
    assert [trace.get("task_role") for trace in new_traces] == ["workhorse", "research", "decision"]
    store = StateStore(db_path=str(root / "proactive.sqlite"))
    task_state = store.get_state("llm_task_runtime_state")
    assert task_state["research"]["output"]["status"] == "ok"


def _assert_failed_decision_isolation(config_path: Path, trace_path: Path, root: Path) -> None:
    original = config_path.read_text(encoding="utf-8")
    config = json.loads(original)
    config["llm_task_routes"]["decision"]["model"] = "malformed-model"
    config["llm_task_routes"]["decision"]["fallback_chain"] = []
    config_path.write_text(json.dumps(config), encoding="utf-8")
    inbox_path = root / "failed-decision-user-events.jsonl"
    append_chat_event("Exercise failed Decision isolation.", inbox_path=str(inbox_path))
    db_path = root / "failed-decision.sqlite"
    daemon = AtlasRuntimeDaemon(
        AtlasRuntimeDaemonConfig(
            interval_seconds=60,
            max_cycles=1,
            log_path=str(root / "failed-decision-runtime.jsonl"),
            db_path=str(db_path),
            inbox_dir=str(root / "failed-decision-events"),
            ui_inbox_path=str(inbox_path),
            no_sleep=True,
            market_refresh_enabled=False,
            market_config_path=str(config_path),
            proactive_update_enabled=False,
            runtime_mode="live",
        )
    )
    entry = daemon.run_tick(0)
    tick = entry["cognition_summary"]["tick_result"]
    assert tick["llm_feedback_status"] == "not_applied_no_fresh_decision", tick
    latest = StateStore(db_path=str(db_path)).get_latest_decision_brief()
    assert latest["metadata"]["decision_packet_fresh"] is False
    config_path.write_text(original, encoding="utf-8")


def _assert_heartbeat_cost_safety(config_path: Path, trace_path: Path, db_path: Path, root: Path) -> None:
    before = len(read_llm_traces(str(trace_path), limit=100))
    loop = DecisionLoop(
        DecisionLoopConfig(
            sleep_interval_seconds=60,
            heartbeat_interval_seconds=1,
            db_path=str(db_path),
            inbox_dir=str(root / "heartbeat-events"),
        )
    )
    loop._last_heartbeat = 0.0
    result = loop.run_once()
    after = len(read_llm_traces(str(trace_path), limit=100))
    assert result["status"] == "success"
    assert after == before, (before, after)
    tick = result["results"][0]
    assert tick["decision_packet_fresh"] is False
    assert tick["llm_tasks"]["decision"]["status"] == "skipped_no_meaningful_delta"
    assert tick["llm_feedback_status"] == "not_applied_no_fresh_decision"


def _assert_security(config_path: Path, trace_path: Path) -> None:
    config_text = config_path.read_text(encoding="utf-8")
    trace_text = trace_path.read_text(encoding="utf-8")
    assert SECRET not in config_text
    assert SECRET not in trace_text
    assert "Authorization" not in trace_text


if __name__ == "__main__":
    main()
