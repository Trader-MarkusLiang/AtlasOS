#!/usr/bin/env python3
"""Validate the Atlas OS Home Intelligence Surface.

This validator checks presentation completeness only. It does not mutate
cognition, create forecasts, modify portfolios, or execute trades.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ui.app_server import state_api  # noqa: E402
from ui.i18n.i18n import current_language, set_language  # noqa: E402
from ui.pages.product_views import candidate_pool_content, home_content  # noqa: E402
from ui.presentation.home_intelligence import build_home_intelligence  # noqa: E402


ARTIFACT_DIR = ROOT / "99_Verification" / "artifacts" / "home_intelligence"


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    original_language = current_language()
    results: list[dict[str, object]] = []
    try:
        state = state_api()
        intelligence = build_home_intelligence(state)
        results.extend(validate_state_projection(state, intelligence))
        for language in ("zh", "en"):
            set_language(language)
            state = state_api()
            home_html = home_content(state)
            candidate_html = candidate_pool_content(state)
            (ARTIFACT_DIR / f"validator_home_{language}.html").write_text(home_html, encoding="utf-8")
            (ARTIFACT_DIR / f"validator_candidates_{language}.html").write_text(candidate_html, encoding="utf-8")
            results.extend(validate_home_html(home_html, language))
            results.extend(validate_candidate_html(candidate_html, language))
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


def validate_state_projection(state: dict[str, object], intelligence: dict[str, object]) -> list[dict[str, object]]:
    candidate_pool = state.get("candidate_pool") if isinstance(state.get("candidate_pool"), dict) else {}
    forecast_ledger = state.get("forecast_ledger") if isinstance(state.get("forecast_ledger"), dict) else {}
    market_outlook = intelligence.get("market_outlook") if isinstance(intelligence.get("market_outlook"), dict) else {}
    expert = intelligence.get("expert_analysis") if isinstance(intelligence.get("expert_analysis"), dict) else {}
    return [
        check("state exposes candidate_pool", bool(candidate_pool.get("items"))),
        check("state exposes forecast_ledger", "metrics" in forecast_ledger and "forecasts" in forecast_ledger),
        check("market outlook distinct from ledger", market_outlook.get("distinct_from_forecast_ledger") is True),
        check("expert analysis has nine sections", int(expert.get("section_count", 0) or 0) >= 9),
        check("candidate ranking safety flag", candidate_pool.get("candidate_ranking_not_buy_recommendation") is True),
    ]


def validate_home_html(html: str, language: str) -> list[dict[str, object]]:
    if language == "zh":
        terms = ["当前状态", "市场前瞻", "组合影响", "研究候选", "预测与兑现", "专家分析", "原始证据"]
        safety = "候选排序不是交易动作"
    else:
        terms = [
            "Current State",
            "Market Outlook",
            "Portfolio Impact",
            "Research Candidates",
            "Forecast Accountability",
            "Expert Analysis",
            "Raw Evidence",
        ]
        safety = "Candidate Ranking is not a trading action"
    checks = [check(f"{language} home contains {term}", term in html) for term in terms]
    checks.extend(
        [
            check(f"{language} home includes candidate safety", safety in html),
            check(f"{language} home no Buy/Sell candidate action", "Buy" not in html and "Sell" not in html),
            check(f"{language} home has forecast link", 'href="/predictions"' in html),
            check(f"{language} home has candidate route link", 'href="/candidates"' in html),
            check(f"{language} home has expert raw nested details", "raw-evidence-details" in html),
            check(f"{language} home has candidate filters", "data-candidate-filter" in html),
        ]
    )
    return checks


def validate_candidate_html(html: str, language: str) -> list[dict[str, object]]:
    title = "研究候选" if language == "zh" else "Research Candidates"
    return [
        check(f"{language} candidates page title", title in html),
        check(f"{language} candidates page has details", "candidate-detail" in html),
        check(f"{language} candidates page no Buy/Sell", "Buy" not in html and "Sell" not in html),
    ]


def check(name: str, passed: bool) -> dict[str, object]:
    return {"name": name, "passed": bool(passed)}


if __name__ == "__main__":
    raise SystemExit(main())
