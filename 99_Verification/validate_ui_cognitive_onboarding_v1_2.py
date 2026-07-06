"""Validate Atlas UI v1.2 cognitive onboarding and navigation guidance."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from ui import app_server
from ui.components.onboarding_overlay import render_onboarding_overlay
from ui.components.top_bar import render_top_bar
from ui.pages.system_guide import render_system_guide_page


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    overlay = render_onboarding_overlay()
    for text in (
        "Welcome to Atlas OS Runtime Cognitive System",
        "Start System Tour",
        "View Roadmap",
        "Enter Dashboard",
        "Booting Atlas OS Cognitive Runtime...",
        "Initializing Event Stream...",
        "Loading Cognitive Layers...",
        "System Ready",
        "UNKNOWN",
        "NEUTRAL",
    ):
        _assert(text in overlay, f"onboarding overlay should include {text}")

    guide = render_system_guide_page()
    for text in (
        "What Is Atlas OS",
        "State Meaning",
        "UNKNOWN",
        "NEUTRAL",
        "ATTENTION",
        "LIQUIDITY",
        "VOLATILITY",
        "Event",
        "Cognitive Layers",
        "Decision",
        "Explanation",
        "Trust Update",
        "regime",
        "Trust score",
        "Decision trace",
        "Causal summary",
    ):
        _assert(text in guide, f"system guide should include {text}")

    top_bar = render_top_bar()
    for text in (
        "Cognitive Control Center",
        "Dashboard",
        "Workflow",
        "Roadmap",
        "Settings",
        "/dashboard",
        "/workflow",
        "/roadmap",
        "/settings",
    ):
        _assert(text in top_bar, f"top bar should include {text}")

    dashboard = app_server._system_interface_page()
    html = dashboard.body.decode("utf-8") if hasattr(dashboard, "body") else str(dashboard)
    for text in (
        "onboarding-overlay",
        "Dashboard",
        "Roadmap",
        "Settings",
        "Waiting for cognitive signal",
        "Insufficient system context",
        "System has not yet converged on this metric.",
        "runBootSequence",
        "Start System Tour",
    ):
        _assert(text in html, f"dashboard should include {text}")

    app_text = (REPO_ROOT / "ui" / "app_server.py").read_text(encoding="utf-8")
    _assert("@app.get(\"/system-guide\"" in app_text, "FastAPI /system-guide endpoint should exist")
    _assert('parsed.path == "/system-guide"' in app_text, "stdlib /system-guide route should exist")

    ui_files = [
        REPO_ROOT / "ui" / "app_server.py",
        REPO_ROOT / "ui" / "components" / "top_bar.py",
        REPO_ROOT / "ui" / "components" / "onboarding_overlay.py",
        REPO_ROOT / "ui" / "pages" / "system_guide.py",
    ]
    for path in ui_files:
        text = path.read_text(encoding="utf-8")
        _assert("runtime.cognition" not in text, f"{path} must not import cognitive modules")

    print("UI Cognitive Onboarding v1.2 validation PASS")


if __name__ == "__main__":
    main()
