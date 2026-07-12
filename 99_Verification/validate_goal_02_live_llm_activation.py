"""GOAL 02 live LLM activation validation.

This validator uses a temporary provider fixture for repeatable failure
injection and does not read or print real provider secrets. Current live
provider proof is recorded separately in the GOAL 02 report.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.cognition.decision_contract import parse_decision_packet  # noqa: E402
from runtime.llm import provider_router  # noqa: E402
from runtime.llm.provider_registry import safe_registry_view, update_provider_registry  # noqa: E402
from runtime.llm.provider_router import route_llm_request  # noqa: E402
from runtime.llm_router import call_llm_raw  # noqa: E402
from runtime.telemetry.llm_trace_logger import read_llm_traces  # noqa: E402


FIXTURE_SECRET = "goal02-fixture-provider-secret"


class ProviderFixtureHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/valid":
            packet = {
                "regime_state": "GOAL_02_FIXTURE",
                "confidence": 0.61,
                "risk_level": "medium",
                "attention_state": "fixture_attention",
                "liquidity_state": "fixture_liquidity",
                "causal_summary": "Fixture provider returned a valid DecisionPacket.",
                "recommended_action": "neutral",
                "reasoning_trace": "GOAL 02 fixture contract response.",
            }
            self._json(200, {"choices": [{"message": {"content": json.dumps(packet)}}]})
        elif self.path == "/unauthorized":
            self._json(401, {"error": "unauthorized"})
        elif self.path == "/rate_limited":
            self._json(429, {"error": "rate_limited"})
        elif self.path == "/empty":
            self._json(200, {"choices": [{"message": {"content": ""}}]})
        elif self.path == "/malformed":
            body = b"{bad-json"
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/model_not_found":
            self._json(404, {"error": "model_not_found"})
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


def main() -> int:
    old_env = {
        "ATLAS_DISABLE_KEYCHAIN": os.environ.get("ATLAS_DISABLE_KEYCHAIN"),
        "ATLAS_USER_CONFIG": os.environ.get("ATLAS_USER_CONFIG"),
        "ATLAS_LLM_TRACE_LOG": os.environ.get("ATLAS_LLM_TRACE_LOG"),
    }
    server = ThreadingHTTPServer(("127.0.0.1", 0), ProviderFixtureHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    original_urlopen = provider_router.urllib.request.urlopen
    try:
        with tempfile.TemporaryDirectory(prefix="atlas-goal02-") as tmp:
            root = Path(tmp)
            config_path = root / "user_config.json"
            trace_path = root / "llm_traces.jsonl"
            os.environ["ATLAS_DISABLE_KEYCHAIN"] = "1"
            os.environ["ATLAS_USER_CONFIG"] = str(config_path)
            os.environ["ATLAS_LLM_TRACE_LOG"] = str(trace_path)
            base = f"http://127.0.0.1:{server.server_address[1]}"
            _write_registry(config_path, base, fallback=False)

            result: dict[str, Any] = {"checks": {}}
            _check("secret_not_plaintext", FIXTURE_SECRET not in config_path.read_text(encoding="utf-8"), result)
            safe_text = json.dumps(safe_registry_view(), ensure_ascii=False)
            _check("safe_registry_masks_secret", FIXTURE_SECRET not in safe_text and "api_key_encrypted" not in safe_text, result)

            raw = call_llm_raw(
                "valid",
                "Return a valid DecisionPacket.",
                {"runtime_context": {"decision_packet_id": "goal-02-fixture", "feedback_applied": False}},
            )
            packet = parse_decision_packet(raw)
            _check("valid_provider_packet", packet["regime_state"] == "GOAL_02_FIXTURE", result)
            traces = read_llm_traces(str(trace_path))
            trace_text = trace_path.read_text(encoding="utf-8") if trace_path.exists() else ""
            _check("telemetry_recorded", len(traces) == 1 and traces[0].get("decision_packet_id") == "goal-02-fixture", result)
            _check("telemetry_no_secret", FIXTURE_SECRET not in trace_text, result)

            for provider_id, expected in [
                ("unauthorized", "401"),
                ("rate_limited", "429"),
                ("empty", "empty_response"),
                ("malformed", "malformed_response"),
                ("model_not_found", "404"),
            ]:
                routed = route_llm_request(prompt="fixture", context={}, provider_id=provider_id, config_path=str(config_path))
                errors = json.dumps(routed.get("fallback_attempts", []), ensure_ascii=False)
                _check(f"{provider_id}_visible", routed["status"] == "failsafe" and expected in errors, result)

            def timeout_urlopen(request: Any, *args: Any, **kwargs: Any) -> Any:
                url = getattr(request, "full_url", str(request))
                if str(url).endswith("/timeout"):
                    raise TimeoutError("timed out")
                return original_urlopen(request, *args, **kwargs)

            provider_router.urllib.request.urlopen = timeout_urlopen
            _write_registry(config_path, base, fallback=False, include_timeout=True)
            timed = route_llm_request(prompt="fixture", context={}, provider_id="timeout", config_path=str(config_path))
            _check("timeout_visible", timed["status"] == "failsafe" and "timed out" in json.dumps(timed.get("fallback_attempts", [])), result)
            provider_router.urllib.request.urlopen = original_urlopen

            _write_registry(config_path, base, fallback=True)
            fallback = route_llm_request(prompt="fallback fixture", context={}, provider_id="unauthorized", config_path=str(config_path))
            fallback_packet = parse_decision_packet(str(fallback.get("content") or ""))
            _check("fallback_reaches_valid_provider", fallback["status"] == "ok" and fallback["provider"] == "valid", result)
            _check("fallback_packet_valid", fallback_packet["regime_state"] == "GOAL_02_FIXTURE", result)

            failures = [key for key, value in result["checks"].items() if value is not True]
            result.update(
                {
                    "status": "PASS" if not failures else "FAIL",
                    "failures": failures,
                    "fixture_provider_url": "127.0.0.1",
                }
            )
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
            return 0 if not failures else 1
    finally:
        provider_router.urllib.request.urlopen = original_urlopen
        server.shutdown()
        thread.join(timeout=2)
        for key, value in old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _write_registry(config_path: Path, base: str, *, fallback: bool, include_timeout: bool = False) -> None:
    providers = [
        _provider("valid", f"{base}/valid", api_key=FIXTURE_SECRET),
        _provider("unauthorized", f"{base}/unauthorized"),
        _provider("rate_limited", f"{base}/rate_limited"),
        _provider("empty", f"{base}/empty"),
        _provider("malformed", f"{base}/malformed"),
        _provider("model_not_found", f"{base}/model_not_found"),
    ]
    if include_timeout:
        providers.append(_provider("timeout", f"{base}/timeout"))
    registry = {
        "active_provider": "valid",
        "fallback_chain": ["rate_limited", "valid"] if fallback else [],
        "providers": providers,
    }
    update_provider_registry(registry, str(config_path))


def _provider(provider_id: str, base_url: str, api_key: str = "") -> dict[str, Any]:
    item = {
        "id": provider_id,
        "type": "openai",
        "enabled": True,
        "base_url": base_url,
        "model": "goal-02-fixture-model",
    }
    if api_key:
        item["api_key"] = api_key
    return item


def _check(name: str, condition: bool, result: dict[str, Any]) -> None:
    result["checks"][name] = bool(condition)


if __name__ == "__main__":
    raise SystemExit(main())
