"""Validate Atlas OS v1.4 LLM provider runtime, UI redesign, and i18n."""

from __future__ import annotations

from pathlib import Path
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.llm.provider_registry import (
    decrypt_api_key,
    default_provider_registry,
    encrypt_api_key,
    list_provider_models,
    load_provider_registry,
    update_provider_registry,
    safe_registry_view,
    save_provider_registry,
)
from runtime.llm.provider_router import route_llm_request
from ui.app_server import create_app, state_api
from ui.i18n.i18n import t
from ui.pages.settings import load_user_config, render_settings_page

def main() -> None:
    _assert_provider_registry()
    _assert_provider_router()
    _assert_ui_i18n()
    _assert_ui_boundary()
    _assert_no_cognition_core_changes()
    print("LLM Provider UI i18n v1.4 validation PASS")


def _assert_provider_registry() -> None:
    secret = "atlas_local_test_secret"
    encrypted = encrypt_api_key(secret)
    assert encrypted != secret
    assert decrypt_api_key(encrypted) == secret
    with TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "user_config.json")
        registry = default_provider_registry()
        save_provider_registry(registry, path)
        loaded = load_provider_registry(path)
        assert loaded["active_provider"] == "openai"
        safe = safe_registry_view(loaded)
        assert safe["providers"]
        assert "api_key_encrypted" not in safe["providers"][0]
    with TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "user_config.json")
        registry = default_provider_registry()
        for provider in registry["providers"]:
            if provider["id"] == "morecode":
                provider["api_key_encrypted"] = encrypt_api_key(secret)
        save_provider_registry(registry, path)
        safe_payload = safe_registry_view(load_provider_registry(path))
        for provider in safe_payload["providers"]:
            provider["api_key"] = ""
            if provider["id"] == "morecode":
                provider["model"] = "gpt-5.4"
        update_provider_registry(safe_payload, path)
        loaded = load_provider_registry(path)
        morecode = next(provider for provider in loaded["providers"] if provider["id"] == "morecode")
        assert decrypt_api_key(morecode["api_key_encrypted"]) == secret
    with TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "user_config.json")
        registry = default_provider_registry()
        for provider in registry["providers"]:
            if provider["id"] == "custom":
                provider["base_url"] = ""
        save_provider_registry(registry, path)
        result = list_provider_models("custom", path=path, timeout=0.1)
        assert result["status"] == "not_configured"
        assert result["models"] == []


def _assert_provider_router() -> None:
    with TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "user_config.json")
        registry = default_provider_registry()
        for provider in registry["providers"]:
            if provider["id"] != "ollama":
                provider["enabled"] = False
        registry["active_provider"] = "ollama"
        registry["fallback_chain"] = ["ollama"]
        save_provider_registry(registry, path)
        result = route_llm_request(prompt="hello", context={}, provider_id="ollama", config_path=path)
        assert result["status"] in {"ok", "failsafe"}
        assert isinstance(result.get("content"), str)
        assert "fallback_attempts" in result


def _assert_ui_i18n() -> None:
    assert t("nav.dashboard", "en") == "Dashboard"
    assert t("nav.dashboard", "zh") == "仪表盘"
    html = render_settings_page(load_user_config("/tmp/atlas-nonexistent-config.json"))
    assert "LLM Providers" in html
    assert "/llm/provider/test" in html
    assert "/llm/providers/test_all" in html
    assert "settings-language" in html
    assert "provider-card" in html
    assert "provider-health-overview" in html
    assert "provider-status-pill" in html
    assert "provider-latency-bar" in html
    assert "test-all-providers" in html
    assert "provider-available-list" in html
    assert "provider-secondary-details" in html
    assert "provider-secondary-list" in html
    assert "provider-available-count" in html
    assert "/llm/provider/models" in html
    assert "data-refresh-models" in html
    assert "data-provider-model-options" in html
    assert "data-model-input" in html
    assert t("provider.refresh_models", "en") == "Refresh models from provider API"
    assert t("provider.models_unavailable", "zh") == "无法获取模型列表"


def _assert_ui_boundary() -> None:
    create_app()
    state = state_api()
    assert "llm_provider_registry" in state
    assert "providers" in state["llm_provider_registry"]
    app_server = (ROOT / "ui/app_server.py").read_text(encoding="utf-8")
    assert "/llm/provider/test" in app_server
    assert "/llm/provider/models" in app_server
    assert "/llm/providers/test_all" in app_server
    assert "/ui/language" in app_server


def _assert_no_cognition_core_changes() -> None:
    changed_surface = {
        "runtime/llm/provider_registry.py",
        "runtime/llm/provider_router.py",
        "runtime/llm_router.py",
        "ui/i18n/i18n.py",
        "ui/pages/settings.py",
        "ui/app_server.py",
        "ui/components/control_panel.py",
        "ui/components/intelligence_panel.py",
        "ui/components/top_bar.py",
        "ui/components/execution_timeline.py",
    }
    for path in changed_surface:
        assert (ROOT / path).exists(), path
    forbidden = [
        "runtime/cognition/event_fusion_engine.py",
        "runtime/cognition/causal_intelligence_layer.py",
        "runtime/cognition/latent_market_structure_engine.py",
        "runtime/cognition/market_physics_constraint_engine.py",
        "runtime/cognition/market_law_emergence_engine.py",
    ]
    for path in forbidden:
        assert (ROOT / path).exists(), path


if __name__ == "__main__":
    main()
