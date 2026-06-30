"""Data anomaly checks for Atlas market snapshots.

This utility flags extreme or suspicious market data before it is used for rebalance execution
planning. It is not an Engine, trade signal, or execution authority.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def check_data_anomaly(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Return anomaly status for a market snapshot."""

    flags: List[str] = []
    severe_flags: List[str] = []
    warning_flags: List[str] = []

    latest_price = _num(snapshot.get("latest_price"))
    change_20d = _num(snapshot.get("change_20d_pct"))
    change_60d = _num(snapshot.get("change_60d_pct"))
    gap_ma20 = _num(snapshot.get("price_vs_ma20_pct"))
    gap_ma60 = _num(snapshot.get("price_vs_ma60_pct"))
    volume_ratio = _num(snapshot.get("volume_ratio_20d"))
    freshness = snapshot.get("data_freshness")
    ma60 = _num(snapshot.get("ma60"))
    timestamp = snapshot.get("timestamp")

    if latest_price is None or latest_price <= 0:
        severe_flags.append("latest_price_missing_or_non_positive")
    if ma60 is None:
        severe_flags.append("history_too_short_for_ma60")
    if freshness == "Stale":
        severe_flags.append("timestamp_stale")

    _threshold(change_20d, "abs_20d_change_pct", warning=80, severe=120, warning_flags=warning_flags, severe_flags=severe_flags, absolute=True)
    _threshold(change_60d, "abs_60d_change_pct", warning=150, severe=250, warning_flags=warning_flags, severe_flags=severe_flags, absolute=True)
    _threshold(gap_ma20, "price_vs_ma20_pct", warning=40, severe=70, warning_flags=warning_flags, severe_flags=severe_flags)
    _threshold(gap_ma60, "price_vs_ma60_pct", warning=80, severe=120, warning_flags=warning_flags, severe_flags=severe_flags)
    _threshold(volume_ratio, "volume_ratio_20d", warning=3, severe=None, warning_flags=warning_flags, severe_flags=severe_flags)

    if freshness == "Unknown" or not timestamp:
        warning_flags.append("timestamp_freshness_unknown")

    if severe_flags:
        status = "Severe"
        decision_impact = "Execution Blocked"
        flags = severe_flags + warning_flags
    elif warning_flags:
        status = "Warning"
        decision_impact = "CDE Precision Limited"
        flags = warning_flags
    elif snapshot.get("data_status") not in {"Available", "Partial"}:
        status = "Unknown"
        decision_impact = "Use Conservative Framework Only"
        flags = ["data_status_unavailable_or_unknown"]
    else:
        status = "Normal"
        decision_impact = "None"

    return {
        "ticker": snapshot.get("ticker"),
        "name": snapshot.get("name"),
        "anomaly_status": status,
        "anomaly_flags": flags,
        "anomaly_reason": _reason(status, flags),
        "decision_impact": decision_impact,
    }


def aggregate_anomaly_status(checks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate multiple anomaly checks for a rebalance plan."""

    if not checks:
        return {
            "anomaly_status": "Unknown",
            "anomaly_flags": ["no_checks"],
            "decision_impact": "Use Conservative Framework Only",
        }
    statuses = [check.get("anomaly_status") for check in checks]
    flags: List[str] = []
    for check in checks:
        for flag in check.get("anomaly_flags") or []:
            label = f"{check.get('name') or check.get('ticker')}: {flag}"
            flags.append(label)
    if "Severe" in statuses:
        return {
            "anomaly_status": "Severe",
            "anomaly_flags": flags,
            "decision_impact": "Execution Blocked",
        }
    if "Warning" in statuses:
        return {
            "anomaly_status": "Warning",
            "anomaly_flags": flags,
            "decision_impact": "CDE Precision Limited",
        }
    if "Unknown" in statuses:
        return {
            "anomaly_status": "Unknown",
            "anomaly_flags": flags,
            "decision_impact": "Use Conservative Framework Only",
        }
    return {
        "anomaly_status": "Normal",
        "anomaly_flags": [],
        "decision_impact": "None",
    }


def migration_band_from_anomaly(aggregate: Dict[str, Any], cde_precision_limited: bool = False) -> str:
    """Return maximum migration band implied by anomaly status.

    This is not CDE authority and not mandatory action.
    """

    status = aggregate.get("anomaly_status")
    impact = aggregate.get("decision_impact")
    if status == "Severe" or impact == "Execution Blocked":
        return "0-5%"
    if status == "Warning" or cde_precision_limited:
        return "5-10%"
    if status == "Unknown":
        return "0-5%"
    return "10-20%"


def _num(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def _threshold(
    value: Optional[float],
    label: str,
    warning: float,
    severe: Optional[float],
    warning_flags: List[str],
    severe_flags: List[str],
    absolute: bool = False,
) -> None:
    if value is None:
        return
    tested = abs(value) if absolute else value
    if severe is not None and tested > severe:
        severe_flags.append(label)
    elif tested > warning:
        warning_flags.append(label)


def _reason(status: str, flags: List[str]) -> str:
    if status == "Normal":
        return "No anomaly threshold triggered."
    if status == "Warning":
        return "Extreme movement or uncertain freshness detected; use data with CDE Precision Limited."
    if status == "Severe":
        return "Severe data anomaly or extreme move detected; execution sizing must be blocked."
    return "Anomaly status cannot be determined; use conservative framework only."
