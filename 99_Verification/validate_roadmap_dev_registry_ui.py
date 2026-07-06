"""Validate Atlas Roadmap + Development Registry UI layer."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from ui import app_server
from ui.pages.dev_registry import load_roadmap, render_dev_registry_page, roadmap_api_payload


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    roadmap_path = REPO_ROOT / "docs" / "atlas_roadmap.json"
    roadmap = json.loads(roadmap_path.read_text(encoding="utf-8"))
    _assert(roadmap.get("version") == "v0.1 - v0.8", "roadmap version range should be v0.1 - v0.8")
    _assert(roadmap.get("current_stage") == "v0.7", "current stage should be v0.7")
    _assert("v0.8" in str(roadmap.get("next_stage", "")), "next stage should point to v0.8 preparation")
    layers = roadmap.get("layers", [])
    _assert(isinstance(layers, list) and len(layers) >= 8, "roadmap should contain version layers")
    versions = {layer.get("version") for layer in layers if isinstance(layer, dict)}
    for version in {"v0.1", "v0.7", "v0.8"}:
        _assert(version in versions, f"roadmap should include {version}")
    v07 = next(layer for layer in layers if layer.get("version") == "v0.7")
    v08 = next(layer for layer in layers if layer.get("version") == "v0.8")
    _assert(v07.get("status") == "completed", "v0.7 should be completed")
    _assert(v08.get("status") == "planned", "v0.8 should be planned")
    _assert(v07.get("validation", {}).get("status") == "PASS", "v0.7 validation should pass")

    payload = roadmap_api_payload(str(roadmap_path))
    _assert(payload.get("current_version") == "v0.7", "/roadmap payload should expose current version")
    _assert(payload.get("completed_layers"), "/roadmap payload should expose completed layers")
    _assert(payload.get("planned_layers"), "/roadmap payload should expose planned layers")
    _assert(payload.get("active_stage") == "v0.7", "/roadmap payload should expose active stage")

    page = render_dev_registry_page(load_roadmap(str(roadmap_path)), {"regime_state": "NORMAL", "trust_index": 0.75})
    for text in (
        "Version Timeline",
        "Module Evolution Log",
        "Validation Results",
        "Current System State",
        "System Architecture Evolution Graph",
        "Causal Self-Discovery",
        "Causal Interaction Layer",
    ):
        _assert(text in page, f"dev registry should render {text}")

    dashboard = app_server._system_interface_page()
    dashboard_html = dashboard.body.decode("utf-8") if hasattr(dashboard, "body") else str(dashboard)
    for text in ("Dashboard", "Workflow", "Roadmap", "Settings"):
        _assert(text in dashboard_html, f"dashboard should include {text} tab")
    _assert("/roadmap" in dashboard_html, "dashboard should link to /roadmap")
    _assert("/settings" in dashboard_html, "dashboard should link to /settings")

    app_text = (REPO_ROOT / "ui" / "app_server.py").read_text(encoding="utf-8")
    _assert("@app.get(\"/roadmap\"" in app_text, "FastAPI /roadmap endpoint should exist")
    _assert("@app.get(\"/roadmap.json\")" in app_text, "FastAPI /roadmap.json endpoint should exist")
    _assert("@app.get(\"/dev-registry\"" in app_text, "FastAPI /dev-registry endpoint should exist")
    _assert('parsed.path == "/roadmap"' in app_text, "stdlib /roadmap route should exist")
    _assert('parsed.path == "/roadmap.json"' in app_text, "stdlib /roadmap.json route should exist")
    _assert('parsed.path == "/dev-registry"' in app_text, "stdlib /dev-registry route should exist")

    ui_files = [
        REPO_ROOT / "ui" / "app_server.py",
        REPO_ROOT / "ui" / "components" / "top_bar.py",
        REPO_ROOT / "ui" / "pages" / "dev_registry.py",
    ]
    for path in ui_files:
        text = path.read_text(encoding="utf-8")
        _assert("runtime.cognition" not in text, f"{path} must not import cognitive modules")

    print("Roadmap Dev Registry UI validation PASS")


if __name__ == "__main__":
    main()
