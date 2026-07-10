#!/usr/bin/env python3
"""Validate the Atlas OS User Decision Home rebuild.

The validator checks read-only presentation behavior only. It does not mutate
cognition, create forecasts, alter candidate semantics, change portfolio state,
or execute trades.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ui.app_server import state_api  # noqa: E402
from ui.i18n.i18n import current_language, set_language  # noqa: E402
from ui.pages.product_views import candidate_pool_content, home_content  # noqa: E402
from ui.presentation.home_intelligence import build_home_intelligence  # noqa: E402


ARTIFACT_DIR = ROOT / "99_Verification" / "artifacts" / "user_decision_home"
EXPECTED_JOURNEY = [
    "what_changed",
    "strongest_judgment",
    "portfolio_relevance",
    "decision_agenda",
    "view_change_triggers",
    "research_priorities",
]
OLD_HOME_IDS = [
    "home-current-state",
    "home-forward-outlook",
    "home-portfolio-impact",
    "home-research-candidates",
]
FORBIDDEN_ACTION_WORDS = re.compile(r"\b(Buy|Sell|Strong Buy|Must Buy|买入|卖出)\b", re.IGNORECASE)


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    original_language = current_language()
    results: list[dict[str, Any]] = []
    try:
        state = state_api()
        intelligence = build_home_intelligence(state)
        results.extend(validate_decision_home_model(intelligence))
        for language in ("zh", "en"):
            set_language(language)
            state = state_api()
            home_html = home_content(state)
            candidates_html = candidate_pool_content(state)
            (ARTIFACT_DIR / f"home_{language}.html").write_text(home_html, encoding="utf-8")
            (ARTIFACT_DIR / f"candidates_{language}.html").write_text(candidates_html, encoding="utf-8")
            results.extend(validate_home_html(home_html, language))
            results.extend(validate_candidate_page(candidates_html, language))
    finally:
        set_language(original_language)
    summary = {
        "status": "PASS" if all(item["passed"] for item in results) else "FAIL",
        "checks": results,
    }
    (ARTIFACT_DIR / "validator_results.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["status"] == "PASS" else 1


def validate_decision_home_model(intelligence: dict[str, Any]) -> list[dict[str, Any]]:
    decision_home = intelligence.get("decision_home") if isinstance(intelligence.get("decision_home"), dict) else {}
    core = decision_home.get("core_judgment") if isinstance(decision_home.get("core_judgment"), dict) else {}
    forward = decision_home.get("strongest_forward_view") if isinstance(decision_home.get("strongest_forward_view"), dict) else {}
    hierarchy = decision_home.get("conviction_hierarchy") if isinstance(decision_home.get("conviction_hierarchy"), dict) else {}
    agenda = decision_home.get("decision_agenda") if isinstance(decision_home.get("decision_agenda"), dict) else {}
    triggers = decision_home.get("decision_triggers") if isinstance(decision_home.get("decision_triggers"), dict) else {}
    research = decision_home.get("research_priorities") if isinstance(decision_home.get("research_priorities"), dict) else {}
    forecast = decision_home.get("forecast_accountability") if isinstance(decision_home.get("forecast_accountability"), dict) else {}
    boundaries = decision_home.get("source_boundaries") if isinstance(decision_home.get("source_boundaries"), dict) else {}
    truth = research.get("candidate_priority_truth") if isinstance(research.get("candidate_priority_truth"), dict) else {}
    return [
        check("journey order is mandatory six-question sequence", decision_home.get("journey_order") == EXPECTED_JOURNEY),
        check("first viewport exposes exactly four primary blocks", len(decision_home.get("first_viewport_blocks", [])) == 4),
        check("one core judgment exists", bool(core.get("title")) and core.get("question") == "what_changed"),
        check("one strongest forward view exists", bool(forward.get("statement")) and bool(forward.get("horizon"))),
        check("forward view includes confidence", "confidence" in forward and "confidence_text" in forward),
        check("forward view includes falsification condition", bool(forward.get("falsification_condition"))),
        check("conviction hierarchy level 1 has exactly one item", len(hierarchy.get("level_1", [])) == 1),
        check("conviction hierarchy level 2 has max three key predictions", len(hierarchy.get("level_2", [])) <= 3),
        check("agenda posture maps to Atlas allowed action", agenda.get("posture") in {"observe", "hold", "reduce", "build", "accumulate"}),
        check("decision agenda has max three focus items", len(agenda.get("focus_items", [])) <= 3),
        check("positive triggers visible in model", len(triggers.get("positive_confirmation", [])) >= 1),
        check("negative triggers visible in model", len(triggers.get("negative_confirmation", [])) >= 1),
        check("research priorities max three", len(research.get("items", [])) <= 3),
        check("candidate priority truth is explicit", "Static Research Pool" in str(truth.get("classification", ""))),
        check("forecast compact exposes only required count keys", set(forecast.get("counts", {}).keys()) == {"open", "verified", "invalidated", "inconclusive"}),
        check("expert analysis marked collapsed by default", decision_home.get("expert_analysis", {}).get("collapsed_by_default") is True),
        check("presentation boundaries preserved", boundaries.get("read_only") is True and boundaries.get("no_trading_execution") is True),
    ]


def validate_home_html(html: str, language: str) -> list[dict[str, Any]]:
    if language == "zh":
        required_terms = [
            "发生了什么？",
            "Atlas 最强判断是什么？",
            "这和我有什么关系？",
            "我现在该关注什么？",
            "什么会改变判断？",
            "哪里值得深入研究？",
            "今日核心判断",
            "最强前瞻判断",
            "组合相关性",
            "决策议程",
            "支持增强",
            "风险恶化",
            "今天最值得深入研究",
            "预测责任检查",
        ]
    else:
        required_terms = [
            "What changed?",
            "What is Atlas&#x27;s strongest judgment?",
            "What does this mean for me?",
            "What should I focus on now?",
            "What would change the view?",
            "What deserves deeper research?",
            "Today&#x27;s Core Judgment",
            "Strongest Forward View",
            "Portfolio Relevance",
            "Decision Agenda",
            "Positive confirmation",
            "Negative confirmation",
            "Today&#x27;s Top 3 Research Priorities",
            "Forecast Accountability",
        ]
    checks = [
        check(f"{language} home uses user decision journey layout", 'data-home-layout="user-decision-journey"' in html),
        check(f"{language} home has four primary blocks", html.count("data-primary-block=") == 4),
        check(f"{language} home has one core judgment card", html.count('id="home-core-judgment"') == 1),
        check(f"{language} home has one strongest forward view card", html.count('id="home-strongest-forward-view"') == 1),
        check(f"{language} home shows horizon", ("观察周期" in html if language == "zh" else "Horizon" in html)),
        check(f"{language} home shows confidence", ("置信度" in html if language == "zh" else "Confidence" in html)),
        check(f"{language} home has max three focus items", _count_between(html, 'id="home-focus-items"', "</ol>", "<li>") <= 3),
        check(f"{language} home has exactly three research priorities", html.count("data-research-priority=") == 3),
        check(f"{language} home links full candidate pool", 'href="/candidates"' in html),
        check(f"{language} home links all forecasts", 'href="/predictions"' in html),
        check(f"{language} home links learning record", 'href="/learning"' in html),
        check(f"{language} home does not render candidate table", '<div class="candidate-table"' not in html),
        check(f"{language} home does not render candidate filters", "data-candidate-filter" not in html),
        check(f"{language} home does not render old equal-weight IDs", not any(old_id in html for old_id in OLD_HOME_IDS)),
        check(f"{language} home does not render old scenario grid", '<div class="home-scenario-grid"' not in html),
        check(f"{language} expert analysis is collapsed in markup", '<details class="expert-details home-expert-panel" id="expert-analysis-panel" open' not in html),
        check(f"{language} home has no forbidden buy/sell wording", FORBIDDEN_ACTION_WORDS.search(html) is None),
    ]
    checks.extend(check(f"{language} required term: {term}", term in html) for term in required_terms)
    return checks


def validate_candidate_page(html: str, language: str) -> list[dict[str, Any]]:
    title = "候选池" if language == "zh" else "Candidate Pool"
    return [
        check(f"{language} full candidate pool route remains available", title in html),
        check(f"{language} candidate page still has filters", "data-candidate-filter" in html),
        check(f"{language} candidate page still has candidate table", '<div class="candidate-table"' in html),
        check(f"{language} candidate page has no forbidden buy/sell wording", FORBIDDEN_ACTION_WORDS.search(html) is None),
    ]


def _count_between(text: str, start: str, end: str, needle: str) -> int:
    start_index = text.find(start)
    if start_index < 0:
        return 0
    end_index = text.find(end, start_index)
    if end_index < 0:
        end_index = len(text)
    return text[start_index:end_index].count(needle)


def check(name: str, passed: bool) -> dict[str, Any]:
    return {"name": name, "passed": bool(passed)}


if __name__ == "__main__":
    raise SystemExit(main())
