"""Validate Atlas productization backbone without private config or live keys."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.forecast_ledger import create_forecast, evaluate_forecast, list_forecasts
from runtime.daily_cycle import current_daily_cycle
from runtime.market_intelligence import market_observation_to_event, refresh_market_intelligence
from runtime.portfolio_context import build_portfolio_context
from ui.app_server import state_api
from ui.pages.home import render_home_page
from ui.pages.markets import render_markets_page
from ui.pages.portfolio import render_portfolio_page
from ui.pages.predictions import render_predictions_page
from ui.pages.setup import render_setup_page


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        db_path = root / "atlas_test.sqlite"
        config_path = root / "user_config.json"
        config_path.write_text(
            json.dumps(
                {
                    "assets": {
                        "portfolio_json": json.dumps(
                            [
                                {
                                    "asset": "AAPL",
                                    "market": "US",
                                    "portfolio_percentage": 12,
                                    "theme": "AI Infrastructure",
                                    "role": "Core",
                                },
                                {
                                    "asset": "700.HK",
                                    "market": "HK",
                                    "portfolio_percentage": 8,
                                    "theme": "China Internet",
                                    "role": "Satellite",
                                },
                            ]
                        )
                    }
                }
            ),
            encoding="utf-8",
        )
        os.environ["ATLAS_USER_CONFIG"] = str(config_path)
        os.environ["ATLAS_RUNTIME_DB"] = str(db_path)

        portfolio = build_portfolio_context(config_path=str(config_path))
        assert portfolio["status"] == "configured"
        assert portfolio["portfolio_consistency"] == "PASS"
        assert portfolio["privacy"] == "percentage_only_no_account_amounts"
        serialized_portfolio = json.dumps(portfolio).lower()
        for forbidden in ("account_value", "net_worth", "cost_basis", "broker", "balance"):
            assert forbidden not in serialized_portfolio

        routed = market_observation_to_event(
            {
                "timestamp": "2026-07-08T00:00:00+00:00",
                "source": "test",
                "source_type": "market_data_provider",
                "asset": "AAPL",
                "theme": "AI Infrastructure",
                "market": "US",
                "freshness": "Available",
                "confidence": 0.8,
                "raw_reference": {"provider": "test"},
                "normalized_event_type": "price_breakout",
                "data_quality_status": "Available",
            }
        )
        assert routed["event_type"] == "volume_price_breakout"
        assert routed["payload"]["asset"] == "AAPL"

        empty_config = root / "empty_config.json"
        empty_config.write_text(json.dumps({"assets": {"portfolio_json": "[]"}}), encoding="utf-8")
        market = refresh_market_intelligence(config_path=str(empty_config), db_path=str(db_path), enqueue=True)
        assert market["status"] == "no_configured_assets"
        assert market["events_enqueued"] == 0

        forecast = create_forecast(
            {
                "horizon": "3 ticks",
                "subject": "attention breadth",
                "forecast_statement": "attention likely to broaden",
                "expected_direction_state": "broaden",
                "confidence": 0.62,
                "active_hypothesis": "attention_flow",
                "causal_drivers": ["attention", "liquidity"],
                "invalidation_conditions": ["attention narrows"],
                "expected_observation_window": "next simulated window",
            },
            db_path=str(db_path),
        )
        evaluated = evaluate_forecast(
            forecast["forecast_id"],
            {"actual_outcome": "attention did broaden across configured assets"},
            db_path=str(db_path),
        )
        assert evaluated["status"] == "VERIFIED"
        ledger = list_forecasts(db_path=str(db_path))
        assert ledger["metrics"]["evaluated"] == 1
        assert ledger["metrics"]["minimum_sample_size_met"] is False
        daily = current_daily_cycle(db_path=str(db_path))
        assert daily["phase"] in {"morning", "intraday", "post_market", "overnight"}
        assert daily["forecast_review"]["evaluated"] == 1

        state = state_api()
        assert "portfolio_context" in state
        assert "market_intelligence" in state
        assert "daily_cycle" in state
        assert "Today&apos;s Atlas Brief" in render_home_page(state)
        assert "Portfolio Context" in render_portfolio_page(portfolio)
        assert "Market Intelligence" in render_markets_page(market)
        assert "Forecast Ledger" in render_predictions_page(ledger)
        assert "Set up Atlas OS" in render_setup_page({})

    print(
        json.dumps(
            {
                "status": "PASS",
                "validated": [
                    "portfolio_context_privacy",
                    "market_router_mapping",
                    "market_refresh_degraded_mode",
                    "forecast_ledger_evaluation",
                    "daily_cycle_metadata",
                    "state_api_product_fields",
                    "product_pages_render",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
