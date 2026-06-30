#!/usr/bin/env python3
"""Validate Atlas OS market data provider setup.

This script writes a Markdown validation result. It does not cache market data, modify portfolio
files, execute trades, or change strategy logic.
"""

from __future__ import annotations

import importlib
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.market_data import get_market_snapshot  # noqa: E402


REQUIRED_PACKAGES = [
    ("pandas", "pandas"),
    ("numpy", "numpy"),
    ("requests", "requests"),
    ("akshare", "akshare"),
    ("yfinance", "yfinance"),
    ("beautifulsoup4", "bs4"),
    ("lxml", "lxml"),
    ("pandas_market_calendars", "pandas_market_calendars"),
]

REGISTRY_PATH = REPO_ROOT / "tools" / "market_data" / "ticker_registry.yaml"
RESULT_PATH = REPO_ROOT / "99_Verification" / "Market_Data_Provider_Validation_Result.md"


def package_audit() -> List[Dict[str, str]]:
    rows = []
    for label, module_name in REQUIRED_PACKAGES:
        try:
            module = importlib.import_module(module_name)
            rows.append(
                {
                    "package": label,
                    "installed": "YES",
                    "version": str(getattr(module, "__version__", "unknown")),
                    "notes": "Import OK",
                }
            )
        except Exception as exc:
            rows.append(
                {
                    "package": label,
                    "installed": "NO",
                    "version": "Data Missing",
                    "notes": f"{type(exc).__name__}: {exc}",
                }
            )
    return rows


def load_registry() -> List[Dict[str, Any]]:
    with REGISTRY_PATH.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return data.get("tickers", [])


def provider_symbol(entry: Dict[str, Any]) -> str:
    symbols = entry.get("provider_symbols") or {}
    market = entry.get("market")
    if market == "A-share":
        return symbols.get("akshare") or symbols.get("yfinance") or ""
    if market == "HK":
        return symbols.get("akshare") or symbols.get("yfinance") or ""
    if market in {"US", "US / ETF", "ETF"}:
        return symbols.get("yfinance") or ""
    return symbols.get("akshare") or symbols.get("yfinance") or ""


def validation_rows() -> List[Dict[str, Any]]:
    rows = []
    for entry in load_registry():
        name = entry.get("name", "")
        status = entry.get("identity_status", "")
        market = entry.get("market", "")
        symbol = provider_symbol(entry)

        if status == "Needs Manual Mapping" or not symbol:
            rows.append(
                {
                    "name": name,
                    "ticker": symbol or "Needs Manual Mapping",
                    "market": market,
                    "latest": "Data Missing",
                    "history": "Data Missing",
                    "volume": "Data Missing",
                    "valuation": "Valuation Data Missing — Optional",
                    "status": "Needs Manual Mapping",
                    "source": "None",
                    "notes": entry.get("notes", "Ticker mapping not confirmed"),
                }
            )
            continue

        snapshot = get_market_snapshot(symbol, market)
        missing = snapshot.get("missing_fields", [])
        latest_status = "Available" if snapshot.get("latest_price") is not None else "Data Missing"
        history_status = (
            "Available"
            if snapshot.get("change_5d_pct") is not None and snapshot.get("change_20d_pct") is not None
            else "Partial"
            if snapshot.get("latest_price") is not None
            else "Data Missing"
        )
        volume_status = "Available" if snapshot.get("volume") is not None else "Data Missing"
        valuation_status = (
            "Available"
            if any(snapshot.get(field) is not None for field in ["market_cap", "pe", "pb"])
            else "Valuation Data Missing — Optional"
        )

        rows.append(
            {
                "name": name,
                "ticker": symbol,
                "market": market,
                "latest": latest_status,
                "history": history_status,
                "volume": volume_status,
                "valuation": valuation_status,
                "status": snapshot.get("data_status", "Unavailable"),
                "source": snapshot.get("source") or "None",
                "notes": "; ".join(missing[:4]) if missing else "OK",
            }
        )
    return rows


def md_table(headers: List[str], rows: List[List[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("\n", " ") for cell in row) + " |")
    return "\n".join(lines)


def main() -> int:
    packages = package_audit()
    rows = validation_rows()

    package_ok = all(row["installed"] == "YES" for row in packages)
    successful_fetches = [row for row in rows if row["status"] in {"Available", "Partial"}]
    has_a_or_hk = any(row["market"] in {"A-share", "HK"} for row in successful_fetches)

    if package_ok and has_a_or_hk:
        final_decision = "PARTIAL"
    elif package_ok:
        final_decision = "BLOCKED"
    else:
        final_decision = "BLOCKED"

    lines = [
        "# Market Data Provider Validation Result",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Package Import Result",
        "",
        md_table(
            ["Package", "Installed", "Version", "Notes"],
            [[r["package"], r["installed"], r["version"], r["notes"]] for r in packages],
        ),
        "",
        "## Ticker Validation Result",
        "",
        md_table(
            ["Ticker", "Name", "Market", "Latest", "History", "Volume", "Valuation", "Status", "Source", "Notes"],
            [
                [
                    r["ticker"],
                    r["name"],
                    r["market"],
                    r["latest"],
                    r["history"],
                    r["volume"],
                    r["valuation"],
                    r["status"],
                    r["source"],
                    r["notes"],
                ]
                for r in rows
            ],
        ),
        "",
        "## Final Decision",
        "",
        final_decision,
        "",
        "## Safety",
        "",
        "- No portfolio file modified.",
        "- No strategy logic modified.",
        "- No CDE logic modified.",
        "- No trading action executed.",
        "- No private portfolio amount stored.",
    ]

    RESULT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(md_table(
        ["Ticker", "Name", "Market", "Status", "Source"],
        [[r["ticker"], r["name"], r["market"], r["status"], r["source"]] for r in rows],
    ))
    print(f"\nFinal Decision: {final_decision}")
    print(f"Result written to: {RESULT_PATH}")
    return 0 if package_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
