"""Validate polished Workflow and Roadmap UI pages."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from ui import app_server
from ui.pages.dev_registry import roadmap_api_payload
from ui.pages.roadmap import render_roadmap_page
from ui.pages.workflow import render_workflow_page


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    workflow = render_workflow_page("causal_layer")
    for text in (
        "Atlas Workflow",
        "Guided Execution Path",
        "From event to bounded feedback.",
        "stage-card",
        "stage-detail",
        "Input boundary",
        "No signal-engine collapse",
        "Read-only UI",
        "Structured outputs",
        "Bounded adaptation",
    ):
        _assert(text in workflow, f"workflow page should include {text}")
    _assert("Minimal Active Path" not in workflow, "workflow page should no longer be the old compact card")

    payload = roadmap_api_payload("docs/atlas_roadmap.json")
    roadmap = render_roadmap_page(payload)
    for text in (
        "Atlas Roadmap",
        "Current Stage",
        "Release Progress",
        "Version Timeline",
        "Layer progression",
        "Architecture Evolution",
        "/roadmap?format=json",
        "/roadmap.json",
        "card layer-card",
    ):
        _assert(text in roadmap, f"roadmap page should include {text}")
    _assert(not roadmap.lstrip().startswith("{"), "roadmap browser page must not render raw JSON")

    dashboard_route = app_server._workflow_page("event_stream")
    route_html = dashboard_route.body.decode("utf-8") if hasattr(dashboard_route, "body") else str(dashboard_route)
    _assert("Guided Execution Path" in route_html, "workflow route helper should use polished page")

    app_text = (REPO_ROOT / "ui" / "app_server.py").read_text(encoding="utf-8")
    for route in (
        '@app.get("/roadmap", response_class=HTMLResponse)',
        '@app.get("/roadmap.json")',
        'format.lower() == "json"',
        'render_roadmap_page(payload)',
    ):
        _assert(route in app_text, f"app server should preserve roadmap route behavior: {route}")

    ui_files = [
        REPO_ROOT / "ui" / "pages" / "workflow.py",
        REPO_ROOT / "ui" / "pages" / "roadmap.py",
        REPO_ROOT / "ui" / "app_server.py",
    ]
    for path in ui_files:
        text = path.read_text(encoding="utf-8")
        _assert("runtime.cognition" not in text, f"{path} must not import cognitive modules")

    print("UI Workflow/Roadmap v2.1 validation PASS")


if __name__ == "__main__":
    main()
