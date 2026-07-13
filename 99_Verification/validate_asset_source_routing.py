"""Validate market-derived fixed source plans without private portfolio data."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.market_source_registry import build_asset_source_map  # noqa: E402


def main() -> int:
    positions = [
        {"asset": "600000.SH", "market": "A-share"},
        {"asset": "000001.SZ", "market": "A-share"},
        {"asset": "00700.HK", "market": "HK"},
        {"asset": "AAPL", "market": "US"},
    ]
    observations = [
        {"asset": "600000.SH", "source": "eastmoney_kline", "timestamp": "2026-07-13", "freshness": "DELAYED", "raw_reference": {"errors": []}},
        {"asset": "000001.SZ", "source": "tencent_kline", "timestamp": "2026-07-13", "freshness": "DELAYED", "raw_reference": {"errors": []}},
        {"asset": "00700.HK", "source": "tencent_kline", "timestamp": "2026-07-13", "freshness": "DELAYED", "raw_reference": {"errors": []}},
        {"asset": "AAPL", "source": "yahoo_chart", "timestamp": "2026-07-10", "freshness": "CACHED", "raw_reference": {"errors": []}},
    ]
    evidence = [
        {"source": "sse_official", "affected_assets": ["600000.SH"], "timestamp": "2026-07-12", "freshness": "DELAYED"},
        {"source": "cninfo_official_disclosure", "affected_assets": ["000001.SZ"], "timestamp": "2026-07-12", "freshness": "DELAYED"},
        {"source": "eastmoney_stock_rank", "affected_assets": ["000001.SZ"], "timestamp": "2026-07-13", "freshness": "DELAYED"},
    ]
    rows = build_asset_source_map(positions, observations, evidence, {})
    by_asset = {row["asset"]: row for row in rows}
    result: dict[str, Any] = {"checks": {}}
    _check("all_assets_mapped", set(by_asset) == {item["asset"] for item in positions}, result)
    _check("sh_official_source", _status(by_asset["600000.SH"], "sse_official") == "USED", result)
    _check("sz_official_source", _status(by_asset["000001.SZ"], "cninfo_official_disclosure") == "USED", result)
    _check("a_share_attention_source", _status(by_asset["000001.SZ"], "eastmoney_stock_rank") == "USED", result)
    _check("hk_price_source", _status(by_asset["00700.HK"], "tencent_kline") == "USED", result)
    _check("hkex_manual_explicit", _status(by_asset["00700.HK"], "hkex_issuer_search") == "MANUAL_REVIEW", result)
    _check("us_price_source", _status(by_asset["AAPL"], "yahoo_chart") == "USED", result)
    _check("sec_manual_explicit", _status(by_asset["AAPL"], "sec_edgar") == "MANUAL_REVIEW", result)
    _check("fallbacks_standby", _status(by_asset["600000.SH"], "tencent_kline") == "STANDBY", result)
    result["source_counts"] = {
        asset: len(row["sources"])
        for asset, row in by_asset.items()
    }
    failures = [name for name, passed in result["checks"].items() if not passed]
    result["status"] = "PASS" if not failures else "FAIL"
    result["failures"] = failures
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def _status(row: dict[str, Any], source_id: str) -> str:
    source = next(item for item in row["sources"] if item["source_id"] == source_id)
    return str(source["status"])


def _check(name: str, passed: bool, result: dict[str, Any]) -> None:
    result["checks"][name] = bool(passed)


if __name__ == "__main__":
    raise SystemExit(main())
