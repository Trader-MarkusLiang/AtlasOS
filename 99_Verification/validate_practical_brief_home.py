#!/usr/bin/env python3
"""Validate the Atlas OS Practical Decision Brief Home contract.

This validator is intentionally UI/presentation scoped. It does not mutate
runtime state, cognition, forecasts, portfolio config, or trading authority.
"""

from __future__ import annotations

import json
import re
import sys
from html import unescape
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from ui.app_server import state_api
import ui.pages.product_views as product_views
from ui.presentation.home_intelligence import build_home_intelligence


ARTIFACT_DIR = Path("99_Verification/artifacts/practical_brief")
RESULT_PATH = ARTIFACT_DIR / "validator_result.json"


def check(name: str, passed: bool, details: Any, results: list[dict[str, Any]]) -> None:
    results.append({"name": name, "passed": bool(passed), "details": details})


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    state = state_api()
    intelligence = build_home_intelligence(state)
    brief = intelligence["practical_brief"]
    original_language = product_views.current_language
    try:
        product_views.current_language = lambda: "zh"  # type: ignore[assignment]
        html = product_views.home_content(state)
        product_views.current_language = lambda: "en"  # type: ignore[assignment]
        html_en = product_views.home_content(state)
    finally:
        product_views.current_language = original_language  # type: ignore[assignment]
    html_lower = html.lower()
    html_en_lower = html_en.lower()
    html_text = unescape(html)
    html_en_text = unescape(html_en)
    results: list[dict[str, Any]] = []

    chain = brief.get("chain_order", [])
    expected_chain = [
        "action_today",
        "core_judgment",
        "strongest_predictions",
        "ai_bottleneck_index",
        "capital_relay",
        "current_holdings",
        "capital_allocation",
        "waiting_triggers",
        "research_tasks",
        "intelligence_alerts",
        "counter_argument",
        "review_plan",
    ]

    check("A_home_begins_with_action_today", "home-action-today" in html and html.find("home-action-today") < html.find("home-core-judgment"), chain, results)
    core = brief.get("core_judgment", {})
    check("B_one_line_core_judgment", bool(core.get("headline")) and bool(core.get("supporting_sentence")), core, results)
    predictions = brief.get("strongest_predictions", {}).get("items", [])
    check("C_strongest_predictions_max_3", isinstance(predictions, list) and len(predictions) <= 3, len(predictions), results)
    prediction_fields_ok = all(
        item.get("confidence") is not None and item.get("horizon") and item.get("evidence") and item.get("invalidation")
        for item in predictions
        if isinstance(item, dict)
    )
    check("D_prediction_required_fields", prediction_fields_ok, predictions, results)
    bottlenecks = brief.get("ai_bottleneck_index", {}).get("domains", [])
    required_domains = {"Memory", "Equipment", "Materials", "Bandwidth", "Power"}
    found_domains = {str(item.get("domain")) for item in bottlenecks if isinstance(item, dict)}
    check("E_ai_bottleneck_index_exists", required_domains.issubset(found_domains), sorted(found_domains), results)
    relay = brief.get("capital_relay", {})
    check("F_capital_relay_exists", bool(relay.get("path")) and relay.get("status") == "available", relay, results)
    holdings = brief.get("current_holdings", {}).get("holdings", [])
    configured_assets = [str(item.get("asset")) for item in state.get("portfolio_context", {}).get("positions", []) if isinstance(item, dict)]
    home_assets = [str(item.get("asset")) for item in holdings if isinstance(item, dict)]
    check("G_actual_configured_holdings_connected", home_assets == configured_assets and bool(home_assets), {"home": home_assets, "configured": configured_assets}, results)
    allocation = brief.get("capital_allocation", {})
    check("H_capital_allocation_board_exists", bool(allocation.get("rebalance_today")) and bool(allocation.get("funding_flow")), allocation, results)
    flow = allocation.get("funding_flow", {})
    check("I_funding_source_destination_logic", bool(flow.get("source")) and bool(flow.get("destination")) and "→" in html, flow, results)
    triggers = brief.get("waiting_triggers", {}).get("items", [])
    trigger_statuses = {str(item.get("status")) for item in triggers if isinstance(item, dict)}
    check("J_waiting_triggers_exist", len(triggers) >= 4, len(triggers), results)
    check("K_trigger_state_visible", trigger_statuses.issubset({"MET", "PARTIAL", "NOT_MET", "UNKNOWN"}) and bool(trigger_statuses), sorted(trigger_statuses), results)
    tasks = brief.get("research_tasks", {}).get("items", [])
    check("L_top_3_research_tasks_only", isinstance(tasks, list) and 0 < len(tasks) <= 3, len(tasks), results)
    candidate_rows = html.count("data-candidate-row")
    check("M_full_candidate_pool_not_dumped_on_home", candidate_rows == 0 and "/candidates" in html, {"candidate_rows": candidate_rows}, results)
    truth = brief.get("candidate_source_truth", {})
    check("N_candidate_source_truth_labeled", truth.get("classification") == "static_markdown_manual_priority_with_portfolio_overlay", truth, results)
    alerts = brief.get("intelligence_alerts", {}).get("items", [])
    check("O_intelligence_alerts_compact", 0 < len(alerts) <= 5, len(alerts), results)
    check("P_counter_argument_exists", bool(brief.get("counter_argument", {}).get("thesis")), brief.get("counter_argument"), results)
    check("Q_review_plan_exists", bool(brief.get("review_plan", {}).get("next_review_time")), brief.get("review_plan"), results)
    check("R_forecast_accountability_accessible", "home-forecast-accountability" in html and "/predictions" in html, None, results)
    check("S_expert_analysis_secondary", "home-expert-analysis" in html and "secondary_collapsed" in html, None, results)
    forbidden = ["buy", "sell", "买", "卖"]
    forbidden_hits = {
        "zh": {term: html_lower.find(term) if term.isascii() else html_text.find(term) for term in forbidden},
        "en": {term: html_en_lower.find(term) if term.isascii() else html_en_text.find(term) for term in forbidden},
    }
    check("T_no_buy_sell_language", all(value < 0 for group in forbidden_hits.values() for value in group.values()), forbidden_hits, results)
    private_patterns = [r"\b500000\b", r"50万", r"api[_ -]?key", r"sk-[A-Za-z0-9]"]
    private_hits = [pattern for pattern in private_patterns if re.search(pattern, html, flags=re.IGNORECASE)]
    check("U_no_exact_private_amounts_or_secrets", not private_hits, private_hits, results)
    zh_terms = ["今日是否行动", "今日总判断", "最强预测", "AI 瓶颈指数", "资本迁移", "当前持仓", "资金调度", "等待触发条件", "今日研究任务", "情报与预警", "反方观点", "复盘计划"]
    check("V_chinese_mode_covers_required_chain", all(term in html_text for term in zh_terms), zh_terms, results)
    en_terms = ["Action Today", "Today's Core Judgment", "Highest-Conviction Predictions", "AI Bottleneck Index", "Capital Relay", "Current Holdings", "Capital Allocation Board", "Waiting Triggers", "Today's Research Tasks", "Intelligence & Alerts", "Counter Argument", "Review Plan"]
    check("V2_english_mode_covers_required_chain", all(term in html_en_text for term in en_terms), en_terms, results)
    check("chain_order_exact", chain == expected_chain, chain, results)

    passed = all(item["passed"] for item in results)
    payload = {"passed": passed, "checks": results}
    RESULT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
