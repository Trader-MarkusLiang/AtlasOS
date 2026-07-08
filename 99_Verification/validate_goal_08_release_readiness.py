"""GOAL 08 release-readiness tribunal.

This validator audits current evidence from GOAL 01 through GOAL 07 and
classifies Atlas OS maturity without creating new cognition, trading logic, or
runtime semantics. It treats missing long-duration and market-channel evidence
as release risks instead of silently upgrading them.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "99_Verification/artifacts/goal_08_release_readiness"
RESULT_PATH = ARTIFACT_DIR / "tribunal_result.json"

REQUIRED_COMPLETED_GOALS = [
    "GOAL_00_TRUTH_BASELINE",
    "GOAL_01_USER_ACTIVATION",
    "GOAL_02_LIVE_LLM_ACTIVATION",
    "GOAL_03_MARKET_INTELLIGENCE",
    "GOAL_04_PORTFOLIO_COGNITION",
    "GOAL_05_FORECAST_ACCOUNTABILITY",
    "GOAL_06_SELF_ITERATION_REALITY",
    "GOAL_07_AUTONOMOUS_OPERATIONS",
]

EVIDENCE_LEVELS = {
    "LIVE_PROVEN",
    "REAL_RUNTIME_PROVEN",
    "CONTROLLED_FIXTURE_PROVEN",
    "ACCELERATED_ONLY",
    "PARTIAL",
    "FAILED",
    "EXTERNAL_BLOCKER",
}


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    status = _json("docs/goals/status/GOAL_STATUS.json")
    goal01 = _json("99_Verification/artifacts/goal_01_user_activation_fixed/browser_journey_result.json")
    goal02_live = _json("99_Verification/artifacts/goal_02_live_llm_activation/live_smoke_result.json")
    goal02_matrix = _json("99_Verification/artifacts/goal_02_live_llm_activation/failure_matrix_result.json")
    goal03 = _json("99_Verification/artifacts/goal_03_market_intelligence/live_runtime_result.json")
    goal04 = _json("99_Verification/artifacts/goal_04_portfolio_cognition/differential_result.json")
    goal05 = _json("99_Verification/artifacts/goal_05_forecast_accountability/lifecycle_result.json")
    goal06 = _json("99_Verification/artifacts/goal_06_self_iteration_reality/treatment_control_result.json")
    goal07 = _json("99_Verification/artifacts/goal_07_autonomous_operations/operations_result.json")
    goal07_long = _json("99_Verification/artifacts/goal_07_autonomous_operations/long_soak_2h_result.json")

    checks: dict[str, bool] = {}
    tribunal: dict[str, dict[str, Any]] = {}

    _check("status_cursor_goal_08", status.get("current_goal") == "GOAL_08_RELEASE_READINESS", checks)
    _check(
        "goals_00_to_07_completed",
        all(goal in set(status.get("completed_goals", [])) for goal in REQUIRED_COMPLETED_GOALS),
        checks,
    )
    _check(
        "goal_08_status_consistent",
        status.get("status") == "IN_PROGRESS"
        or (
            status.get("status") == "COMPLETE"
            and "GOAL_08_RELEASE_READINESS" in set(status.get("completed_goals", []))
            and status.get("master_goal", {}).get("classification") == "PRODUCTION_TRIAL_CANDIDATE"
        ),
        checks,
    )

    goal01_steps = {item.get("step"): item for item in goal01.get("steps", [])}
    _check("first_time_user_flow_artifact", {"open_setup_en", "setup_start_runtime", "ask_atlas", "stop_runtime"}.issubset(goal01_steps), checks)
    _check("first_time_user_language_zh", goal01_steps.get("setup_zh_after_save", {}).get("hasZhTitle") is True, checks)
    _check("first_time_user_report_pass", "`PROVEN_COMPLETE`" in _text("99_Verification/GOAL_01_User_Activation_Report.md"), checks)

    _check("live_llm_provider_proven", goal02_live.get("classification") == "LIVE_PROVEN", checks)
    _check("llm_decision_contract_valid", goal02_live.get("active_chain_smoke", {}).get("decision_contract_packet_valid") is True, checks)
    _check("llm_fallback_matrix_pass", goal02_matrix.get("status") == "PASS" and not goal02_matrix.get("failures"), checks)
    _check("llm_telemetry_secret_safe", goal02_live.get("security", {}).get("raw_secret_committed") is False, checks)

    channels = goal03.get("runtime_summary", {}).get("channels", {})
    _check("live_market_price_volume", goal03.get("status") == "PASS" and channels.get("price_volume") == "LIVE", checks)
    _check("market_missing_channels_explicit", all(channels.get(key) == "NOT_CONFIGURED" for key in ["market_breadth", "news_announcement", "narrative_attention", "macro_policy"]), checks)
    _check("market_ui_freshness_visible", goal03.get("ui_visibility", {}).get("state_api_freshness_visible") is True, checks)
    _check("market_no_trading_execution", goal03.get("safety", {}).get("no_trading_execution") is True, checks)

    portfolio_cases = goal04.get("cases", {})
    _check("portfolio_differential_pass", goal04.get("status") == "PASS" and not goal04.get("failures"), checks)
    _check(
        "portfolio_multiple_cases",
        {"portfolio_a_ai_hardware", "portfolio_b_cash_proxy", "portfolio_c_single_theme", "no_portfolio"}.issubset(portfolio_cases),
        checks,
    )
    _check(
        "portfolio_no_private_amounts",
        goal04.get("checks", {}).get("no_private_amounts") is True and goal04.get("safety", {}).get("no_exact_amounts") is True,
        checks,
    )

    _check("forecast_lifecycle_pass", goal05.get("status") == "PASS" and not goal05.get("failures"), checks)
    _check(
        "forecast_required_cases",
        {
            "goal05_hit",
            "goal05_miss",
            "goal05_inconclusive",
            "goal05_high_confidence_miss",
            "goal05_low_confidence_hit",
        }.issubset(goal05.get("cases", {})),
        checks,
    )
    _check("forecast_metrics_computed", goal05.get("metrics", {}).get("evaluated", 0) >= 5, checks)

    _check("self_iteration_behavioral_loop", goal06.get("classification") == "REAL_RUNTIME_BEHAVIORAL_LOOP", checks)
    _check("self_iteration_pass", goal06.get("status") == "PASS" and not goal06.get("failures"), checks)
    _check("self_iteration_feedback_applied", goal06.get("comparison", {}).get("treatment_feedback_status") == "applied", checks)

    _check("daily_cycle_pass", goal07.get("status") == "PASS" and not goal07.get("failures"), checks)
    _check("daily_all_phases", set(goal07.get("daily_cycles", {})) == {"morning", "intraday", "post_market", "overnight"}, checks)
    _check("recovery_matrix_pass", all(item.get("status") == "passed" for item in goal07.get("recovery", {}).values()), checks)
    _check("two_hour_soak_pass", goal07_long.get("status") == "PASS" and goal07_long.get("classification") == "REAL_DURATION_2H_PROVEN", checks)
    _check("two_hour_zero_tick_errors", goal07_long.get("tick_errors") == 0 and goal07_long.get("runtime_log_lines", 0) >= 721, checks)
    _check("two_hour_no_trading_execution", goal07_long.get("no_trading_execution") is True, checks)

    _check("python_compile_regression", _compile_targets(), checks)
    _check("diff_check_clean", _run(["git", "diff", "--check"]).returncode == 0, checks)
    _check("secret_shape_scan_clean", not _tracked_secret_hits(), checks)

    tribunal["background_runtime"] = _item("REAL_RUNTIME_PROVEN", "Daemon, EventStream, DecisionLoop, persistence, scheduler sleep, and two-hour loop are proven.")
    tribunal["llm_routing"] = _item("LIVE_PROVEN", "Volcano fallback route and Decision Contract parse were live-proven; failure matrix is repeatable.")
    tribunal["market_awareness"] = _item("LIVE_PROVEN", "At least one live price/volume observation reached daemon/EventStream/DecisionLoop/UI.")
    tribunal["market_freshness"] = _item("PARTIAL", "Price/volume freshness is visible; breadth/news/macro/narrative remain NOT_CONFIGURED.")
    tribunal["portfolio_cognition"] = _item("REAL_RUNTIME_PROVEN", "UI-configured portfolios change normal runtime output under same market state.")
    tribunal["forecast_accountability"] = _item("REAL_RUNTIME_PROVEN", "Forecast lifecycle records expectations before outcomes and computes errors.")
    tribunal["self_iteration"] = _item("REAL_RUNTIME_PROVEN", "Treatment/control forecast miss changes later trust, hypothesis scores, and structural shift.")
    tribunal["autonomous_operations"] = _item("REAL_RUNTIME_PROVEN", "Daily phases, recovery, 500 accelerated cycles, and 2h real-duration soak are proven.")
    tribunal["ui_usability"] = _item("REAL_RUNTIME_PROVEN", "First-time setup/start/ask/stop path has browser and repeatable validation evidence.")
    tribunal["bilingual_parity"] = _item("PARTIAL", "Primary setup/home zh/en path is proven; exhaustive page-level parity is not proven.")
    tribunal["recovery"] = _item("REAL_RUNTIME_PROVEN", "Daemon restart, UI restart, stale PID, malformed JSONL, provider outage, and market outage passed.")
    tribunal["stability"] = _item("PARTIAL", "2h real-duration stability is proven; 24h unattended stability is not proven.")
    tribunal["security"] = _item("REAL_RUNTIME_PROVEN", "Secret masking, no raw secret artifact, and tracked secret-shape scan passed.")

    for item in tribunal.values():
        if item["classification"] not in EVIDENCE_LEVELS:
            raise ValueError(f"invalid evidence label: {item['classification']}")

    failures = [key for key, value in checks.items() if value is not True]
    release_risks = [
        "24h unattended stability is not proven.",
        "Breadth/news/macro/narrative live market channels remain NOT_CONFIGURED.",
        "Bilingual parity is proven on primary path, not every UI page.",
        "Provider long-run stability sample is small and the 2h soak used failsafe provider degradation.",
        "Stale UI server guard remains a known product risk.",
    ]
    final_classification = _final_classification(failures, tribunal)
    result = {
        "date": status.get("last_updated") or datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "final_classification": final_classification,
        "checks": checks,
        "failures": failures,
        "tribunal": tribunal,
        "release_risks": release_risks,
        "master_goal_status_recommendation": "COMPLETE" if not failures else "BLOCKED_WITH_EVIDENCE",
        "rc_readiness": "NOT_RC_READY",
        "production_ready_claim_allowed": False,
        "release_candidate_claim_allowed": False,
        "live_market_complete_claim_allowed": False,
        "twenty_four_hour_stability_claim_allowed": False,
        "no_trading_execution": True,
    }
    RESULT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


def _json(rel: str) -> dict[str, Any]:
    path = ROOT / rel
    return json.loads(path.read_text(encoding="utf-8"))


def _text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def _check(name: str, condition: bool, checks: dict[str, bool]) -> None:
    checks[name] = bool(condition)


def _item(classification: str, evidence: str) -> dict[str, str]:
    return {"classification": classification, "evidence": evidence}


def _compile_targets() -> bool:
    targets = sorted(str(path.relative_to(ROOT)) for path in (ROOT / "99_Verification").glob("validate_goal_*.py"))
    targets.append("99_Verification/run_goal_07_long_soak.py")
    return _run([sys.executable, "-m", "py_compile", *targets]).returncode == 0


def _tracked_secret_hits() -> list[str]:
    secret_pattern = re.compile(r"sk-[A-Za-z0-9_-]{20,}|Bearer\s+[A-Za-z0-9_\-.]{20,}")
    result = _run(["git", "ls-files"])
    hits: list[str] = []
    for rel in result.stdout.splitlines():
        path = ROOT / rel
        if not path.is_file() or path.suffix in {".png", ".jpg", ".jpeg", ".gif", ".sqlite"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if secret_pattern.search(text):
            hits.append(rel)
    return hits


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, check=False)


def _final_classification(failures: list[str], tribunal: dict[str, dict[str, Any]]) -> str:
    if failures:
        return "NOT_READY"
    labels = {name: item["classification"] for name, item in tribunal.items()}
    core_ready = all(
        labels.get(name) in {"LIVE_PROVEN", "REAL_RUNTIME_PROVEN"}
        for name in [
            "background_runtime",
            "llm_routing",
            "market_awareness",
            "portfolio_cognition",
            "forecast_accountability",
            "self_iteration",
            "autonomous_operations",
            "ui_usability",
            "recovery",
            "security",
        ]
    )
    release_candidate_ready = core_ready and all(value in {"LIVE_PROVEN", "REAL_RUNTIME_PROVEN"} for value in labels.values())
    if release_candidate_ready:
        return "RELEASE_CANDIDATE"
    if core_ready:
        return "PRODUCTION_TRIAL_CANDIDATE"
    if any(value in {"REAL_RUNTIME_PROVEN", "LIVE_PROVEN"} for value in labels.values()):
        return "INTERNAL_ALPHA"
    return "INTERNAL_DEVELOPMENT_ONLY"


if __name__ == "__main__":
    raise SystemExit(main())
