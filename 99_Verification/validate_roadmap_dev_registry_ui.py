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
    _assert(roadmap.get("version") == "parallel-track productization roadmap", "roadmap should use parallel-track versioning")
    _assert("productization" in str(roadmap.get("current_stage", "")), "current stage should focus productization")
    _assert("forecast accountability" in str(roadmap.get("next_stage", "")), "next stage should include forecast accountability")
    tracks = roadmap.get("tracks", [])
    _assert(isinstance(tracks, list) and len(tracks) >= 5, "roadmap should expose parallel tracks")
    track_names = {track.get("track") for track in tracks if isinstance(track, dict)}
    for track in {
        "Atlas Core / Knowledge OS",
        "Atlas Runtime",
        "Atlas Cognitive Overlay",
        "Atlas UI / Product",
        "Atlas Data / Market Intelligence",
    }:
        _assert(track in track_names, f"roadmap should include {track}")
    model = roadmap.get("version_model", {})
    _assert("Core v2.x" in str(model.get("why_versions_differ", "")), "roadmap should explain differing version tracks")
    layers = roadmap.get("layers", [])
    _assert(isinstance(layers, list) and len(layers) >= 8, "roadmap should contain version layers")
    versions = {layer.get("version") for layer in layers if isinstance(layer, dict)}
    for version in {"v0.1", "v0.7", "v0.8"}:
        _assert(version in versions, f"roadmap should include {version}")
    v07 = next(layer for layer in layers if layer.get("version") == "v0.7")
    v08 = next(layer for layer in layers if layer.get("version") == "v0.8")
    _assert(v07.get("status") == "implemented", "v0.7 should be implemented")
    _assert(v08.get("status") == "planned", "v0.8 should be planned")
    _assert(
        v07.get("validation", {}).get("status") == "REAL_RUNTIME_PROVEN",
        "v0.7 validation should expose Prompt D evidence level",
    )

    payload = roadmap_api_payload(str(roadmap_path))
    _assert(payload.get("current_version") == "productization-sprint", "/roadmap payload should expose current version")
    _assert(payload.get("tracks"), "/roadmap payload should expose parallel tracks")
    _assert(payload.get("version_model"), "/roadmap payload should expose version model")
    _assert(payload.get("implemented_layers"), "/roadmap payload should expose implemented layers")
    _assert(payload.get("planned_layers"), "/roadmap payload should expose planned layers")
    _assert("productization" in str(payload.get("active_stage")), "/roadmap payload should expose active stage")

    page = render_dev_registry_page(load_roadmap(str(roadmap_path)), {"regime_state": "NORMAL", "trust_index": 0.75})
    for text in (
        "Version Timeline",
        "Module Evolution Log",
        "Evidence Results",
        "Current System State",
        "System Architecture Evolution Graph",
        "Causal Self-Discovery",
        "Causal Interaction Layer",
    ):
        _assert(text in page, f"dev registry should render {text}")
    roadmap_page = __import__("ui.pages.roadmap", fromlist=["render_roadmap_page"]).render_roadmap_page(payload)
    for text in ("Parallel product tracks", "Atlas Runtime", "Atlas UI / Product", "Atlas Data / Market Intelligence"):
        _assert(text in roadmap_page, f"roadmap page should render {text}")

    dashboard = app_server._system_interface_page()
    dashboard_html = dashboard.body.decode("utf-8") if hasattr(dashboard, "body") else str(dashboard)
    for href in ('href="/dashboard"', 'href="/workflow"', 'href="/roadmap"', 'href="/settings"'):
        _assert(href in dashboard_html, f"dashboard should include {href} navigation")

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
