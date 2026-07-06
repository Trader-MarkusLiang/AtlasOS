"""Validate Atlas UI v1.3 control-plane redesign."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from ui import app_server
from ui.components.sidebar import render_sidebar
from ui.components.workflow_graph import render_workflow_graph
from ui.pages.settings import load_user_config, render_settings_page, save_user_config


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    sidebar = render_sidebar()
    for text in (
        "System Status",
        "Model Configuration",
        "API Keys",
        "Runtime Settings",
        "Asset Configuration",
        "LLM Providers",
        "Logs",
        "Roadmap",
    ):
        _assert(text in sidebar, f"sidebar should include {text}")

    graph = render_workflow_graph("hypothesis_engine")
    for text in (
        "Event Stream",
        "Cognitive Pipeline",
        "Causal Layer",
        "World Model",
        "Hypothesis Engine",
        "Decision Contract",
        "LLM Router",
        "Feedback Loop",
        "active",
    ):
        _assert(text in graph, f"workflow graph should include {text}")

    settings = render_settings_page()
    for text in (
        "LLM Config",
        "Provider",
        "API Key",
        "Base URL",
        "Model",
        "Atlas System Config",
        "Tick Interval",
        "Runtime Mode",
        "Trust Threshold",
        "Hypothesis Switching Sensitivity",
        "User Assets Config",
        "Portfolio JSON",
        "Asset List",
        "Optional Weights JSON",
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
        _assert(saved["system"]["tick_interval"] == 30, "tick interval should persist")
        _assert(saved["assets"]["asset_list"] == ["AAPL", "MSFT"], "asset list should persist")
        _assert(saved["metadata"]["ui_only"] is True, "config should be UI-only")
        _assert(saved["metadata"]["no_trading_execution"] is True, "config must not imply trading")

    dashboard = app_server._system_interface_page()
    html = dashboard.body.decode("utf-8") if hasattr(dashboard, "body") else str(dashboard)
    for text in (
        "atlas-v2-shell",
        "v2-control-panel",
        "Chat Mode",
        "System Mode",
        "Workflow Mode",
        "v2-intelligence-panel",
        "Flow Timeline",
        "Event -> Decision -> Feedback",
        "Settings",
        "workflow-graph",
    ):
        _assert(text in html, f"dashboard should include {text}")

    app_text = (REPO_ROOT / "ui" / "app_server.py").read_text(encoding="utf-8")
    for route in (
        '@app.get("/settings"',
        '@app.post("/settings"',
        '@app.get("/workflow"',
        'parsed.path == "/settings"',
        'parsed.path == "/workflow"',
    ):
        _assert(route in app_text, f"app server should include route {route}")

    ui_files = [
        REPO_ROOT / "ui" / "app_server.py",
        REPO_ROOT / "ui" / "components" / "sidebar.py",
        REPO_ROOT / "ui" / "components" / "workflow_graph.py",
        REPO_ROOT / "ui" / "pages" / "settings.py",
    ]
    for path in ui_files:
        text = path.read_text(encoding="utf-8")
        _assert("runtime.cognition" not in text, f"{path} must not import cognitive modules")

    print("UI Control Plane v1.3 validation PASS")


if __name__ == "__main__":
    main()
