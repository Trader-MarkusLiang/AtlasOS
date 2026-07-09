"""Behavior validator for Atlas OS Guided Start Center."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from fastapi.testclient import TestClient
except ModuleNotFoundError:  # pragma: no cover - local fallback validation path.
    TestClient = None  # type: ignore[assignment]

from ui.app_server import app, _product_shell, getting_started_status_api
from ui.i18n.i18n import TRANSLATIONS
from ui.pages.getting_started import build_getting_started_status, render_getting_started_page


def main() -> None:
    results = [
        _test_provider_readiness_changes(),
        _test_portfolio_status_changes(),
        _test_no_secret_fields_rendered(),
        _test_i18n_parity(),
        _test_routes(),
    ]
    failed = [item for item in results if item["status"] != "PASS"]
    print(json.dumps({"status": "FAIL" if failed else "PASS", "results": results}, ensure_ascii=False, indent=2))
    if failed:
        raise SystemExit(1)


def _test_provider_readiness_changes() -> dict[str, Any]:
    config = _config()
    missing = build_getting_started_status(config, _state(provider={"base_url": "", "api_key": "", "health": "unknown"}))
    ready = build_getting_started_status(config, _state(provider={"base_url": "https://example.test/v1/chat/completions", "api_key": "***", "health": "reachable"}))
    assert missing["provider"]["status"] == "NEEDS_CONFIGURATION"
    assert ready["provider"]["status"] == "READY"
    assert ready["overall_readiness"]["can_start"] is True
    return {"name": "provider_readiness_changes", "status": "PASS"}


def _test_portfolio_status_changes() -> dict[str, Any]:
    config = _config()
    no_portfolio = build_getting_started_status(config, _state(provider={"base_url": "http://localhost:11434/api/generate", "api_key": "", "type": "ollama", "health": "reachable"}, positions=[]))
    with_portfolio = build_getting_started_status(config, _state(provider={"base_url": "http://localhost:11434/api/generate", "api_key": "", "type": "ollama", "health": "reachable"}, positions=[{"asset": "AAPL", "portfolio_percentage": 12}]))
    assert no_portfolio["portfolio"]["status"] == "OPTIONAL"
    assert with_portfolio["portfolio"]["status"] == "READY"
    assert with_portfolio["portfolio"]["position_count"] == 1
    return {"name": "portfolio_status_changes", "status": "PASS"}


def _test_no_secret_fields_rendered() -> dict[str, Any]:
    config = _config()
    state = _state(provider={"base_url": "https://example.test/v1/chat/completions", "api_key": "***", "health": "reachable"})
    status = build_getting_started_status(config, state)
    content, script = render_getting_started_page(config, state, status)
    html = content + script
    assert "api_key_encrypted" not in html
    assert "api_key_keychain_account" not in html
    assert "sk-live-secret" not in html
    return {"name": "no_secret_fields_rendered", "status": "PASS"}


def _test_i18n_parity() -> dict[str, Any]:
    en_keys = {key for key in TRANSLATIONS["en"] if key.startswith("getting.") or key == "nav.getting_started" or key == "page.getting_started"}
    zh_keys = {key for key in TRANSLATIONS["zh"] if key.startswith("getting.") or key == "nav.getting_started" or key == "page.getting_started"}
    missing = sorted(en_keys.symmetric_difference(zh_keys))
    assert not missing, missing
    return {"name": "i18n_parity", "status": "PASS", "keys": len(en_keys)}


def _test_routes() -> dict[str, Any]:
    if TestClient is None:
        payload = getting_started_status_api()
        content, script = render_getting_started_page(_config(), _state(provider={"base_url": "http://localhost:11434/api/generate", "api_key": "", "type": "ollama", "health": "reachable"}), payload)
        html = _product_shell("getting_started", content, _state(provider={"base_url": "http://localhost:11434/api/generate", "api_key": "", "type": "ollama", "health": "reachable"}), page_script=script)
        assert "overall_readiness" in payload
        assert "api_key_encrypted" not in html
        return {"name": "routes", "status": "PASS", "mode": "direct_render_no_fastapi"}
    client = TestClient(app)
    page = client.get("/getting-started")
    status = client.get("/getting-started/status")
    assert page.status_code == 200
    assert status.status_code == 200
    payload = status.json()
    assert "overall_readiness" in payload
    assert "safe" in payload and payload["safe"]["no_secrets"] is True
    assert "api_key_encrypted" not in page.text
    return {"name": "routes", "status": "PASS"}


def _config() -> dict[str, Any]:
    return {
        "ui": {"language": "en"},
        "system": {"tick_interval": 60, "runtime_mode": "simulation"},
        "assets": {"portfolio_json": "{}"},
    }


def _state(*, provider: dict[str, Any], positions: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    item = {
        "id": "openai",
        "type": provider.get("type", "openai"),
        "label": "OpenAI",
        "base_url": provider.get("base_url", ""),
        "model": "gpt-test",
        "api_key": provider.get("api_key", ""),
        "health": provider.get("health", "unknown"),
        "last_latency_ms": 120,
        "available_models": ["gpt-test"],
    }
    return {
        "llm_provider_registry": {
            "active_provider": "openai",
            "fallback_chain": ["openai"],
            "providers": [item],
            "supported_provider_types": {},
        },
        "market_intelligence": {
            "timestamp": None,
            "degraded": True,
            "channels": {"price": "NOT_CONFIGURED", "news": "SIMULATED"},
        },
        "portfolio_context": {
            "positions": positions or [],
            "exposure_sum_pct": sum(float(row.get("portfolio_percentage", 0)) for row in (positions or [])),
            "portfolio_consistency": "PASS",
        },
        "runtime": {"running": False, "pid": None},
        "tick_counter": 0,
        "last_decision_packet": {},
        "last_decision_brief_id": "",
    }


if __name__ == "__main__":
    main()
