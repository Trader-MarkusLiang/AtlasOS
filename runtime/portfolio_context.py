"""Read-only portfolio context layer for Atlas Runtime productization.

This module turns UI asset configuration into privacy-preserving exposure
metadata. It never stores account value, cost basis, balances, broker data, or
trade instructions.
"""

from __future__ import annotations

import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping


DEFAULT_CONFIG_PATH = Path("runtime/config/user_config.json")


def build_portfolio_context(config_path: str | None = None, config: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Return a read-only exposure map from local UI config."""

    data = dict(config or _load_config(config_path))
    assets = data.get("assets") if isinstance(data.get("assets"), Mapping) else {}
    positions = _positions_from_assets(assets)
    total = round(sum(float(item.get("portfolio_percentage", 0.0) or 0.0) for item in positions), 4)
    status = "configured" if positions else "missing"
    consistency = "PASS"
    warnings: list[str] = []
    if total > 100.5:
        consistency = "FAIL"
        warnings.append("portfolio_percentage_sum_exceeds_100")
    if any(float(item.get("portfolio_percentage", 0.0) or 0.0) < 0 for item in positions):
        consistency = "FAIL"
        warnings.append("negative_portfolio_percentage")
    return {
        "status": status,
        "source": str(Path(config_path) if config_path else DEFAULT_CONFIG_PATH),
        "privacy": "percentage_only_no_account_amounts",
        "portfolio_consistency": consistency,
        "exposure_sum_pct": total,
        "cash_or_unassigned_pct": round(max(0.0, 100.0 - total), 4) if positions else None,
        "positions": positions,
        "exposure_map": _exposure_map(positions),
        "warnings": warnings,
        "read_only": True,
        "no_trading_execution": True,
    }


def _positions_from_assets(assets: Mapping[str, Any]) -> list[dict[str, Any]]:
    portfolio_json = _parse_jsonish(assets.get("portfolio_json"))
    weights = assets.get("weights") if isinstance(assets.get("weights"), Mapping) else {}
    asset_list = assets.get("asset_list") if isinstance(assets.get("asset_list"), list) else []
    candidates: list[Any] = []
    if isinstance(portfolio_json, list):
        candidates.extend(portfolio_json)
    elif isinstance(portfolio_json, Mapping):
        raw_positions = portfolio_json.get("positions") or portfolio_json.get("assets") or portfolio_json.get("holdings")
        if isinstance(raw_positions, list):
            candidates.extend(raw_positions)
        elif portfolio_json:
            candidates.append(portfolio_json)
    for item in asset_list:
        candidates.append({"asset": item})

    by_asset: dict[str, dict[str, Any]] = {}
    for item in candidates:
        if isinstance(item, Mapping):
            asset = str(item.get("asset") or item.get("symbol") or item.get("ticker") or item.get("name") or "").strip()
            if not asset:
                continue
            weight = item.get("portfolio_percentage", item.get("weight", weights.get(asset, 0.0)))
            record = {
                "asset": asset[:80],
                "market": str(item.get("market") or _guess_market(asset))[:40],
                "portfolio_percentage": _percent(weight),
                "theme": str(item.get("theme") or "Unspecified")[:80],
                "role": str(item.get("role") or "Unspecified")[:80],
                "user_thesis": str(item.get("thesis") or item.get("user_thesis") or "")[:500],
                "risk_note": str(item.get("risk_note") or "")[:500],
            }
        else:
            asset = str(item or "").strip()
            if not asset:
                continue
            record = {
                "asset": asset[:80],
                "market": _guess_market(asset),
                "portfolio_percentage": _percent(weights.get(asset, 0.0)),
                "theme": "Unspecified",
                "role": "Unspecified",
                "user_thesis": "",
                "risk_note": "",
            }
        existing = by_asset.get(record["asset"])
        if existing:
            if not float(existing.get("portfolio_percentage", 0.0) or 0.0) and record["portfolio_percentage"]:
                existing["portfolio_percentage"] = record["portfolio_percentage"]
            for key, default in (
                ("market", "US"),
                ("theme", "Unspecified"),
                ("role", "Unspecified"),
                ("user_thesis", ""),
                ("risk_note", ""),
            ):
                if existing.get(key) == default and record.get(key) != default:
                    existing[key] = record[key]
            continue
        by_asset[record["asset"]] = record
    return list(by_asset.values())


def _exposure_map(positions: list[Mapping[str, Any]]) -> dict[str, Any]:
    theme = defaultdict(float)
    market = defaultdict(float)
    role = defaultdict(float)
    for item in positions:
        weight = float(item.get("portfolio_percentage", 0.0) or 0.0)
        theme[str(item.get("theme") or "Unspecified")] += weight
        market[str(item.get("market") or "Unknown")] += weight
        role[str(item.get("role") or "Unspecified")] += weight
    largest = sorted(positions, key=lambda item: float(item.get("portfolio_percentage", 0.0) or 0.0), reverse=True)[:5]
    clusters = [
        {"cluster": key, "exposure_pct": round(value, 4), "risk": _cluster_risk(value)}
        for key, value in sorted(theme.items(), key=lambda pair: pair[1], reverse=True)
        if value > 0
    ]
    return {
        "asset_concentration": [
            {"asset": item.get("asset"), "exposure_pct": item.get("portfolio_percentage")}
            for item in largest
        ],
        "theme_concentration": _rounded_map(theme),
        "market_concentration": _rounded_map(market),
        "role_concentration": _rounded_map(role),
        "liquidity_sensitivity": _liquidity_sensitivity(market),
        "regime_sensitivity": _regime_sensitivity(theme),
        "portfolio_relevance_score": _portfolio_relevance_score(positions, theme, market),
        "correlated_risk_clusters": clusters,
    }


def _parse_jsonish(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(str(value or "{}"))
    except json.JSONDecodeError:
        return {}


def _percent(value: Any) -> float:
    text = str(value if value is not None else "0").strip().replace("%", "")
    try:
        number = float(text)
    except ValueError:
        return 0.0
    if 0 < number <= 1:
        number *= 100
    return round(number, 4)


def _guess_market(asset: str) -> str:
    clean = asset.strip().upper()
    if clean.endswith(".HK") or (clean.isdigit() and len(clean) == 5):
        return "HK"
    if clean.endswith((".SS", ".SZ")) or (clean.isdigit() and len(clean) == 6):
        return "A-share"
    if clean:
        return "US"
    return "Unknown"


def _rounded_map(values: Mapping[str, float]) -> dict[str, float]:
    return {key: round(value, 4) for key, value in sorted(values.items(), key=lambda pair: pair[1], reverse=True)}


def _cluster_risk(value: float) -> str:
    if value >= 45:
        return "high_concentration"
    if value >= 25:
        return "moderate_concentration"
    return "low"


def _liquidity_sensitivity(market: Mapping[str, float]) -> str:
    if market.get("A-share", 0.0) + market.get("HK", 0.0) >= 60:
        return "regional_liquidity_sensitive"
    if market.get("Unspecified", 0.0) >= 30:
        return "unknown_liquidity_profile"
    return "diversified_or_unknown"


def _regime_sensitivity(theme: Mapping[str, float]) -> str:
    top = max(theme.values(), default=0.0)
    if top >= 45:
        return "single_theme_regime_sensitive"
    if top >= 25:
        return "theme_cluster_sensitive"
    return "broad_or_unclassified"


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


def _portfolio_relevance_score(
    positions: list[Mapping[str, Any]],
    theme: Mapping[str, float],
    market: Mapping[str, float],
) -> float:
    if not positions:
        return 0.0
    exposure = min(100.0, sum(float(item.get("portfolio_percentage", 0.0) or 0.0) for item in positions))
    top_theme = max(theme.values(), default=0.0)
    top_market = max(market.values(), default=0.0)
    score = exposure * 0.55 + top_theme * 0.3 + top_market * 0.15
    return round(max(0.0, min(100.0, score)), 4)
