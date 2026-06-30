#!/usr/bin/env python3
"""Validate domestic market snapshot support for Atlas OS.

This script writes a Markdown validation result. It does not modify portfolio files, strategy
logic, CDE, allocation, or execution state.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.market_data import get_domestic_market_snapshot  # noqa: E402


REGISTRY_PATH = REPO_ROOT / "tools" / "market_data" / "ticker_registry.yaml"
RESULT_PATH = REPO_ROOT / "99_Verification" / "Domestic_Market_Snapshot_Result.md"

CURRENT_DOMESTIC_HOLDINGS = ["雅克科技", "建滔集团", "东山精密", "泰金新能"]
A_SHARE_CANDIDATES = ["赛腾股份", "澜起科技", "江丰电子", "太极实业", "广钢气体", "昊华科技"]
HK_CANDIDATES = ["中芯国际", "长飞光纤光缆"]


def load_registry() -> Dict[str, Dict[str, Any]]:
    with REGISTRY_PATH.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    registry: Dict[str, Dict[str, Any]] = {}
    for entry in data.get("tickers", []):
        for name in [entry.get("name", "")] + (entry.get("aliases") or []):
            if name:
                registry[name] = entry
    return registry


def provider_symbol(entry: Dict[str, Any]) -> str:
    symbols = entry.get("provider_symbols") or {}
    market = entry.get("market")
    if entry.get("identity_status") != "Validated":
        return ""
    if market in {"A-share", "HK"}:
        return symbols.get("akshare") or symbols.get("yfinance") or ""
    return symbols.get("yfinance") or symbols.get("akshare") or ""


def snapshot_for(name: str, registry: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    entry = registry.get(name)
    if not entry:
        return {
            "name": name,
            "code": "Data Missing",
            "market": "Unknown",
            "source": "None",
            "timestamp": "Data Missing",
            "latest_price": None,
            "change_5d_pct": None,
            "change_20d_pct": None,
            "change_60d_pct": None,
            "price_vs_ma20_pct": None,
            "volume_ratio_20d": None,
            "market_structure_status": "Data Insufficient",
            "execution_readiness": "Data Insufficient",
            "data_status": "Unavailable",
            "data_freshness": "Unknown",
            "missing_fields": ["ticker_registry_entry"],
            "errors": ["Ticker not found in registry"],
        }

    symbol = provider_symbol(entry)
    if not symbol:
        return {
            "name": entry.get("name", name),
            "code": entry.get("code") or "Data Missing",
            "market": entry.get("market", "Unknown"),
            "source": "None",
            "timestamp": "Data Missing",
            "latest_price": None,
            "change_5d_pct": None,
            "change_20d_pct": None,
            "change_60d_pct": None,
            "price_vs_ma20_pct": None,
            "volume_ratio_20d": None,
            "market_structure_status": "Data Insufficient",
            "execution_readiness": "Data Insufficient",
            "data_status": "Unavailable",
            "data_freshness": "Unknown",
            "missing_fields": ["provider_symbol"],
            "errors": [entry.get("notes", "Provider symbol missing")],
        }

    snapshot = get_domestic_market_snapshot(
        symbol,
        entry.get("market", "Unknown"),
        name=entry.get("name", name),
        exchange=entry.get("exchange", ""),
    )
    snapshot["code"] = entry.get("code") or symbol
    return snapshot


def rows_for(names: Iterable[str], registry: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [snapshot_for(name, registry) for name in names]


def fmt(value: Any, digits: int = 2) -> str:
    if value is None:
        return "Data Missing"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def compact_missing(row: Dict[str, Any]) -> str:
    missing = row.get("missing_fields") or []
    if not missing:
        return "None"
    return "; ".join(missing[:6])


def md_table(headers: List[str], rows: List[List[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("\n", " ") for cell in row) + " |")
    return "\n".join(lines)


def snapshot_table(rows: List[Dict[str, Any]]) -> str:
    return md_table(
        [
            "Name",
            "Code",
            "Market",
            "Source",
            "Timestamp",
            "Latest",
            "5D",
            "20D",
            "60D",
            "MA20 Gap",
            "Volume Ratio",
            "Structure",
            "Readiness",
            "Data Status",
            "Freshness",
            "Missing",
        ],
        [
            [
                row.get("name", ""),
                row.get("code", ""),
                row.get("market", ""),
                row.get("source") or "None",
                row.get("timestamp") or "Data Missing",
                fmt(row.get("latest_price")),
                fmt(row.get("change_5d_pct")),
                fmt(row.get("change_20d_pct")),
                fmt(row.get("change_60d_pct")),
                fmt(row.get("price_vs_ma20_pct")),
                fmt(row.get("volume_ratio_20d")),
                row.get("market_structure_status", ""),
                row.get("execution_readiness", ""),
                row.get("data_status", ""),
                row.get("data_freshness", ""),
                compact_missing(row),
            ]
            for row in rows
        ],
    )


def status_summary(rows: List[Dict[str, Any]]) -> str:
    if all(row.get("data_status") in {"Available", "Partial"} for row in rows):
        return "Available"
    if any(row.get("data_status") in {"Available", "Partial"} for row in rows):
        return "Partial"
    return "Blocked"


def source_summary(rows: List[Dict[str, Any]]) -> str:
    sources = sorted({row.get("source") or "None" for row in rows})
    return ", ".join(sources)


def final_decision(current: List[Dict[str, Any]], a_share: List[Dict[str, Any]], hk: List[Dict[str, Any]]) -> str:
    current_ready = all(row.get("data_status") == "Available" for row in current)
    candidate_rows = a_share + hk
    candidate_ready_count = sum(1 for row in candidate_rows if row.get("data_status") in {"Available", "Partial"})
    freshness_ok = all(row.get("data_freshness") in {"Fresh", "Delayed", "Unknown"} for row in current + candidate_rows)
    most_candidates_ready = candidate_ready_count >= max(1, int(len(candidate_rows) * 0.75))
    if current_ready and most_candidates_ready and freshness_ok:
        return "DOMESTIC READY"
    if candidate_ready_count or any(row.get("data_status") in {"Available", "Partial"} for row in current):
        return "DOMESTIC PARTIAL"
    return "DOMESTIC BLOCKED"


def main() -> int:
    registry = load_registry()
    current = rows_for(CURRENT_DOMESTIC_HOLDINGS, registry)
    a_share = rows_for(A_SHARE_CANDIDATES, registry)
    hk = rows_for(HK_CANDIDATES, registry)
    decision = final_decision(current, a_share, hk)
    all_rows = current + a_share + hk

    lines = [
        "# Domestic Market Snapshot Result",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Executive Summary",
        "",
        f"- Final decision: {decision}",
        f"- Current domestic holdings status: {status_summary(current)}",
        f"- A-share candidate status: {status_summary(a_share)}",
        f"- Hong Kong candidate status: {status_summary(hk)}",
        f"- Provider sources used: {source_summary(all_rows)}",
        "- Execution Readiness is not Trading Authority. CDE authorization is still required.",
        "",
        "## Current Domestic Holdings",
        "",
        snapshot_table(current),
        "",
        "## A-share Candidates",
        "",
        snapshot_table(a_share),
        "",
        "## Hong Kong Candidates",
        "",
        snapshot_table(hk),
        "",
        "## Rule Explanation",
        "",
        "- Market Structure is rule-based from price vs MA20 / MA60, 20D / 60D trend, distance from highs / lows, and volume ratio.",
        "- Execution Readiness is an input-only classification for Decision Brief / CDE / Rebalance review; it is not trade authority.",
        "- Data Freshness is conservative: current date is Fresh, recent prior dates are Delayed, older dates are Stale, unclear dates are Unknown.",
        "- Missing turnover / valuation does not fail the snapshot when quote, history, volume, and moving averages are available.",
        "",
        "## Safety",
        "",
        "- No portfolio file modified.",
        "- No allocation percentage stored.",
        "- No private amount, cost, net worth, or account balance stored.",
        "- No strategy logic modified.",
        "- No CDE logic modified.",
        "- No new Engine created.",
        "- No automatic trading.",
    ]

    RESULT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(snapshot_table(current))
    print()
    print(snapshot_table(a_share))
    print()
    print(snapshot_table(hk))
    print(f"\nFinal Decision: {decision}")
    print(f"Result written to: {RESULT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
