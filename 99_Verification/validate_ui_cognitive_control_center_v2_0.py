"""Validate Atlas UI v2.0 cognitive control center redesign."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from ui import app_server
from ui.components.control_panel import render_control_panel
from ui.components.execution_timeline import render_execution_timeline
from ui.components.intelligence_panel import render_intelligence_panel
from ui.components.workflow_graph import render_workflow_graph
from ui.pages.settings import load_user_config, render_settings_page, save_user_config


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    control = render_control_panel()
    for text in (
        "runtime-start",
        "runtime-stop",
        "tick-interval",
        "simulation-mode",
        "active-provider-label",
        "active-provider-model",
        "active-provider-health",
        "asset-json-editor",
    ):
        _assert(text in control, f"control panel should include {text}")

    intelligence = render_intelligence_panel()
    for text in (
        "decision-why",
        "dominant-causal-factors",
        "active-hypothesis",
        "shadow-hypothesis-count",
        "trust-trend",
        "stability-index",
        "llm-call-count",
        "llm-latency",
    ):
        _assert(text in intelligence, f"intelligence panel should include {text}")

    timeline = render_execution_timeline()
    for text in ("v2-execution-timeline", "Event", "Decision", "Feedback", "compressed-stream"):
        _assert(text in timeline, f"timeline should include {text}")

    graph = render_workflow_graph("hypothesis_engine")
    for text in (
        "Minimal Active Path",
        "active-path",
        "inactive",
        "workflow-node-explanation",
        "data-explanation",
        "Hypothesis Engine",
    ):
        _assert(text in graph, f"workflow graph should include {text}")

    settings = render_settings_page()
    for text in (
        "LLM Providers",
        "OpenAI",
        "Claude",
        "Ollama",
        "Custom Proxy",
        "active-provider",
        "fallback-chain",
        "tick-interval-setting",
        "runtime-mode-setting",
        "trust-threshold-setting",
        "asset-list",
        "/llm/provider/test",
        "settings-language",
    ):
        _assert(text in settings, f"settings page should include {text}")

    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = str(Path(temp_dir) / "user_config.json")
        result = save_user_config(
            {
                "provider": "Claude",
                "api_key": "placeholder-api-key",
                "base_url": "https://example.test",
                "model": "claude-test",
                "tick_interval": "30",
                "runtime_mode": "simulation",
                "trust_threshold": "0.55",
                "hypothesis_switching_sensitivity": "0.12",
                "portfolio_json": '{"mode":"test"}',
                "asset_list": "AAPL\nMSFT",
                "weights": '{"AAPL": 0.5, "MSFT": 0.5}',
            },
            config_path,
        )
        saved = load_user_config(config_path)
        _assert(result["status"] == "saved", "settings save should report saved")
        _assert(result["config"]["llm"]["api_key"] == "***", "settings response should mask API key")
        _assert(saved["llm"]["provider"] == "Claude", "provider should persist")
        _assert(saved["metadata"]["ui_only"] is True, "config should remain UI-only")
        _assert(saved["metadata"]["no_trading_execution"] is True, "config must not imply trading")

    dashboard = app_server._system_interface_page()
    html = dashboard.body.decode("utf-8") if hasattr(dashboard, "body") else str(dashboard)
    for text in (
        "atlas-v2-shell",
        "v2-control-panel",
        "atlas-v2-focus-zone",
        "v2-intelligence-panel",
        "v2-execution-timeline",
        'data-v2-mode="system"',
        'data-v2-mode="chat"',
        'data-v2-mode="workflow"',
        "state-regime",
        "state-trust",
        "decision-action",
        "focus-runtime-status",
        "language-select",
    ):
        _assert(text in html, f"dashboard should include {text}")
    _assert('data-v2-mode="architecture"' not in html, "redundant Architecture Mode should be removed")

    ui_files = [
        REPO_ROOT / "ui" / "app_server.py",
        REPO_ROOT / "ui" / "components" / "control_panel.py",
        REPO_ROOT / "ui" / "components" / "intelligence_panel.py",
        REPO_ROOT / "ui" / "components" / "execution_timeline.py",
        REPO_ROOT / "ui" / "components" / "workflow_graph.py",
        REPO_ROOT / "ui" / "pages" / "settings.py",
    ]
    for path in ui_files:
        text = path.read_text(encoding="utf-8")
        _assert("runtime.cognition" not in text, f"{path} must not import cognitive modules")

    print("UI Cognitive Control Center v2.0 validation PASS")


if __name__ == "__main__":
    main()
