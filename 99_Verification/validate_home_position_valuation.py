#!/usr/bin/env python3
"""Validate ISSUE-2026-061 with synthetic private position fixtures only."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.portfolio_context import build_portfolio_context  # noqa: E402
from runtime.portfolio_valuation import (  # noqa: E402
    build_local_portfolio_valuation,
    normalize_local_portfolio_config,
    redact_private_portfolio_config,
    validate_local_portfolio_config,
)
from ui.pages.product_views import home_content, settings_content  # noqa: E402
from ui.pages.settings import load_user_config, save_user_config  # noqa: E402


ARTIFACT_DIR = ROOT / "99_Verification" / "artifacts" / "home_position_valuation"
PRIVATE_KEYS = {
    "average_cost_price",
    "quantity",
    "total_position_cost",
    "current_market_value",
    "unrealized_pnl_amount",
}


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    checks: dict[str, bool] = {}

    positive = _config(cost=100, quantity=10, currency="CNY", show_amounts=True, show_quantity=True)
    negative = _config(cost=100, quantity=10, currency="CNY", show_amounts=True)
    zero = _config(cost=100, quantity=None, currency="CNY")
    valid = validate_local_portfolio_config(positive)
    invalid_cost = validate_local_portfolio_config(_config(cost=0, quantity=10, currency="CNY"))
    invalid_quantity = validate_local_portfolio_config(_config(cost=100, quantity=-1, currency="CNY"))
    missing_currency = validate_local_portfolio_config(_config(cost=100, quantity=10, currency=""))
    checks["test_01_cost_schema_validation"] = (
        valid["status"] == "valid"
        and invalid_cost["status"] == "invalid"
        and invalid_quantity["status"] == "invalid"
        and missing_currency["status"] == "invalid"
    )

    gain = _valuation(positive, latest=125, currency="CNY")
    loss = _valuation(negative, latest=80, currency="CNY")
    flat = _valuation(zero, latest=100, currency="CNY")
    checks["test_02_return_calculation"] = (
        _position(gain).get("unrealized_return_pct") == 25
        and _position(loss).get("unrealized_return_pct") == -20
        and _position(flat).get("unrealized_return_pct") == 0
    )
    checks["test_03_amount_calculation"] = (
        _position(gain).get("total_position_cost") == 1000
        and _position(gain).get("current_market_value") == 1250
        and _position(gain).get("unrealized_pnl_amount") == 250
        and _position(flat).get("current_market_value") is None
    )

    mismatch = _valuation(positive, latest=125, currency="HKD")
    mixed = _mixed_currency_valuation()
    checks["test_04_multi_currency"] = (
        _position(mismatch).get("unrealized_return_pct") is None
        and "PRICE_COST_CURRENCY_MISMATCH" in _position(mismatch).get("limitations", [])
        and "FX_DATA_MISSING_AGGREGATE_VALUATION_LIMITED" in mixed.get("summary", {}).get("limitations", [])
    )

    delayed = _valuation(positive, latest=125, currency="CNY", freshness="DELAYED")
    failed = _valuation(positive, latest=None, currency="CNY", quality="Unavailable", freshness="FAILED")
    simulated = _valuation(positive, latest=125, currency="CNY", source_type="controlled_fixture", freshness="SIMULATED")
    checks["test_05_market_freshness"] = (
        _position(delayed).get("unrealized_return_pct") == 25
        and "PRICE_NOT_LIVE" in _position(delayed).get("limitations", [])
        and _position(failed).get("unrealized_return_pct") is None
        and _position(simulated).get("unrealized_return_pct") is None
    )

    checks["test_06_portfolio_weight_truth"] = (
        gain.get("summary", {}).get("estimated_current_weight_status") == "UNAVAILABLE"
        and _position(gain).get("configured_allocation_pct") == 20
        and "estimated_current_weight_pct" not in _position(gain)
    )

    safe_context = build_portfolio_context(config=positive)
    redacted = redact_private_portfolio_config(positive)
    checks["test_07_privacy"] = (
        not _contains_private_keys(safe_context)
        and "[stored locally]" in redacted.get("assets", {}).get("portfolio_json", "")
        and subprocess.run(
            ["git", "check-ignore", "-q", "runtime/config/user_config.json"], cwd=ROOT, check=False
        ).returncode == 0
    )

    orchestrator_text = (ROOT / "runtime" / "orchestrator.py").read_text(encoding="utf-8")
    checks["test_08_llm_isolation"] = (
        "from runtime.portfolio_valuation" not in orchestrator_text
        and not _contains_private_keys(safe_context)
        and gain.get("not_for_llm") is True
    )

    state = _home_state(safe_context, gain)
    with _language_config("en"):
        html_en = home_content(state)
        settings_en, _ = settings_content(positive, _settings_state())
    checks["test_09_home_rendering"] = all(
        marker in html_en
        for marker in ("Cost vs latest price", "Unrealized return", "+25.00%", "synthetic_provider", "DELAYED")
    )

    hidden_config = _config(cost=100, quantity=10, currency="CNY", show_cost=False, show_return=False)
    hidden = _valuation(hidden_config, latest=125, currency="CNY")
    checks["test_10_privacy_toggle"] = (
        "average_cost_price" not in _position(hidden)
        and "unrealized_return_pct" not in _position(hidden)
        and "quantity" not in _position(hidden)
        and "unrealized_pnl_amount" not in _position(hidden)
    )

    with _language_config("zh"):
        html_zh = home_content(state)
        settings_zh, _ = settings_content(positive, _settings_state())
    checks["test_11_zh_en_parity"] = (
        "平均成本价" in settings_zh
        and "Average cost" in settings_en
        and "成本价与最新价" in html_zh
        and "Cost vs latest price" in html_en
    )

    checks["test_12_browser_contract"] = all(
        marker in html_en
        for marker in ("cost-price-track", "pnl-track", "valuation-provenance", "@media (max-width:640px)")
    )

    protected = [
        "runtime/cognition",
        "runtime/decision_loop.py",
        "runtime/event_fusion.py",
        "runtime/cil.py",
    ]
    diff = subprocess.run(
        ["git", "diff", "--", *protected], cwd=ROOT, capture_output=True, text=True, check=False
    )
    checks["test_13_cognitive_regression"] = diff.returncode == 0 and not diff.stdout.strip()

    malformed = {"assets": {"portfolio_json": "{broken"}}
    missing_market = build_local_portfolio_valuation(config=positive, market_intelligence={})
    checks["test_14_failure_recovery"] = (
        build_local_portfolio_valuation(config=malformed, market_intelligence={}).get("status") == "missing"
        and _position(missing_market).get("valuation_status") == "LIMITED"
        and "MARKET_DATA_MISSING" in _position(missing_market).get("limitations", [])
    )

    checks["settings_save_masks_private_values"] = _settings_save_roundtrip()
    checks["general_state_contract_remains_private"] = "local_portfolio_valuation" not in safe_context
    checks["market_price_currency_present"] = _position(gain).get("price_currency") == "CNY"

    failures = [name for name, passed in checks.items() if not passed]
    result = {
        "issue": "ISSUE-2026-061",
        "status": "PASS" if not failures else "FAIL",
        "checks": checks,
        "failures": failures,
        "fixture_policy": "synthetic_only_no_real_private_values",
        "private_runtime_config": "not_read_or_recorded",
    }
    (ARTIFACT_DIR / "validation_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def _config(
    *,
    cost: Any,
    quantity: Any,
    currency: str,
    show_cost: bool = True,
    show_return: bool = True,
    show_quantity: bool = False,
    show_amounts: bool = False,
) -> dict[str, Any]:
    position = {
        "asset": "SYNTHETIC.SZ",
        "market": "A-share",
        "portfolio_percentage": 20,
        "theme": "Synthetic verification",
        "role": "Test only",
        "average_cost_price": cost,
        "position_currency": currency,
    }
    if quantity is not None:
        position["quantity"] = quantity
    return {
        "ui": {"language": "en"},
        "assets": {
            "portfolio_json": json.dumps({"positions": [position]}),
            "asset_list": ["SYNTHETIC.SZ"],
            "weights": {"SYNTHETIC.SZ": 20},
        },
        "portfolio_privacy": {
            "show_cost_price": show_cost,
            "show_pnl_percentage": show_return,
            "show_quantity": show_quantity,
            "show_amounts": show_amounts,
        },
    }


def _valuation(
    config: Mapping[str, Any],
    *,
    latest: Any,
    currency: str,
    freshness: str = "DELAYED",
    quality: str = "Available",
    source_type: str = "market_data_provider",
) -> dict[str, Any]:
    observation = {
        "asset": "SYNTHETIC.SZ",
        "market": "A-share",
        "latest_price": latest,
        "price_currency": currency,
        "source": "synthetic_provider",
        "source_type": source_type,
        "timestamp": "2026-07-14T00:00:00+08:00",
        "freshness": freshness,
        "data_quality_status": quality,
        "raw_reference": {"ticker": "SYNTHETIC.SZ"},
    }
    return build_local_portfolio_valuation(config=config, market_intelligence={"observations": [observation]})


def _mixed_currency_valuation() -> dict[str, Any]:
    config = _config(cost=100, quantity=10, currency="CNY", show_amounts=True)
    payload = json.loads(config["assets"]["portfolio_json"])
    payload["positions"].append(
        {
            "asset": "SYNTHETIC.HK",
            "market": "HK",
            "portfolio_percentage": 20,
            "average_cost_price": 20,
            "quantity": 10,
            "position_currency": "HKD",
        }
    )
    config["assets"]["portfolio_json"] = json.dumps(payload)
    observations = [
        {
            "asset": "SYNTHETIC.SZ", "market": "A-share", "latest_price": 110,
            "price_currency": "CNY", "source": "synthetic_provider", "source_type": "market_data_provider",
            "timestamp": "2026-07-14T00:00:00+08:00", "freshness": "DELAYED",
            "data_quality_status": "Available", "raw_reference": {"ticker": "SYNTHETIC.SZ"},
        },
        {
            "asset": "SYNTHETIC.HK", "market": "HK", "latest_price": 22,
            "price_currency": "HKD", "source": "synthetic_provider", "source_type": "market_data_provider",
            "timestamp": "2026-07-14T00:00:00+08:00", "freshness": "DELAYED",
            "data_quality_status": "Available", "raw_reference": {"ticker": "SYNTHETIC.HK"},
        },
    ]
    return build_local_portfolio_valuation(config=config, market_intelligence={"observations": observations})


def _home_state(portfolio: Mapping[str, Any], valuation: Mapping[str, Any]) -> dict[str, Any]:
    observation = {
        "asset": "SYNTHETIC.SZ", "latest_price": 125, "price_currency": "CNY",
        "source": "synthetic_provider", "source_type": "market_data_provider",
        "timestamp": "2026-07-14T00:00:00+08:00", "freshness": "DELAYED",
        "data_quality_status": "Available", "latest_price_available": True,
        "raw_reference": {"ticker": "SYNTHETIC.SZ"},
    }
    return {
        "timestamp": "2026-07-14T00:00:00+08:00",
        "regime_state": "neutral",
        "portfolio_context": portfolio,
        "local_portfolio_valuation": valuation,
        "market_intelligence": {
            "observations": [observation],
            "channels": {"price_volume": "DELAYED", "portfolio_relevance": "LIVE"},
        },
        "last_decision_packet": {"recommended_action": "observe", "confidence": 0.5, "risk_level": "medium"},
        "forecast_ledger": {"forecasts": [], "metrics": {}},
        "candidate_pool": {"items": [], "changes": []},
    }


def _settings_state() -> dict[str, Any]:
    return {"llm_provider_registry": {"providers": [], "active_provider": ""}, "llm_task_routes": {}, "llm_task_runtime_state": {}}


class _language_config:
    def __init__(self, language: str) -> None:
        self.language = language
        self.previous = os.environ.get("ATLAS_USER_CONFIG")
        self.temp: tempfile.TemporaryDirectory[str] | None = None

    def __enter__(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="atlas-valuation-lang-")
        path = Path(self.temp.name) / "config.json"
        path.write_text(json.dumps({"ui": {"language": self.language}}), encoding="utf-8")
        os.environ["ATLAS_USER_CONFIG"] = str(path)

    def __exit__(self, *_: Any) -> None:
        if self.previous is None:
            os.environ.pop("ATLAS_USER_CONFIG", None)
        else:
            os.environ["ATLAS_USER_CONFIG"] = self.previous
        if self.temp:
            self.temp.cleanup()


def _settings_save_roundtrip() -> bool:
    with tempfile.TemporaryDirectory(prefix="atlas-private-config-") as temp:
        target = Path(temp) / "config.json"
        payload = _config(cost=100, quantity=10, currency="CNY", show_amounts=True)
        result = save_user_config(payload, str(target))
        stored = load_user_config(str(target))
        normalized = normalize_local_portfolio_config(payload)
        return (
            result.get("status") == "saved"
            and "[stored locally]" in result.get("config", {}).get("assets", {}).get("portfolio_json", "")
            and "average_cost_price" in stored.get("assets", {}).get("portfolio_json", "")
            and normalized.get("status") == "valid"
        )


def _position(value: Mapping[str, Any]) -> dict[str, Any]:
    positions = value.get("positions") if isinstance(value.get("positions"), list) else []
    return positions[0] if positions and isinstance(positions[0], dict) else {}


def _contains_private_keys(value: Any) -> bool:
    if isinstance(value, Mapping):
        return bool(PRIVATE_KEYS & set(value)) or any(_contains_private_keys(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_private_keys(item) for item in value)
    return False


if __name__ == "__main__":
    raise SystemExit(main())
