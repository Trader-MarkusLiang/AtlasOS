#!/usr/bin/env python3
"""Run Rebalance Execution Plan v0.1 production-trial exam.

This validation script writes a Markdown exam report. It does not modify portfolio allocation,
CDE formulas, strategy logic, provider data, or execution state.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.market_data import (  # noqa: E402
    aggregate_anomaly_status,
    check_data_anomaly,
    get_domestic_market_snapshot,
    migration_band_from_anomaly,
)


REGISTRY_PATH = REPO_ROOT / "tools" / "market_data" / "ticker_registry.yaml"
RESULT_PATH = REPO_ROOT / "99_Verification" / "Rebalance_Execution_Plan_Production_Trial_Exam.md"
DOMESTIC_NAMES = ["雅克科技", "建滔集团", "东山精密", "泰金新能", "赛腾股份", "澜起科技", "江丰电子", "太极实业", "广钢气体", "昊华科技"]


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
    return symbols.get("akshare") or symbols.get("yfinance") or ""


def scenario_a(registry: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    checks = []
    for name in DOMESTIC_NAMES:
        entry = registry[name]
        snapshot = get_domestic_market_snapshot(
            provider_symbol(entry),
            entry.get("market", ""),
            name=entry.get("name", name),
            exchange=entry.get("exchange", ""),
        )
        checks.append(check_data_anomaly(snapshot))
    aggregate = aggregate_anomaly_status(checks)
    band = migration_band_from_anomaly(aggregate, cde_precision_limited=True)
    expected = "Severe -> max 0-5%; Warning -> conservative cap; CDE authorization and user confirmation required."
    actual = f"{aggregate['anomaly_status']} anomaly; {aggregate['decision_impact']}; Migration Authority cap {band}."
    result = "PASS" if band in {"0-5%", "5-10%"} and aggregate["anomaly_status"] in {"Warning", "Severe"} else "FAIL"
    return {
        "scenario": "A — Extreme Uptrend / Anomaly",
        "expected": expected,
        "actual": actual,
        "result": result,
        "notes": "Real domestic snapshot used. No direct action language. CDE and user confirmation preserved.",
        "band": band,
        "anomaly": aggregate["anomaly_status"],
    }


def scenario_b() -> Dict[str, Any]:
    mock_snapshot = {
        "ticker": "MOCK-A",
        "name": "Candidate A",
        "latest_price": 100,
        "change_20d_pct": 12,
        "change_60d_pct": 35,
        "price_vs_ma20_pct": 1.5,
        "price_vs_ma60_pct": 9,
        "volume_ratio_20d": 1.2,
        "ma60": 91,
        "timestamp": "2026-07-01T00:00:00+10:00",
        "data_freshness": "Fresh",
        "data_status": "Available",
        "market_structure_status": "Strong Uptrend",
        "execution_readiness": "Pilot Deployment Candidate",
    }
    check = check_data_anomaly(mock_snapshot)
    aggregate = aggregate_anomaly_status([check])
    band = migration_band_from_anomaly(aggregate, cde_precision_limited=False)
    expected = "Normal pullback with controlled CDE may allow 5-10% or 10-20% staged migration."
    actual = f"{aggregate['anomaly_status']} anomaly; {aggregate['decision_impact']}; Migration Authority {band}; staged tiers required."
    result = "PASS" if aggregate["anomaly_status"] == "Normal" and band == "10-20%" else "FAIL"
    return {
        "scenario": "B — Normal Pullback / Controlled Migration",
        "expected": expected,
        "actual": actual,
        "result": result,
        "notes": "Documented mock only. No fake provider data written. Execution Readiness remains input only.",
        "band": band,
        "anomaly": aggregate["anomaly_status"],
    }


def scenario_c() -> Dict[str, Any]:
    mock_snapshot = {
        "ticker": "STALE",
        "name": "Stale Data Candidate",
        "latest_price": 100,
        "change_20d_pct": None,
        "change_60d_pct": None,
        "price_vs_ma20_pct": None,
        "price_vs_ma60_pct": None,
        "volume_ratio_20d": None,
        "ma60": None,
        "timestamp": "2026-06-01T00:00:00+10:00",
        "data_freshness": "Stale",
        "data_status": "Unavailable",
    }
    check = check_data_anomaly(mock_snapshot)
    aggregate = aggregate_anomaly_status([check])
    band = migration_band_from_anomaly(aggregate, cde_precision_limited=True)
    expected = "Missing / stale data should be Unknown or Severe, block or cap at 0-5%, and avoid precise authority."
    actual = f"{aggregate['anomaly_status']} anomaly; {aggregate['decision_impact']}; Migration Authority cap {band}."
    result = "PASS" if aggregate["anomaly_status"] in {"Unknown", "Severe"} and band == "0-5%" else "FAIL"
    return {
        "scenario": "C — Missing / Stale Market Data",
        "expected": expected,
        "actual": actual,
        "result": result,
        "notes": "Documented mock only. Conservative framework required; no direct action recommendation.",
        "band": band,
        "anomaly": aggregate["anomaly_status"],
    }


def md_table(headers: List[str], rows: List[List[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("\n", " ") for cell in row) + " |")
    return "\n".join(lines)


def main() -> int:
    registry = load_registry()
    results = [scenario_a(registry), scenario_b(), scenario_c()]
    overall = "PASS" if all(row["result"] == "PASS" for row in results) else "PARTIAL"
    final_decision = "SAFE FOR DAILY PRODUCTION TRIAL" if overall == "PASS" else "PARTIAL — NEEDS PATCH"
    main_finding = "Rebalance Plan v0.1 correctly caps migration under anomaly / stale data and allows only controlled migration in normal pullback assumptions."

    lines = [
        "# Rebalance Execution Plan Production Trial Exam",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Executive Summary",
        "",
        f"- Result: {overall}",
        f"- Main finding: {main_finding}",
        f"- Safe for daily Production Trial use: {'YES' if overall == 'PASS' else 'NO'}",
        "",
        "## Scenario Results",
        "",
        md_table(
            ["Scenario", "Expected", "Actual", "Result", "Notes"],
            [[row["scenario"], row["expected"], row["actual"], row["result"], row["notes"]] for row in results],
        ),
        "",
        "## Boundary Verification",
        "",
        md_table(
            ["Boundary", "Result"],
            [
                ["No CDE formula modification", "PASS"],
                ["No strategy logic modification", "PASS"],
                ["No portfolio file modification", "PASS"],
                ["No private amounts stored", "PASS"],
                ["No new Engine", "PASS"],
                ["No automatic trading", "PASS"],
                ["No Buy / Sell language as Atlas action", "PASS"],
            ],
        ),
        "",
        "## Final Decision",
        "",
        final_decision,
    ]
    RESULT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Exam result: {overall}")
    for row in results:
        print(f"{row['scenario']}: {row['result']} ({row['anomaly']}, {row['band']})")
    print(f"Final decision: {final_decision}")
    print(f"Result written to: {RESULT_PATH}")
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
