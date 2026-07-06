"""Validate Atlas OS UI Cognitive Explainability Interface v1.1."""

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
        REPO_ROOT / "ui/components/causal_graph_viewer.py",
        REPO_ROOT / "ui/components/regime_transition_map.py",
        REPO_ROOT / "ui/components/structural_drift_timeline.py",
        REPO_ROOT / "ui/components/inspector_panel.py",
        REPO_ROOT / "ui/components/top_bar.py",
    ]
    for path in component_files:
        _assert(path.exists(), f"missing explainability component: {path}")

    html_value = _system_interface_page()
    html = str(html_value.body.decode("utf-8") if hasattr(html_value, "body") else html_value)
    required_fragments = [
        'data-component="causal-graph-viewer"',
        'data-component="regime-transition-map"',
        'data-component="structural-drift-timeline"',
        'id="causal-graph-overlay"',
        'id="regime-map-overlay"',
        'id="drift-timeline-overlay"',
        "causal-graph-svg",
        "regime-map-svg",
        "drift-timeline-svg",
        "decision-why",
        "dominant-causal-factors",
        "regime-influence",
        "trust-impact",
        "fetch(\"/state\"",
        "fetch(\"/replay?start_tick=\"",
        "updateCausalGraph(state)",
        "updateRegimeMap(state)",
        "updateDriftTimeline(state)",
        "updateDecisionExplanation(state, packet)",
    ]
    for fragment in required_fragments:
        _assert(fragment in html, f"explainability interface missing fragment: {fragment}")

    with tempfile.TemporaryDirectory() as temp_dir:
        old_env = os.environ.get("ATLAS_UI_DB_PATH")
        os.environ["ATLAS_UI_DB_PATH"] = str(Path(temp_dir) / "runtime.sqlite")
        try:
            state = state_api()
            _assert("dashboard" in state, "/state should include dashboard snapshot data")
            _assert("last_decision_packet" in state, "/state should expose DecisionPacket")
            _assert("structural_coevolution_state" in state, "/state should expose structural state")
            _assert("self_organization_state" in state, "/state should expose self-organization state")
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
        "compute_trust_score",
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
        "runtime/cognition/trust_score_engine.py",
        "runtime/atlas_runtime_daemon.py",
    ]
    for relative in forbidden_core_files:
        text = (REPO_ROOT / relative).read_text(encoding="utf-8")
        _assert("causal_graph_viewer" not in text, f"{relative} must not depend on explainability UI")
        _assert("regime_transition_map" not in text, f"{relative} must not depend on explainability UI")
        _assert("structural_drift_timeline" not in text, f"{relative} must not depend on explainability UI")

    print("UI Cognitive Explainability v1.1 validation PASS")


if __name__ == "__main__":
    main()
