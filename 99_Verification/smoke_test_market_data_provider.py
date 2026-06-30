#!/usr/bin/env python3
"""Run a smoke test for Atlas ticker registry and market data provider.

This script validates ticker mappings and provider snapshots. It does not modify portfolio
allocation, strategy logic, CDE, Decision Brief logic, or execution state.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.market_data import get_market_snapshot  # noqa: E402


REGISTRY_PATH = REPO_ROOT / "tools" / "market_data" / "ticker_registry.yaml"
RESULT_PATH = REPO_ROOT / "99_Verification" / "Market_Data_Provider_Smoke_Test_Result.md"

CURRENT_HOLDINGS = ["雅克科技", "建滔集团", "东山精密", "泰金新能", "DRAM ETF"]
A_SHARE_CANDIDATES = ["赛腾股份", "澜起科技", "雅克科技", "江丰电子"]
HK_CANDIDATES = ["中芯国际", "长飞光纤光缆"]
US_ETF = ["DRAM ETF"]


def load_registry() -> Dict[str, Dict[str, Any]]:
    with REGISTRY_PATH.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    entries = {}
    for entry in data.get("tickers", []):
        names = [entry.get("name", "")]
        names.extend(entry.get("aliases") or [])
        for name in names:
            if name:
                entries[name] = entry
    return entries


def provider_symbol(entry: Dict[str, Any]) -> Optional[str]:
    symbols = entry.get("provider_symbols") or {}
    market = entry.get("market")
    if entry.get("identity_status") == "Needs Manual Mapping":
        return None
    if market == "A-share":
        return symbols.get("akshare") or symbols.get("yfinance")
    if market == "HK":
        return symbols.get("akshare") or symbols.get("yfinance")
    if market in {"US", "US / ETF", "ETF"}:
        return symbols.get("yfinance")
    return symbols.get("akshare") or symbols.get("yfinance")


def smoke_row(name: str, registry: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    entry = registry.get(name)
    if not entry:
        return {
            "name": name,
            "code": "Data Missing",
            "market": "Unknown",
            "provider_symbol": "Needs Manual Mapping",
            "identity_status": "Needs Manual Mapping",
            "latest": "Data Missing",
            "history_60d": "Data Missing",
            "volume": "Data Missing",
            "turnover": "Optional Data Missing",
            "ma": "Data Missing",
            "valuation": "Optional Data Missing",
            "status": "Needs Manual Mapping",
            "source": "None",
            "timestamp": "Data Missing",
            "notes": "Ticker not found in registry",
        }

    symbol = provider_symbol(entry)
    if not symbol:
        return {
            "name": entry.get("name", name),
            "code": entry.get("code") or "Data Missing",
            "market": entry.get("market", "Unknown"),
            "provider_symbol": "Needs Manual Mapping",
            "identity_status": entry.get("identity_status", "Needs Manual Mapping"),
            "latest": "Data Missing",
            "history_60d": "Data Missing",
            "volume": "Data Missing",
            "turnover": "Optional Data Missing",
            "ma": "Data Missing",
            "valuation": "Optional Data Missing",
            "status": "Needs Manual Mapping",
            "source": "None",
            "timestamp": "Data Missing",
            "notes": entry.get("notes", "Ticker mapping not confirmed"),
        }

    snapshot = get_market_snapshot(symbol, entry.get("market", "Unknown"))
    missing = snapshot.get("missing_fields", [])
    has_history_60d = (
        snapshot.get("change_5d_pct") is not None
        and snapshot.get("change_20d_pct") is not None
        and snapshot.get("change_60d_pct") is not None
    )
    has_ma = snapshot.get("ma20") is not None and snapshot.get("ma60") is not None
    has_valuation = any(snapshot.get(field) is not None for field in ["market_cap", "pe", "pb"])

    return {
        "name": entry.get("name", name),
        "code": entry.get("code") or "Data Missing",
        "market": entry.get("market", "Unknown"),
        "provider_symbol": symbol,
        "identity_status": entry.get("identity_status", "Unknown"),
        "latest": "Available" if snapshot.get("latest_price") is not None else "Data Missing",
        "history_60d": "Available" if has_history_60d else "Partial" if snapshot.get("latest_price") is not None else "Data Missing",
        "volume": "Available" if snapshot.get("volume") is not None else "Data Missing",
        "turnover": "Available" if snapshot.get("turnover") is not None else "Optional Data Missing",
        "ma": "Available" if has_ma else "Partial",
        "valuation": "Available" if has_valuation else "Optional Data Missing",
        "status": snapshot.get("data_status", "Unavailable"),
        "source": snapshot.get("source") or "None",
        "timestamp": snapshot.get("timestamp") or "Data Missing",
        "notes": "; ".join(missing[:5]) if missing else "OK",
    }


def rows_for(names: Iterable[str], registry: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [smoke_row(name, registry) for name in names]


def md_table(headers: List[str], rows: List[List[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("\n", " ") for cell in row) + " |")
    return "\n".join(lines)


def status_summary(rows: List[Dict[str, Any]]) -> str:
    if all(row["status"] in {"Available", "Partial"} for row in rows):
        return "Available"
    if any(row["status"] in {"Available", "Partial"} for row in rows):
        return "Partial"
    return "Blocked"


def registry_table(registry: Dict[str, Dict[str, Any]]) -> str:
    unique_entries: List[Dict[str, Any]] = []
    seen = set()
    for entry in registry.values():
        key = entry.get("name")
        if key and key not in seen:
            seen.add(key)
            unique_entries.append(entry)

    rows = []
    for entry in unique_entries:
        symbol = provider_symbol(entry)
        rows.append(
            [
                entry.get("name", ""),
                entry.get("code") or "Data Missing",
                entry.get("market", ""),
                symbol or "Needs Manual Mapping",
                entry.get("identity_status", ""),
                entry.get("notes", ""),
            ]
        )
    return md_table(["Name", "Code", "Market", "Provider Symbol", "Identity Status", "Notes"], rows)


def smoke_table(rows: List[Dict[str, Any]], first_col: str) -> str:
    return md_table(
        [first_col, "Market", "Latest", "History 60d", "Volume", "MA20/MA60", "Valuation", "Status", "Source", "Notes"],
        [
            [
                row["name"],
                row["market"],
                row["latest"],
                row["history_60d"],
                row["volume"],
                row["ma"],
                row["valuation"],
                row["status"],
                row["source"],
                row["notes"],
            ]
            for row in rows
        ],
    )


def main() -> int:
    registry = load_registry()
    current = rows_for(CURRENT_HOLDINGS, registry)
    a_share = rows_for(A_SHARE_CANDIDATES, registry)
    hk = rows_for(HK_CANDIDATES, registry)
    us_etf = rows_for(US_ETF, registry)

    mapped_current = [row for row in current if row["status"] != "Needs Manual Mapping"]
    mapped_candidates = [row for row in a_share + hk + us_etf if row["status"] != "Needs Manual Mapping"]
    current_ok = bool(mapped_current) and all(row["status"] in {"Available", "Partial"} for row in mapped_current)
    candidates_ok = bool(mapped_candidates) and all(row["status"] in {"Available", "Partial"} for row in mapped_candidates)
    has_unmapped = any(row["status"] == "Needs Manual Mapping" for row in current + a_share + hk + us_etf)

    if current_ok and candidates_ok and not has_unmapped:
        decision = "READY"
    elif mapped_current or mapped_candidates:
        decision = "PARTIAL"
    else:
        decision = "BLOCKED"

    lines = [
        "# Market Data Provider Smoke Test Result",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Executive Summary",
        "",
        f"- Overall provider status: {decision}",
        f"- Current holdings data status: {status_summary(current)}",
        f"- A-share candidate data status: {status_summary(a_share)}",
        f"- Hong Kong candidate data status: {status_summary(hk)}",
        f"- US / ETF data status: {status_summary(us_etf)}",
        "- Main blockers: 泰金新能 and DRAM ETF remain Needs Manual Mapping; valuation and turnover are optional and often missing.",
        "",
        "## Ticker Registry Status",
        "",
        registry_table(registry),
        "",
        "## Current Holdings Smoke Test",
        "",
        smoke_table(current, "Holding"),
        "",
        "## A-share Candidates",
        "",
        smoke_table(a_share, "Candidate"),
        "",
        "## Hong Kong Candidates",
        "",
        smoke_table(hk, "Candidate"),
        "",
        "## US / ETF",
        "",
        smoke_table(us_etf, "Candidate"),
        "",
        "## Final Decision",
        "",
        decision,
        "",
        "## Next Step",
        "",
        "Confirm executable ticker mappings for 泰金新能 and DRAM ETF.",
        "",
        "## Safety",
        "",
        "- No private portfolio amount stored.",
        "- No portfolio allocation modified.",
        "- No CDE logic modified.",
        "- No Decision Brief strategy logic modified.",
        "- No new Engine created.",
    ]
    RESULT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(smoke_table(current, "Holding"))
    print()
    print(smoke_table(a_share, "A-share Candidate"))
    print()
    print(smoke_table(hk, "HK Candidate"))
    print()
    print(smoke_table(us_etf, "US / ETF"))
    print(f"\nFinal Decision: {decision}")
    print(f"Result written to: {RESULT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
