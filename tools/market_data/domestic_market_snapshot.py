"""Domestic market snapshot utility for Atlas OS.

This module creates structured China / Hong Kong market-data inputs. It is not an Engine, trading
signal, crawler, cache, or execution layer.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

from .market_data_provider import _safe_float, get_history


def get_domestic_market_snapshot(
    ticker: str,
    market: str,
    name: str = "",
    exchange: str = "",
) -> Dict[str, Any]:
    """Return structured domestic market data for China / Hong Kong tickers."""

    result: Dict[str, Any] = {
        "ticker": ticker,
        "name": name,
        "market": market,
        "exchange": exchange,
        "source": None,
        "timestamp": None,
        "latest_price": None,
        "daily_change_pct": None,
        "volume": None,
        "turnover": None,
        "change_5d_pct": None,
        "change_10d_pct": None,
        "change_20d_pct": None,
        "change_60d_pct": None,
        "ma5": None,
        "ma10": None,
        "ma20": None,
        "ma60": None,
        "price_vs_ma20_pct": None,
        "price_vs_ma60_pct": None,
        "high_20d": None,
        "low_20d": None,
        "high_60d": None,
        "low_60d": None,
        "distance_from_20d_high_pct": None,
        "distance_from_60d_high_pct": None,
        "distance_from_20d_low_pct": None,
        "distance_from_60d_low_pct": None,
        "latest_volume": None,
        "avg_volume_5d": None,
        "avg_volume_20d": None,
        "volume_ratio_5d": None,
        "volume_ratio_20d": None,
        "latest_turnover": None,
        "avg_turnover_5d": None,
        "avg_turnover_20d": None,
        "turnover_ratio_5d": None,
        "turnover_ratio_20d": None,
        "market_structure_status": "Data Insufficient",
        "market_structure_reason": "Missing price or history data.",
        "execution_readiness": "Data Insufficient",
        "execution_readiness_reason": "Execution readiness is an input only; CDE authorization is still required.",
        "data_status": "Unavailable",
        "data_freshness": "Unknown",
        "missing_fields": [],
        "errors": [],
    }

    if market not in {"A-share", "HK"}:
        result["errors"].append(f"Unsupported domestic market: {market}")
        result["missing_fields"] = _missing_fields(result)
        return result

    if not ticker:
        result["errors"].append("Ticker missing")
        result["missing_fields"] = _missing_fields(result)
        return result

    history = get_history(ticker, market, "60d")
    result["source"] = history.attrs.get("source")
    result["errors"] = history.attrs.get("errors", [])

    if history.empty:
        result["missing_fields"] = _missing_fields(result)
        return result

    history = history.sort_values("date") if "date" in history.columns else history
    latest = history.iloc[-1]
    latest_price = _safe_float(latest.get("close"))
    result["timestamp"] = _timestamp_to_iso(latest.get("date"))
    result["latest_price"] = latest_price
    result["daily_change_pct"] = _safe_float(latest.get("daily_change_pct")) or _pct_change(history, 1)
    result["volume"] = _safe_float(latest.get("volume"))
    result["latest_volume"] = result["volume"]
    result["turnover"] = _safe_float(latest.get("turnover"))
    result["latest_turnover"] = result["turnover"]

    for days in [5, 10, 20, 60]:
        result[f"change_{days}d_pct"] = _pct_change(history, days)
        result[f"ma{days}"] = _moving_average(history, days)

    result["price_vs_ma20_pct"] = _distance_pct(latest_price, result["ma20"])
    result["price_vs_ma60_pct"] = _distance_pct(latest_price, result["ma60"])

    for days in [20, 60]:
        result[f"high_{days}d"] = _rolling_extreme(history, days, "high", "max")
        result[f"low_{days}d"] = _rolling_extreme(history, days, "low", "min")
        result[f"distance_from_{days}d_high_pct"] = _distance_pct(latest_price, result[f"high_{days}d"])
        result[f"distance_from_{days}d_low_pct"] = _distance_pct(latest_price, result[f"low_{days}d"])

    result["avg_volume_5d"] = _moving_average(history, 5, "volume")
    result["avg_volume_20d"] = _moving_average(history, 20, "volume")
    result["volume_ratio_5d"] = _ratio(result["latest_volume"], result["avg_volume_5d"])
    result["volume_ratio_20d"] = _ratio(result["latest_volume"], result["avg_volume_20d"])

    result["avg_turnover_5d"] = _moving_average(history, 5, "turnover")
    result["avg_turnover_20d"] = _moving_average(history, 20, "turnover")
    result["turnover_ratio_5d"] = _ratio(result["latest_turnover"], result["avg_turnover_5d"])
    result["turnover_ratio_20d"] = _ratio(result["latest_turnover"], result["avg_turnover_20d"])

    result["data_freshness"] = _data_freshness(result["timestamp"])
    result["data_status"] = _data_status(result)
    result["market_structure_status"], result["market_structure_reason"] = classify_market_structure(result)
    result["execution_readiness"], result["execution_readiness_reason"] = classify_execution_readiness(result)
    result["missing_fields"] = _missing_fields(result)
    return result


def classify_market_structure(snapshot: Dict[str, Any]) -> tuple[str, str]:
    price = snapshot.get("latest_price")
    ma20 = snapshot.get("ma20")
    ma60 = snapshot.get("ma60")
    ch20 = snapshot.get("change_20d_pct")
    ch60 = snapshot.get("change_60d_pct")
    gap20 = snapshot.get("price_vs_ma20_pct")
    gap60_high = snapshot.get("distance_from_60d_high_pct")
    volume_ratio = snapshot.get("volume_ratio_20d")

    if any(value is None for value in [price, ma20, ma60, ch20, ch60]):
        return "Data Insufficient", "Missing price, moving-average, or trend data."

    if gap20 is not None and gap20 > 25 and ch20 is not None and ch20 > 20:
        return "Overextended", "Price is far above MA20 after a sharp 20D move."

    if price > ma20 and price > ma60 and ch20 > 0 and ch60 > 0:
        if gap20 is not None and gap20 <= 20:
            return "Strong Uptrend", "Price is above MA20 / MA60 with positive 20D and 60D trends."
        if volume_ratio is not None and volume_ratio >= 1.2:
            return "Strong Uptrend", "Price is extended but supported by elevated volume."
        return "Overextended", "Price is above trend but extended without clear volume confirmation."

    if price > ma60 and (price >= ma20 * 0.97 or ch20 > 0 or ch60 > 0):
        return "Mild Uptrend", "Price remains above MA60 with at least partial trend support."

    if price < ma20 and price < ma60 and ch20 < 0 and ch60 < 0:
        return "Breakdown Risk", "Price is below MA20 / MA60 with weak 20D and 60D trends."

    if price <= ma20 and price >= ma60 * 0.95 and ch60 >= 0:
        return "Pullback", "Longer trend is intact while price is near or below MA20."

    if gap60_high is not None and gap60_high > -3 and ch20 > 10:
        return "Overextended", "Price is close to the 60D high after a strong recent move."

    return "Range / Consolidation", "Price is near key moving averages without decisive trend evidence."


def classify_execution_readiness(snapshot: Dict[str, Any]) -> tuple[str, str]:
    structure = snapshot.get("market_structure_status")
    freshness = snapshot.get("data_freshness")
    status = snapshot.get("data_status")
    gap20 = snapshot.get("price_vs_ma20_pct")

    prefix = "Input only; not Trading Authority. CDE authorization is still required. "

    if status not in {"Available", "Partial"} or freshness == "Stale":
        return "Data Insufficient", prefix + "Data is unavailable, partial, or stale."
    if structure == "Overextended":
        return "Wait for Pullback", prefix + "Structure is extended versus moving averages."
    if structure == "Strong Uptrend":
        return "Wait for Pullback" if gap20 is not None and gap20 > 12 else "Wait for Breakout Confirmation", prefix + "Trend is strong; wait for cleaner confirmation or pullback."
    if structure == "Mild Uptrend":
        return "Watch", prefix + "Trend support exists but execution timing is not decisive."
    if structure == "Pullback":
        return "Pilot Deployment Candidate", prefix + "Pullback may be execution-relevant only after CDE review."
    if structure == "Breakdown Risk":
        return "Reduce Risk Candidate", prefix + "Weak structure may affect execution risk after CDE review."
    if structure == "Range / Consolidation":
        return "Wait for Breakout Confirmation", prefix + "Range structure needs confirmation."
    return "Data Insufficient", prefix + "Market structure cannot be classified."


def _pct_change(df: pd.DataFrame, periods: int) -> Optional[float]:
    if df.empty or "close" not in df.columns or len(df) <= periods:
        return None
    latest = _safe_float(df["close"].iloc[-1])
    previous = _safe_float(df["close"].iloc[-(periods + 1)])
    if latest is None or previous in (None, 0):
        return None
    return (latest / previous - 1.0) * 100.0


def _moving_average(df: pd.DataFrame, window: int, column: str = "close") -> Optional[float]:
    if df.empty or column not in df.columns or len(df) < window:
        return None
    return _safe_float(df[column].tail(window).mean())


def _rolling_extreme(df: pd.DataFrame, window: int, column: str, method: str) -> Optional[float]:
    if df.empty or len(df) < window:
        return None
    source_col = column if column in df.columns else "close"
    values = pd.to_numeric(df[source_col].tail(window), errors="coerce")
    if values.dropna().empty:
        return None
    return _safe_float(values.max() if method == "max" else values.min())


def _distance_pct(value: Optional[float], reference: Optional[float]) -> Optional[float]:
    if value is None or reference in (None, 0):
        return None
    return (value / reference - 1.0) * 100.0


def _ratio(value: Optional[float], reference: Optional[float]) -> Optional[float]:
    if value is None or reference in (None, 0):
        return None
    return value / reference


def _timestamp_to_iso(value: Any) -> Optional[str]:
    if value is None or pd.isna(value):
        return None
    try:
        return pd.Timestamp(value).isoformat()
    except Exception:
        return str(value)


def _data_freshness(timestamp: Optional[str]) -> str:
    if not timestamp:
        return "Unknown"
    try:
        ts_date = pd.Timestamp(timestamp).date()
    except Exception:
        return "Unknown"
    today = datetime.now().date()
    age_days = (today - ts_date).days
    if age_days <= 0:
        return "Fresh"
    if age_days <= 3:
        return "Delayed"
    if age_days <= 10:
        return "Stale"
    return "Unknown"


def _data_status(result: Dict[str, Any]) -> str:
    core = ["source", "timestamp", "latest_price", "volume", "ma20", "ma60"]
    if all(result.get(field) is not None for field in core):
        return "Available"
    if result.get("latest_price") is not None and result.get("ma20") is not None:
        return "Partial"
    if result.get("latest_price") is not None:
        return "Partial"
    return "Unavailable"


def _missing_fields(result: Dict[str, Any]) -> List[str]:
    required = [
        "source",
        "timestamp",
        "latest_price",
        "daily_change_pct",
        "volume",
        "change_5d_pct",
        "change_10d_pct",
        "change_20d_pct",
        "change_60d_pct",
        "ma5",
        "ma10",
        "ma20",
        "ma60",
        "price_vs_ma20_pct",
        "price_vs_ma60_pct",
        "market_structure_status",
        "execution_readiness",
        "data_freshness",
    ]
    optional = [
        "turnover",
        "avg_turnover_5d",
        "avg_turnover_20d",
        "turnover_ratio_5d",
        "turnover_ratio_20d",
    ]
    missing = [field for field in required if result.get(field) is None]
    missing.extend([f"{field} (optional)" for field in optional if result.get(field) is None])
    return missing
