#!/usr/bin/env python3
"""Validate the portfolio-first Investor Home product contract."""

from __future__ import annotations

import json
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ui.pages.product_views import home_content  # noqa: E402
from ui.presentation.home_intelligence import (  # noqa: E402
    _candidate_score_board,
    _scenario_outlook,
    _usable_market_observations,
)

ARTIFACT_DIR = ROOT / "99_Verification" / "artifacts" / "investor_home"


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {}

    state = _live_state()
    market = state.get("market_intelligence") if isinstance(state.get("market_intelligence"), dict) else {}
    observations = market.get("observations") if isinstance(market.get("observations"), list) else []
    usable = _usable_market_observations(market)
    channels = market.get("channels") if isinstance(market.get("channels"), dict) else {}
    checks["live_runtime_reachable"] = bool(state.get("tick_counter"))
    checks["real_observation_reaches_state"] = bool(usable) and all(str(item.get("source", "")).lower() != "simulated" for item in usable)
    checks["channels_report_honest_status"] = bool(channels) and all(
        str(value).upper() in {"LIVE", "DELAYED", "CACHED", "SIMULATED", "NOT_CONFIGURED", "RATE_LIMITED", "FAILED"}
        for value in channels.values()
    )
    checks["unavailable_observations_excluded"] = not _usable_market_observations(
        {"observations": [{"asset": "X", "source": "Unavailable", "data_quality_status": "Unavailable", "freshness": "LIVE"}]}
    )

    provider = state.get("llm_provider_registry") if isinstance(state.get("llm_provider_registry"), dict) else {}
    trace = state.get("llm_trace_summary") if isinstance(state.get("llm_trace_summary"), dict) else {}
    checks["provider_config_separate_from_inference"] = "active_provider" in provider and "latest_inference_status" in trace
    checks["latest_inference_succeeded"] = str(trace.get("latest_inference_status")).lower() == "succeeded"

    html = home_content(state)
    # Investor Home v2.1 (2026-07-19): the portfolio overview leads the first screen (it contains
    # current-holdings), followed by the merged Core Judgment section; the old answer card survives
    # only as the derived posture line (home-action-today) inside that section. Remaining sections
    # keep their relative order inside folded details blocks.
    order = [
        "home-portfolio-command",
        "home-current-holdings",
        "home-core-judgment",
        "home-action-today",
        "home-material-changes",
        "home-predictions",
        "home-forecast-accountability",
        "home-reasoning-chain",
        "home-scenario-outlook",
        "home-action-playbook",
        "home-candidate-board",
    ]
    offsets = [html.find(f'id="{item}"') for item in order]
    checks["portfolio_first_chain_order"] = all(value >= 0 for value in offsets) and offsets == sorted(offsets)
    checks["candidate_score_separate_from_cde"] = "CDE" in html and (
        "尚未形成有证据支持的 0-100 分评分" in html
        or "evidence-backed 0-100 score has not been assigned" in html
    )
    checks["no_fake_multiday_zero"] = "5d 0.0%, 20d 0.0%" not in html
    checks["portfolio_history_available"] = bool(observations) and all(
        item.get("change_5d_pct") is not None
        and item.get("change_20d_pct") is not None
        and item.get("change_60d_pct") is not None
        for item in observations
    )
    checks["no_private_amount_fields"] = not any(token in html.lower() for token in ("account_value", "net_worth", "cost_basis", "broker_account"))

    candidates = _candidate_score_board(
        {"items": [{"asset": "泰金新能（688813）", "current_priority": "S", "evidence_strength": "Unverified"}]}
    ).get("items", [])
    checks["candidate_ticker_extracted"] = bool(candidates) and candidates[0].get("code") == "688813.SH"
    checks["candidate_unscored_remains_na"] = bool(candidates) and candidates[0].get("strategic_candidate_score") == "N/A"
    checks["candidate_identity_registry_validated"] = bool(candidates) and candidates[0].get("identity_status") == "Validated"

    scenario_signatures = []
    for asset in ("PORT_A", "PORT_B", "PORT_C", ""):
        portfolio = {
            "exposure_map": {"asset_concentration": ([{"asset": asset, "exposure_pct": 60.0}] if asset else [])},
        }
        scenario = _scenario_outlook({}, market, portfolio, {"metrics": {"evaluated": 0}})
        scenario_signatures.append(scenario["items"][0]["portfolio_sensitivity"])
    checks["portfolio_scenario_differential"] = len(set(scenario_signatures)) == 4

    tracked_private = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "runtime/config/user_config.json"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    checks["private_runtime_config_untracked"] = tracked_private.returncode != 0

    evidence.update(
        {
            "tick_counter_present": bool(state.get("tick_counter")),
            "market_observation_count": len(observations),
            "usable_observation_count": len(usable),
            "channel_status_counts": _counts(channels.values()),
            "configured_provider_present": bool(provider.get("active_provider")),
            "latest_inference_status": trace.get("latest_inference_status"),
            "portfolio_scenario_signatures": scenario_signatures,
        }
    )
    failures = [name for name, passed in checks.items() if not passed]
    result = {"status": "PASS" if not failures else "FAIL", "checks": checks, "evidence": evidence, "failures": failures}
    (ARTIFACT_DIR / "goal_validation_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def _live_state() -> dict[str, Any]:
    with urllib.request.urlopen("http://127.0.0.1:8765/state", timeout=15) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload if isinstance(payload, dict) else {}


def _counts(values: Any) -> dict[str, int]:
    output: dict[str, int] = {}
    for value in values:
        key = str(value).upper()
        output[key] = output.get(key, 0) + 1
    return output


if __name__ == "__main__":
    raise SystemExit(main())
