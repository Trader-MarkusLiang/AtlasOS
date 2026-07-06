"""Validate Atlas Runtime v0.5 self-organization and UI v0.1 isolation."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from runtime.atlas_runtime_daemon import AtlasRuntimeDaemon, AtlasRuntimeDaemonConfig
from runtime.cognition.self_organizing_engine import run_self_organization_cycle
from runtime.cognition.structural_evolution_controller import apply_structural_evolution
from runtime.cognition.trust_field_dynamics import evolve_trust_field
from runtime.output_logger import read_runtime_log
from runtime.state_store import StateStore
from runtime.telemetry.state_snapshot import read_cognitive_snapshots
from ui.chat_interface import submit_query
from ui.replay_console import replay_session
from ui.state_visual_dashboard import build_dashboard_state
from ui.system_control_panel import adjust_tick_interval, control_panel_state, toggle_observability_verbosity


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _cognitive_state() -> dict:
    return {
        "fusion": {"stress_score": 55, "attention_pressure": 78, "liquidity_score": 42},
        "latent_structure": {
            "latent_variables": {
                "attention_persistence_field": 84,
                "structural_liquidity_pressure": 76,
                "hidden_risk_compression": 72,
            }
        },
        "physics_constraints": {
            "system_stability_report": {
                "stability_score": 74,
                "constraint_violations": [],
            }
        },
    }


def _structural_state() -> dict:
    return {
        "mutation": {
            "edge_weight_updates": {
                "Attention->Retail Flow": 0.032,
                "Liquidity->Volatility": 0.028,
                "Price Momentum->Attention": 0.02,
            },
            "structural_shift_index": 0.12,
        },
        "regime_topology": {
            "basin_deformation": 0.045,
            "attractor_shift": 0.015,
        },
        "drift_summary": {"structural_shift_index": 0.12},
    }


def _trust(value: float) -> dict:
    return {
        "global_trust_index": value,
        "feedback_consistency_trust": value,
        "cognitive_trust": value,
        "llm_trust": value,
        "regime_stability_trust": value,
    }


def main() -> None:
    feedback = {"attention": 0.01, "causal": 0.015, "risk": 0.01}
    previous = {}
    shifts = []
    for _ in range(3):
        previous = run_self_organization_cycle(
            cognitive_state=_cognitive_state(),
            structural_coevolution_state=_structural_state(),
            system_trust_state={"rolling_trust_index": 0.82, "feedback_stability_index": 0.86},
            trust_score=_trust(0.82),
            feedback_delta=feedback,
            previous_self_organization_state=previous,
        )
        shifts.append(previous["structural_shift_index"])

    _assert(all(0 < shift <= 0.12 for shift in shifts), "self-organization shifts must be bounded and non-zero")
    _assert(previous["causal_reweight_delta"], "causal weights should gradually reweight under repeated stress")
    _assert(previous["regime_attractor_shift"] > 0, "regime sensitivity should shift under stress")
    _assert(previous["bounded"] is True and previous["reversible"] is True, "self-organization must be bounded/reversible")

    field_a = evolve_trust_field(
        previous_field={},
        system_trust_state={"rolling_trust_index": 0.8, "feedback_stability_index": 0.8},
        trust_score=_trust(0.82),
        feedback_delta=feedback,
        regime_volatility=20,
        causal_consistency=0.8,
    )
    field_b = evolve_trust_field(
        previous_field=field_a["trust_field"],
        system_trust_state={"rolling_trust_index": 0.2, "feedback_stability_index": 0.2},
        trust_score=_trust(0.2),
        feedback_delta={"attention": 0.08, "causal": 0.08, "risk": 0.08},
        regime_volatility=95,
        causal_consistency=0.1,
    )
    _assert(
        max(abs(value) for value in field_b["trust_field_delta"].values()) <= 0.08,
        "trust field must evolve smoothly without jumps",
    )

    frozen = apply_structural_evolution(
        proposed={"causal_reweight_delta": {"Attention->Retail Flow": 0.08}, "regime_attractor_shift": 0.08},
        trust_field_state={"trust_field": {"event_fusion": 0.2, "causal_graph": 0.2}, "trust_field_evolution": 0.04},
        previous_state=previous,
    )
    _assert(frozen["status"] == "frozen", "low trust field must freeze structural evolution")
    _assert(frozen["causal_reweight_delta"] == {}, "frozen evolution must not apply causal deltas")

    ui_sources = [
        REPO_ROOT / "ui/__init__.py",
        REPO_ROOT / "ui/chat_interface.py",
        REPO_ROOT / "ui/system_control_panel.py",
        REPO_ROOT / "ui/state_visual_dashboard.py",
        REPO_ROOT / "ui/replay_console.py",
    ]
    for source in ui_sources:
        text = source.read_text(encoding="utf-8")
        _assert("runtime.cognition" not in text, f"{source.name} must not import cognition modules")

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        inbox = root / "inbox"
        snapshot_log = root / "snapshots.jsonl"
        decision_log = root / "decision.jsonl"
        llm_log = root / "llm.jsonl"
        old_env = {
            "ATLAS_COGNITIVE_SNAPSHOT_LOG": os.environ.get("ATLAS_COGNITIVE_SNAPSHOT_LOG"),
            "ATLAS_DECISION_TRACE_LOG": os.environ.get("ATLAS_DECISION_TRACE_LOG"),
            "ATLAS_LLM_TRACE_LOG": os.environ.get("ATLAS_LLM_TRACE_LOG"),
        }
        os.environ["ATLAS_COGNITIVE_SNAPSHOT_LOG"] = str(snapshot_log)
        os.environ["ATLAS_DECISION_TRACE_LOG"] = str(decision_log)
        os.environ["ATLAS_LLM_TRACE_LOG"] = str(llm_log)
        try:
            queued = submit_query("show current regime and trust state", inbox_dir=str(inbox))
            _assert(Path(queued["event_file"]).exists(), "UI chat should write inbox event file")
            daemon = AtlasRuntimeDaemon(
                AtlasRuntimeDaemonConfig(
                    interval_seconds=10,
                    max_cycles=3,
                    log_path=str(root / "atlas_runtime.log"),
                    db_path=str(root / "runtime.sqlite"),
                    inbox_dir=str(inbox),
                    no_sleep=True,
                )
            )
            daemon.run_forever()
            records = read_runtime_log(log_path=str(root / "atlas_runtime.log"), limit=3)
            store = StateStore(db_path=str(root / "runtime.sqlite"))
            self_state = store.get_state("self_organization_state")
            snapshots = read_cognitive_snapshots(log_path=str(snapshot_log), limit=3)
            dashboard = build_dashboard_state(
                db_path=str(root / "runtime.sqlite"),
                decision_trace_path=str(decision_log),
                snapshot_path=str(snapshot_log),
            )
            replay = replay_session(
                0,
                2,
                decision_trace_path=str(decision_log),
                snapshot_path=str(snapshot_log),
                llm_trace_path=str(llm_log),
            )
            config = adjust_tick_interval(30, config_path=str(root / "ui_config.json"))
            verbosity = toggle_observability_verbosity("verbose", config_path=str(root / "ui_config.json"))
            panel = control_panel_state(db_path=str(root / "runtime.sqlite"), pid_file=str(root / "missing.pid"))

            _assert(len(records) == 3, "daemon should complete three cycles with UI inbox present")
            _assert(self_state.get("metadata_only") is True, "self-organization must remain metadata-only")
            _assert(any("self_organization_state" in item for item in snapshots), "snapshots should include self-organization")
            _assert(dashboard["read_only"] is True, "dashboard must be read-only")
            _assert(replay["read_only_replay"] is True, "replay must be read-only")
            _assert(config["tick_interval_seconds"] == 30, "control panel should save interval")
            _assert(verbosity["observability_verbosity"] == "verbose", "control panel should save verbosity")
            _assert("system_trust_state" in panel, "control panel should expose trust state")
        finally:
            for key, value in old_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    print("Self-Organizing Core v0.5 + UI v0.1 validation PASS")


if __name__ == "__main__":
    main()
