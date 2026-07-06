"""Validate Atlas OS UI System Control Interface v1.0."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from ui.app_server import _system_interface_page, state_api


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    component_files = [
        REPO_ROOT / "ui/components/top_bar.py",
        REPO_ROOT / "ui/components/system_state_panel.py",
        REPO_ROOT / "ui/components/inspector_panel.py",
        REPO_ROOT / "ui/components/event_stream_panel.py",
        REPO_ROOT / "ui/components/__init__.py",
    ]
    for path in component_files:
        _assert(path.exists(), f"missing component: {path}")

    html_value = _system_interface_page()
    html = str(html_value.body.decode("utf-8") if hasattr(html_value, "body") else html_value)
    required_fragments = [
        'data-component="top-bar"',
        'data-component="control-panel"',
        'data-component="primary-workspace"',
        'data-component="intelligence-panel"',
        'data-component="execution-timeline"',
        "fetch(\"/state\"",
        "window.setInterval(refreshState, pollMs)",
        "postForm(\"/chat/send\"",
        "postForm(\"/control/start\"",
        "postForm(\"/control/stop\"",
        "atlas-v2-shell",
        "atlas-v2-focus-zone",
        "backdrop-filter",
    ]
    for fragment in required_fragments:
        _assert(fragment in html, f"system interface missing fragment: {fragment}")

    with tempfile.TemporaryDirectory() as temp_dir:
        old_env = os.environ.get("ATLAS_UI_DB_PATH")
        os.environ["ATLAS_UI_DB_PATH"] = str(Path(temp_dir) / "runtime.sqlite")
        try:
            state = state_api()
            _assert("regime_state" in state, "/state should expose regime state")
            _assert("trust_index" in state, "/state should expose trust index")
            _assert("last_decision_packet" in state, "/state should expose DecisionPacket")
            _assert("llm_trace_summary" in state, "/state should expose LLM trace summary")
            json.dumps(state)
        finally:
            if old_env is None:
                os.environ.pop("ATLAS_UI_DB_PATH", None)
            else:
                os.environ["ATLAS_UI_DB_PATH"] = old_env

    ui_sources = [
        REPO_ROOT / "ui/app_server.py",
        REPO_ROOT / "ui/chat_interface.py",
        *sorted((REPO_ROOT / "ui/components").glob("*.py")),
    ]
    forbidden_terms = [
        "runtime.cognition",
        "mutate_causal_graph",
        "apply_structural_drift",
        "run_self_organization_cycle",
    ]
    for source in ui_sources:
        text = source.read_text(encoding="utf-8")
        for term in forbidden_terms:
            _assert(term not in text, f"{source} must not contain forbidden cognition coupling: {term}")

    forbidden_core_files = [
        "runtime/cognition/causal_intelligence_layer.py",
        "runtime/cognition/latent_market_structure_engine.py",
        "runtime/cognition/market_physics_constraint_engine.py",
        "runtime/cognition/market_law_emergence_engine.py",
        "runtime/cognition/unified_market_intelligence_core.py",
        "runtime/cognition/self_organizing_engine.py",
        "runtime/cognition/decision_contract.py",
    ]
    for relative in forbidden_core_files:
        text = (REPO_ROOT / relative).read_text(encoding="utf-8")
        _assert("ui.components" not in text, f"{relative} must not depend on UI components")
        _assert("app_server" not in text, f"{relative} must not depend on UI server")

    print("UI System Control Interface v1.0 validation PASS")


if __name__ == "__main__":
    main()
