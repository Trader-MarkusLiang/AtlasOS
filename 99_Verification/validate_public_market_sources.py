"""Validate bounded public evidence sources with a non-private test asset."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.market_evidence_sources import (  # noqa: E402
    fetch_cninfo_announcements,
    fetch_eastmoney_attention_sample,
    fetch_public_market_evidence,
)


def main() -> int:
    positions = [
        {
            "asset": "000001.SZ",
            "market": "A-share",
            "theme": "public-source-validation",
        }
    ]
    result: dict[str, Any] = {"checks": {}}
    try:
        announcements = fetch_cninfo_announcements(positions, limit_per_asset=2, timeout=8)
        attention = fetch_eastmoney_attention_sample(positions, timeout=8)
        combined = fetch_public_market_evidence(positions, timeout=8)
    except Exception as exc:
        result["status"] = "FAIL"
        result["failure"] = f"{type(exc).__name__}: {exc}"
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 1

    _check("cninfo_announcement_available", bool(announcements), result)
    _check(
        "cninfo_official_provenance",
        all(
            item.get("verification_status") == "VERIFIED_OFFICIAL_SOURCE"
            and str(item.get("source_url") or "").startswith("https://static.cninfo.com.cn/")
            for item in announcements
        ),
        result,
    )
    _check("attention_sample_available", attention.get("source") == "eastmoney_stock_rank", result)
    _check(
        "attention_partial_coverage_explicit",
        attention.get("verification_status") == "VERIFIED_SOURCE_PARTIAL_COVERAGE"
        and "proxy only" in str(attention.get("details", {}).get("interpretation_limit") or ""),
        result,
    )
    channels = combined.get("channel_statuses", {})
    _check("news_channel_observed", channels.get("news_announcement") in {"LIVE", "DELAYED", "CACHED"}, result)
    _check("attention_channel_observed", channels.get("narrative_attention") == "DELAYED", result)
    items = combined.get("items", [])
    _check("thesis_remains_unassessed", all(item.get("thesis_changed") == "UNASSESSED" for item in items), result)
    forbidden = {"buy", "sell", "recommended_action", "cde_authority"}
    _check(
        "no_trading_authority",
        not any(key.lower() in forbidden for item in items for key in item),
        result,
    )
    result["evidence"] = {
        "cninfo_item_count": len(announcements),
        "attention_sample_size": attention.get("details", {}).get("sample_size"),
        "channel_statuses": channels,
        "source_errors": combined.get("errors", {}),
    }
    failures = [name for name, passed in result["checks"].items() if not passed]
    result["status"] = "PASS" if not failures else "FAIL"
    result["failures"] = failures
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def _check(name: str, passed: bool, result: dict[str, Any]) -> None:
    result["checks"][name] = bool(passed)


if __name__ == "__main__":
    raise SystemExit(main())
