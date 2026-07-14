"""Private, local-only portfolio valuation for the Home presentation layer.

This module is deliberately outside cognition, Decision Contract, telemetry,
and LLM routing. Exact values may be rendered on localhost when authorized by
local privacy preferences, but must never be persisted outside ignored config.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Mapping


DEFAULT_CONFIG_PATH = Path("runtime/config/user_config.json")
SUPPORTED_CURRENCIES = {"CNY", "HKD", "USD"}
USABLE_QUALITY = {"available", "partial"}
USABLE_FRESHNESS = {"LIVE", "DELAYED", "CACHED", "FRESH", "AVAILABLE"}
PRIVATE_POSITION_FIELDS = {
    "average_cost_price",
    "quantity",
    "total_position_cost",
    "current_market_value",
    "unrealized_pnl_amount",
}
DEFAULT_PRIVACY = {
    "show_cost_price": True,
    "show_pnl_percentage": True,
    "show_quantity": False,
    "show_amounts": False,
}


def validate_local_portfolio_config(config: Mapping[str, Any]) -> dict[str, Any]:
    """Validate optional private fields without returning their raw values."""

    errors: list[dict[str, Any]] = []
    for index, item in enumerate(_raw_positions(config)):
        if not isinstance(item, Mapping):
            errors.append(_error(index, "position", "must_be_object"))
            continue
        cost = item.get("average_cost_price")
        quantity = item.get("quantity")
        currency = str(item.get("position_currency") or "").strip().upper()
        if _provided(cost) and _positive_decimal(cost) is None:
            errors.append(_error(index, "average_cost_price", "must_be_positive_number"))
        if _provided(quantity) and _positive_decimal(quantity) is None:
            errors.append(_error(index, "quantity", "must_be_positive_number"))
        if _provided(cost) and not currency:
            errors.append(_error(index, "position_currency", "required_when_cost_is_set"))
        elif currency and currency not in SUPPORTED_CURRENCIES:
            errors.append(_error(index, "position_currency", "unsupported_currency"))
        timestamp = str(item.get("cost_updated_at") or "").strip()
        if timestamp and not _valid_timestamp(timestamp):
            errors.append(_error(index, "cost_updated_at", "invalid_iso_timestamp"))
    return {"status": "valid" if not errors else "invalid", "errors": errors}


def normalize_local_portfolio_config(
    config: Mapping[str, Any],
    *,
    now: str | None = None,
) -> dict[str, Any]:
    """Return a copy with stable cost metadata after validation."""

    validation = validate_local_portfolio_config(config)
    if validation["errors"]:
        return {"status": "invalid", "errors": validation["errors"], "config": dict(config)}
    data = json.loads(json.dumps(config))
    assets = data.get("assets") if isinstance(data.get("assets"), dict) else {}
    payload = _parse_jsonish(assets.get("portfolio_json"))
    positions = _positions_container(payload)
    stamp = now or datetime.now(timezone.utc).isoformat()
    for item in positions:
        if not isinstance(item, dict):
            continue
        if _provided(item.get("average_cost_price")):
            item["position_currency"] = str(item.get("position_currency") or "").strip().upper()
            item["cost_basis_method"] = str(
                item.get("cost_basis_method") or "user_supplied_adjusted_average_cost"
            )
            item["cost_updated_at"] = str(item.get("cost_updated_at") or stamp)
        else:
            for key in ("average_cost_price", "position_currency", "cost_basis_method", "cost_updated_at"):
                item.pop(key, None)
        if not _provided(item.get("quantity")):
            item.pop("quantity", None)
    assets["portfolio_json"] = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    data["assets"] = assets
    data["portfolio_privacy"] = _privacy(data.get("portfolio_privacy"))
    return {"status": "valid", "errors": [], "config": data}


def build_local_portfolio_valuation(
    *,
    config_path: str | None = None,
    config: Mapping[str, Any] | None = None,
    market_intelligence: Mapping[str, Any] | None = None,
    fx_rates: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build an ephemeral, privacy-filtered Home valuation projection."""

    data = dict(config or _load_config(config_path))
    privacy = _privacy(data.get("portfolio_privacy"))
    raw_positions = [item for item in _raw_positions(data) if isinstance(item, Mapping)]
    observations = _observation_index(market_intelligence or {})
    validation = validate_local_portfolio_config(data)
    validation_by_index = _errors_by_index(validation["errors"])
    position_views: list[dict[str, Any]] = []
    internal_amounts: list[dict[str, Any]] = []

    for index, position in enumerate(raw_positions):
        view, internal = _value_position(
            position,
            observations,
            privacy,
            validation_by_index.get(index, []),
        )
        position_views.append(view)
        internal_amounts.append(internal)

    summary = _portfolio_summary(position_views, internal_amounts, privacy, fx_rates or {})
    return {
        "status": "configured" if position_views else "missing",
        "scope": "localhost_private_home_projection",
        "privacy": privacy,
        "position_count": len(position_views),
        "positions": position_views,
        "summary": summary,
        "validation_status": validation["status"],
        "validation_errors": validation["errors"],
        "not_for_cognition": True,
        "not_for_llm": True,
        "not_for_telemetry": True,
        "no_trading_execution": True,
    }


def redact_private_portfolio_config(config: Mapping[str, Any]) -> dict[str, Any]:
    """Return a response-safe config view with private values replaced by status."""

    data = json.loads(json.dumps(config))
    assets = data.get("assets") if isinstance(data.get("assets"), dict) else {}
    payload = _parse_jsonish(assets.get("portfolio_json"))
    for item in _positions_container(payload):
        if not isinstance(item, dict):
            continue
        for field in PRIVATE_POSITION_FIELDS:
            if _provided(item.get(field)):
                item[field] = "[stored locally]"
        if item.get("cost_updated_at"):
            item["cost_updated_at"] = "[stored locally]"
    assets["portfolio_json"] = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    data["assets"] = assets
    return data


def _value_position(
    position: Mapping[str, Any],
    observations: Mapping[str, Mapping[str, Any]],
    privacy: Mapping[str, bool],
    field_errors: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    asset = str(position.get("asset") or "").strip()
    market = str(position.get("market") or "Unknown").strip()
    configured_pct = _decimal(position.get("portfolio_percentage"))
    cost = _positive_decimal(position.get("average_cost_price"))
    quantity = _positive_decimal(position.get("quantity"))
    cost_currency = str(position.get("position_currency") or "").strip().upper()
    observation = observations.get(_asset_key(asset), {})
    identity_status = _identity_status(asset, observation)
    latest_price = _positive_decimal(observation.get("latest_price"))
    freshness = str(observation.get("freshness") or "NOT_CONFIGURED").upper()
    source_type = str(observation.get("source_type") or "").lower()
    quality = str(observation.get("data_quality_status") or "").lower()
    price_currency = str(observation.get("price_currency") or _market_currency(market, asset) or "").upper()
    provider_status = _provider_status(observation)
    limitations: list[str] = []

    if field_errors:
        limitations.append("INVALID_PRIVATE_INPUT")
    if not cost:
        limitations.append("AVERAGE_COST_NOT_CONFIGURED")
    if not quantity:
        limitations.append("QUANTITY_NOT_CONFIGURED")
    if not observation:
        limitations.append("MARKET_DATA_MISSING")
    elif source_type == "controlled_fixture" or freshness == "SIMULATED":
        limitations.append("SIMULATED_PRICE_BLOCKED")
    elif quality not in USABLE_QUALITY or freshness not in USABLE_FRESHNESS or not latest_price:
        limitations.append("MARKET_DATA_UNAVAILABLE")
    if identity_status != "Validated":
        limitations.append("IDENTITY_MISMATCH")
    if cost and cost_currency and price_currency and cost_currency != price_currency:
        limitations.append("PRICE_COST_CURRENCY_MISMATCH")
    if freshness in {"DELAYED", "CACHED"}:
        limitations.append("PRICE_NOT_LIVE")

    calculation_blocked = any(
        marker in limitations
        for marker in (
            "INVALID_PRIVATE_INPUT",
            "AVERAGE_COST_NOT_CONFIGURED",
            "MARKET_DATA_MISSING",
            "SIMULATED_PRICE_BLOCKED",
            "MARKET_DATA_UNAVAILABLE",
            "IDENTITY_MISMATCH",
            "PRICE_COST_CURRENCY_MISMATCH",
        )
    )
    return_pct: Decimal | None = None
    total_cost: Decimal | None = None
    market_value: Decimal | None = None
    pnl_amount: Decimal | None = None
    if not calculation_blocked and cost and latest_price:
        return_pct = ((latest_price - cost) / cost * Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    if cost and quantity and not field_errors:
        total_cost = (cost * quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if latest_price and quantity and not any(
        marker in limitations
        for marker in (
            "INVALID_PRIVATE_INPUT",
            "MARKET_DATA_MISSING",
            "MARKET_DATA_UNAVAILABLE",
            "SIMULATED_PRICE_BLOCKED",
            "IDENTITY_MISMATCH",
        )
    ):
        market_value = (latest_price * quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if return_pct is not None and cost and latest_price and quantity:
        pnl_amount = ((latest_price - cost) * quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    view: dict[str, Any] = {
        "asset": asset,
        "market": market,
        "configured_allocation_pct": _number(configured_pct),
        "position_currency": cost_currency or price_currency or None,
        "price_currency": price_currency or None,
        "latest_price": _number(latest_price),
        "daily_change_pct": _number(_decimal(observation.get("daily_change_pct"))),
        "source": observation.get("source") or None,
        "observed_at": observation.get("timestamp") or None,
        "freshness": freshness,
        "provider_status": provider_status,
        "identity_status": identity_status,
        "cost_status": "CONFIGURED" if cost else "NOT_CONFIGURED",
        "cost_updated_at": position.get("cost_updated_at") if cost else None,
        "valuation_status": "AVAILABLE" if return_pct is not None else "LIMITED",
        "limitations": list(dict.fromkeys(limitations)),
        "posture_source": "existing_atlas_evidence_not_cost_basis",
    }
    if privacy["show_cost_price"]:
        view["average_cost_price"] = _number(cost)
    if privacy["show_pnl_percentage"]:
        view["unrealized_return_pct"] = _number(return_pct)
    if privacy["show_quantity"]:
        view["quantity"] = _number(quantity)
    if privacy["show_amounts"]:
        view["total_position_cost"] = _number(total_cost)
        view["current_market_value"] = _number(market_value)
        view["unrealized_pnl_amount"] = _number(pnl_amount)
    internal = {
        "currency": cost_currency or price_currency,
        "quantity": quantity,
        "total_cost": total_cost,
        "market_value": market_value,
        "pnl_amount": pnl_amount,
    }
    return view, internal


def _portfolio_summary(
    positions: list[Mapping[str, Any]],
    amounts: list[Mapping[str, Any]],
    privacy: Mapping[str, bool],
    fx_rates: Mapping[str, Any],
) -> dict[str, Any]:
    return_count = sum(1 for item in positions if item.get("valuation_status") == "AVAILABLE")
    amount_count = sum(1 for item in amounts if item.get("pnl_amount") is not None)
    currencies = {str(item.get("currency")) for item in amounts if item.get("currency")}
    limitations: list[str] = []
    if return_count != len(positions):
        limitations.append("INCOMPLETE_POSITION_RETURNS")
    if amount_count != len(positions):
        limitations.append("INCOMPLETE_AMOUNT_INPUTS")
    if len(currencies) > 1 and not fx_rates:
        limitations.append("FX_DATA_MISSING_AGGREGATE_VALUATION_LIMITED")
    limitations.append("CURRENT_WEIGHT_UNAVAILABLE_CASH_VALUE_NOT_CONFIGURED")

    result: dict[str, Any] = {
        "return_complete_positions": return_count,
        "amount_complete_positions": amount_count,
        "total_positions": len(positions),
        "currencies": sorted(currencies),
        "aggregate_status": "AVAILABLE_BY_NATIVE_CURRENCY" if amount_count else "NOT_CONFIGURED",
        "estimated_current_weight_status": "UNAVAILABLE",
        "limitations": limitations,
    }
    if privacy["show_amounts"] and amount_count:
        by_currency: dict[str, dict[str, Decimal]] = {}
        for item in amounts:
            currency = str(item.get("currency") or "")
            if not currency or item.get("pnl_amount") is None:
                continue
            bucket = by_currency.setdefault(
                currency,
                {"total_cost": Decimal("0"), "market_value": Decimal("0"), "pnl_amount": Decimal("0")},
            )
            for target, source in (
                ("total_cost", "total_cost"),
                ("market_value", "market_value"),
                ("pnl_amount", "pnl_amount"),
            ):
                value = item.get(source)
                if isinstance(value, Decimal):
                    bucket[target] += value
        result["native_currency_totals"] = {
            currency: {key: _number(value) for key, value in values.items()}
            for currency, values in by_currency.items()
        }
    return result


def _observation_index(market: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    observations = market.get("observations") if isinstance(market.get("observations"), list) else []
    output: dict[str, Mapping[str, Any]] = {}
    for item in observations:
        if not isinstance(item, Mapping):
            continue
        asset = str(item.get("asset") or item.get("ticker") or "").strip()
        if asset:
            output[_asset_key(asset)] = item
    return output


def _identity_status(asset: str, observation: Mapping[str, Any]) -> str:
    if not observation:
        return "Data Missing"
    observed_asset = str(observation.get("asset") or "").strip()
    raw = observation.get("raw_reference") if isinstance(observation.get("raw_reference"), Mapping) else {}
    ticker = str(raw.get("ticker") or observed_asset).strip()
    return "Validated" if _asset_key(asset) == _asset_key(observed_asset) == _asset_key(ticker) else "Mismatch"


def _provider_status(observation: Mapping[str, Any]) -> str:
    if not observation:
        return "NOT_CONFIGURED"
    if str(observation.get("source_type") or "").lower() == "controlled_fixture":
        return "SIMULATED"
    quality = str(observation.get("data_quality_status") or "").lower()
    if quality not in USABLE_QUALITY or observation.get("latest_price") is None:
        return "FAILED"
    freshness = str(observation.get("freshness") or "CACHED").upper()
    return freshness if freshness in {"LIVE", "DELAYED", "CACHED"} else "CACHED"


def _market_currency(market: str, asset: str) -> str | None:
    market_key = market.strip().lower()
    ticker = asset.strip().upper()
    if ticker.endswith(".HK") or market_key in {"hk", "hong kong", "hong_kong"}:
        return "HKD"
    if ticker.endswith((".SH", ".SS", ".SZ")) or market_key in {"a-share", "ashare", "cn", "china"}:
        return "CNY"
    if market_key in {"us", "nasdaq", "nyse"}:
        return "USD"
    return None


def _raw_positions(config: Mapping[str, Any]) -> list[Any]:
    assets = config.get("assets") if isinstance(config.get("assets"), Mapping) else {}
    payload = _parse_jsonish(assets.get("portfolio_json"))
    return _positions_container(payload)


def _positions_container(payload: Any) -> list[Any]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, Mapping):
        for key in ("positions", "assets", "holdings"):
            if isinstance(payload.get(key), list):
                return payload[key]
    return []


def _parse_jsonish(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return json.loads(json.dumps(value))
    try:
        return json.loads(str(value or "{}"))
    except (json.JSONDecodeError, TypeError):
        return {}


def _privacy(value: Any) -> dict[str, bool]:
    source = value if isinstance(value, Mapping) else {}
    return {key: bool(source.get(key, default)) for key, default in DEFAULT_PRIVACY.items()}


def _load_config(path: str | None) -> dict[str, Any]:
    configured = path or os.environ.get("ATLAS_USER_CONFIG")
    target = Path(configured) if configured else DEFAULT_CONFIG_PATH
    if not target.exists():
        return {}
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _positive_decimal(value: Any) -> Decimal | None:
    parsed = _decimal(value)
    return parsed if parsed is not None and parsed > 0 else None


def _decimal(value: Any) -> Decimal | None:
    if not _provided(value):
        return None
    try:
        parsed = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None
    return parsed if parsed.is_finite() else None


def _number(value: Decimal | None) -> int | float | None:
    if value is None:
        return None
    if value == value.to_integral_value():
        return int(value)
    return float(value)


def _provided(value: Any) -> bool:
    return value is not None and str(value).strip() != ""


def _valid_timestamp(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def _asset_key(value: str) -> str:
    return value.strip().upper()


def _error(index: int, field: str, code: str) -> dict[str, Any]:
    return {"position_index": index, "field": field, "code": code}


def _errors_by_index(errors: list[Mapping[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    output: dict[int, list[dict[str, Any]]] = {}
    for error in errors:
        index = int(error.get("position_index", -1))
        output.setdefault(index, []).append(dict(error))
    return output
