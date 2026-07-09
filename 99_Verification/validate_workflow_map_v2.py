#!/usr/bin/env python3
"""Validate the Atlas OS Workflow Map v2 UI rebuild.

This validator is UI/verification-only. It inspects the rendered /workflow
route plus local source files and writes a machine-readable evidence artifact.
It does not modify runtime, cognition, Decision Contract, CDE, scheduler, or
portfolio state.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "99_Verification" / "artifacts" / "workflow_map"
RESULT_PATH = ARTIFACT_DIR / "workflow_map_v2_validation_result.json"
WORKFLOW_URL = "http://127.0.0.1:8765/workflow"

REQUIRED_STAGES = {
    "input",
    "understand",
    "model",
    "decide",
    "learn",
}

REQUIRED_NODES = {
    "external_information",
    "market_data",
    "portfolio_context",
    "user_context",
    "provider_context",
    "input_router",
    "event_stream",
    "event_fusion",
    "memory",
    "causal_inference",
    "world_model",
    "lmse",
    "mpce",
    "mle",
    "umis",
    "hypothesis",
    "forecast",
    "decision_contract",
    "cde_decision_layer",
    "llm_router",
    "decision_brief",
    "reality_outcome",
    "forecast_evaluation",
    "feedback",
    "trust_update",
    "hypothesis_reweight",
    "self_iteration",
    "state_store",
    "forecast_ledger",
    "telemetry",
    "cache",
}

REQUIRED_STATUSES = {
    "status-active",
    "status-completed",
    "status-waiting",
    "status-degraded",
    "status-failed",
    "status-not_used",
}

REQUIRED_REPORTS = {
    "Atlas_OS_Workflow_Map_Baseline.md",
    "Atlas_OS_Workflow_Map_Interaction_Report.md",
    "Atlas_OS_Workflow_Map_Bilingual_Report.md",
    "Atlas_OS_Workflow_Map_Final_Acceptance.md",
}

REQUIRED_E2E_FILES = {
    "workflow_map_v2_e2e_result.json",
    "workflow_map_v2_e2e_final.png",
}


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    html = _fetch_workflow()
    sources = _read_sources()
    css = sources["tokens"]
    component = sources["component"]
    i18n = sources["i18n"]

    checks: dict[str, dict[str, object]] = {}
    checks["route_reachable"] = _check(bool(html), "GET /workflow returned HTML")
    checks["static_grid_removed"] = _check(
        'aria-label="Global system workflow"' not in html
        and "<g data-workflow-node" not in html,
        "Old static SVG/grid is absent from active /workflow HTML",
    )
    checks["five_stage_flow"] = _check(
        REQUIRED_STAGES <= set(re.findall(r'data-flow-stage="([^"]+)"', html)),
        "Input / Understand / Model / Decide / Learn stage containers exist",
    )
    checks["required_nodes"] = _check(
        REQUIRED_NODES <= set(re.findall(r'data-flow-node="([^"]+)"', html)),
        "All required node groups are rendered",
    )
    checks["feedback_loop"] = _check(
        "data-feedback-loop" in html and "feedbackTrace" in css,
        "Explicit feedback loop and restrained animation exist",
    )
    checks["concept_first_default"] = _check(
        'data-flow-mode="simple"' in html
        and "Market Meaning" in component
        and "Causal Prediction" in component
        and "Uncertainty Model" in component,
        "Default mode is Simple and conceptual labels exist",
    )
    checks["acronyms_secondary"] = _check(
        "flow-node-acronym" in html
        and 'data-flow-mode="simple"' in html
        and "data-flow-mode=\"simple\"] .flow-node-acronym" in css
        and "display: none" in css,
        "Acronyms are secondary and hidden by default Simple mode",
    )
    checks["main_support_distinct"] = _check(
        "flow-node-primary" in html
        and "flow-node-support" in html
        and "support-shelf" in html
        and 'data-architecture-mode="latest"' in html,
        "Primary path and support systems are visually distinct",
    )
    checks["latest_tick_path"] = _check(
        "current-path" in html
        and "not-current-path" in html
        and 'data-architecture-mode-control="latest"' in html,
        "Latest Tick path is encoded",
    )
    checks["status_encoding"] = _check(
        REQUIRED_STATUSES <= {status for status in REQUIRED_STATUSES if status in css or status in html},
        "ACTIVE / COMPLETED / WAITING / DEGRADED / FAILED / NOT_USED styles exist",
    )
    checks["node_interaction"] = _check(
        "selectNode(key)" in component
        and "upstream" in component
        and "downstream" in component
        and "unrelated" in component,
        "Node selection, dependency highlighting, and dimming are implemented",
    )
    checks["inspector"] = _check(
        "data-flow-inspector" in html
        and "data-inspector-section=\"purpose\"" in html
        and "data-inspector-section=\"inputs\"" in html
        and "data-inspector-section=\"outputs\"" in html
        and "data-inspector-section=\"status\"" in html
        and "flow-inspector-details" in html,
        "Context inspector includes required sections and collapsed technical detail",
    )
    checks["simple_expert_modes"] = _check(
        'data-flow-mode-control="simple"' in html
        and 'data-flow-mode-control="expert"' in html
        and "atlas.workflow.flowMode" in html,
        "Simple and Expert modes exist and persist preference",
    )
    checks["latest_full_modes"] = _check(
        'data-architecture-mode-control="latest"' in html
        and 'data-architecture-mode-control="full"' in html
        and "atlas.workflow.architectureMode" in html,
        "Latest Tick and Full Architecture modes exist and persist preference",
    )
    checks["keyboard"] = _check(
        'event.key === "Enter"' in html
        and 'event.key === " "' in html
        and 'event.key === "Escape"' in html,
        "Enter / Space select and Escape clears selection",
    )
    checks["reduced_motion"] = _check(
        "@media (prefers-reduced-motion: reduce)" in css,
        "Reduced-motion media query exists",
    )
    checks["bilingual"] = _check(
        "Atlas 如何把信息变成判断" in component
        and "How Atlas turns information into judgment" in component
        and "简洁视图" in component
        and "Expert" in component
        and "workflow.interactive_map" in i18n
        and "交互式下钻" in i18n,
        "Chinese and English strings exist for core workflow controls",
    )
    checks["zoom_fit_reset"] = _check(
        'data-flow-zoom="in"' in html
        and 'data-flow-zoom="out"' in html
        and 'data-flow-zoom="fit"' in html
        and "data-flow-reset" in html,
        "Zoom In / Zoom Out / Fit / Reset controls exist",
    )
    checks["responsive"] = _check(
        "@media (max-width: 1180px)" in css
        and "@media (max-width: 900px)" in css
        and ".flow-stage-grid { grid-template-columns: 1fr; }" in css,
        "Responsive stage stacking rules exist",
    )
    checks["verification_reports"] = _check(
        all((ROOT / "99_Verification" / name).exists() for name in REQUIRED_REPORTS),
        "Required workflow map reports exist",
    )
    checks["e2e_artifacts"] = _check(
        all((ARTIFACT_DIR / name).exists() for name in REQUIRED_E2E_FILES),
        "24-step E2E result and final screenshot artifacts exist",
    )

    passed = all(bool(item["passed"]) for item in checks.values())
    result = {
        "status": "PASS" if passed else "FAIL",
        "workflow_url": WORKFLOW_URL,
        "checks": checks,
        "missing_reports": [
            name for name in sorted(REQUIRED_REPORTS) if not (ROOT / "99_Verification" / name).exists()
        ],
        "missing_e2e_artifacts": [
            name for name in sorted(REQUIRED_E2E_FILES) if not (ARTIFACT_DIR / name).exists()
        ],
        "boundary": {
            "ui_only": True,
            "runtime_semantics_modified": False,
            "cognition_semantics_modified": False,
            "decision_contract_modified": False,
        },
    }
    RESULT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if passed else 1


def _fetch_workflow() -> str:
    try:
        with urlopen(WORKFLOW_URL, timeout=8) as response:
            if response.status != 200:
                return ""
            return response.read().decode("utf-8", errors="replace")
    except (OSError, URLError):
        return ""


def _read_sources() -> dict[str, str]:
    return {
        "component": (ROOT / "ui" / "components" / "cognitive_flow_map.py").read_text(),
        "inspector": (ROOT / "ui" / "components" / "workflow_inspector.py").read_text(),
        "tokens": (ROOT / "ui" / "design" / "tokens.py").read_text(),
        "i18n": (ROOT / "ui" / "i18n" / "i18n.py").read_text(),
    }


def _check(passed: bool, evidence: str) -> dict[str, object]:
    return {"passed": bool(passed), "evidence": evidence}


if __name__ == "__main__":
    sys.exit(main())
