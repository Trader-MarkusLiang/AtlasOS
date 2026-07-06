"""Infrastructure data-fetch adapter boundary for Atlas Runtime v0.4."""

from __future__ import annotations

import importlib
import os
from typing import Any, Dict, Iterable, List


def fetch_market_data(symbols: Iterable[str], provider: str = "dsa") -> Dict[str, Any]:
    """Fetch market data through an optional infrastructure provider.

    Atlas treats the result as infrastructure data only. Provider output must be
    normalized by the DSA bridge before it can affect cognition.
    """

    symbol_list = [str(symbol) for symbol in symbols]
    if provider != "dsa":
        return {
            "provider": provider,
            "status": "unsupported_provider",
            "symbols": symbol_list,
            "data": {},
        }

    dotted = os.environ.get("ATLAS_DSA_DATAFETCHER")
    if not dotted:
        return {
            "provider": "dsa",
            "status": "not_configured",
            "symbols": symbol_list,
            "data": {},
            "note": "Set ATLAS_DSA_DATAFETCHER to a callable dotted path to enable DSA data fetch.",
        }

    try:
        func = _load_callable(dotted)
        data = func(symbol_list)
    except Exception as exc:  # pragma: no cover - depends on external DSA runtime
        return {
            "provider": "dsa",
            "status": "provider_error",
            "symbols": symbol_list,
            "data": {},
            "error": str(exc),
        }
    return {
        "provider": "dsa",
        "status": "success",
        "symbols": symbol_list,
        "data": data,
    }


def data_source_status() -> Dict[str, Any]:
    return {
        "dsa_data_fetcher_configured": bool(os.environ.get("ATLAS_DSA_DATAFETCHER")),
        "provider": "dsa",
        "role": "infrastructure_only",
    }


def _load_callable(dotted: str):
    module_name, _, attr = dotted.partition(":")
    if not attr:
        module_name, _, attr = dotted.rpartition(".")
    if not module_name or not attr:
        raise ValueError("ATLAS_DSA_DATAFETCHER must be module:function or module.function")
    module = importlib.import_module(module_name)
    func = getattr(module, attr)
    if not callable(func):
        raise TypeError(f"{dotted} is not callable")
    return func

