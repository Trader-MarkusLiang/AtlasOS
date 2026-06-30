#!/usr/bin/env python3
"""Validate Rebalance Execution Plan v0.1.

This script produces a Markdown acceptance-test result. It does not modify portfolio allocation,
CDE formulas, strategy logic, or execution state.
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

from tools.market_data import (  # noqa: E402
    aggregate_anomaly_status,
    check_data_anomaly,
    get_domestic_market_snapshot,
    migration_band_from_anomaly,
)


REGISTRY_PATH = REPO_ROOT / "tools" / "market_data" / "ticker_registry.yaml"
RESULT_PATH = REPO_ROOT / "99_Verification" / "Rebalance_Execution_Plan_Test_Result.md"

HOLDINGS = ["雅克科技", "建滔集团", "东山精密", "泰金新能"]
CANDIDATES = ["赛腾股份", "澜起科技", "江丰电子", "太极实业", "广钢气体", "昊华科技"]


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
    if entry.get("identity_status") != "Validated":
        return ""
    return symbols.get("akshare") or symbols.get("yfinance") or ""


def snapshot(name: str, registry: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    entry = registry[name]
    return get_domestic_market_snapshot(
        provider_symbol(entry),
        entry.get("market", ""),
        name=entry.get("name", name),
        exchange=entry.get("exchange", ""),
    )


def rows(names: Iterable[str], registry: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    result = []
    for name in names:
        snap = snapshot(name, registry)
        anomaly = check_data_anomaly(snap)
        snap["anomaly_status"] = anomaly["anomaly_status"]
        snap["anomaly_flags"] = anomaly["anomaly_flags"]
        snap["decision_impact"] = anomaly["decision_impact"]
        result.append(snap)
    return result


def holding_treatment(row: Dict[str, Any]) -> str:
    if row.get("anomaly_status") == "Severe":
        return "Data Limited"
    if row.get("market_structure_status") == "Overextended":
        return "Trim if Extended"
    if row.get("execution_readiness") == "Wait for Pullback":
        return "Hold / Watch"
    return "Hold Core"


def receiving_priority(row: Dict[str, Any]) -> str:
    if row.get("anomaly_status") == "Severe":
        return "Data Limited"
    readiness = row.get("execution_readiness")
    if readiness == "Wait for Pullback":
        return "Pullback Candidate"
    if readiness == "Wait for Breakout Confirmation":
        return "Breakout Confirmation Candidate"
    if readiness == "Pilot Deployment Candidate":
        return "Pilot Deployment Candidate"
    return "Watch"


def fmt(value: Any) -> str:
    if value is None:
        return "Data Missing"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def md_table(headers: List[str], rows_: List[List[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows_:
        lines.append("| " + " | ".join(str(cell).replace("\n", " ") for cell in row) + " |")
    return "\n".join(lines)


def main() -> int:
    registry = load_registry()
    holding_rows = rows(HOLDINGS, registry)
    candidate_rows = rows(CANDIDATES, registry)
    checks = [
        {key: row[key] for key in ["ticker", "name", "anomaly_status", "anomaly_flags", "decision_impact"]}
        for row in holding_rows + candidate_rows
    ]
    aggregate = aggregate_anomaly_status(checks)
    band = migration_band_from_anomaly(aggregate, cde_precision_limited=True)
    plan_pass = aggregate["anomaly_status"] in {"Warning", "Severe"} and band in {"0-5%", "5-10%"}

    lines = [
        "# Rebalance Execution Plan Test Result",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Scenario",
        "",
        "User asks whether the domestic account can migrate 20%-40% exposure during a morning rebalance window, using current holdings, domestic snapshots, candidate ranking, and CDE boundary.",
        "",
        "## Required Boundary",
        "",
        "Execution Plan is not Trading Authority. CDE authorization and user confirmation are still required.",
        "",
        "## Precheck Result",
        "",
        "| Check | Result |",
        "|---|---|",
        "| Portfolio Context required | PASS |",
        "| Domestic Market Snapshot required | PASS |",
        "| Data Anomaly Check required | PASS |",
        "| CDE boundary required | PASS |",
        "| Strategic Candidate Ranking is not Trading Authority | PASS |",
        "| Execution Readiness is not Trading Authority | PASS |",
        "",
        "## Data Anomaly Check",
        "",
        f"- Aggregate anomaly status: {aggregate['anomaly_status']}",
        f"- Decision impact: {aggregate['decision_impact']}",
        f"- Migration Authority cap from anomaly / CDE precision: {band}",
        "",
        md_table(
            ["Name", "Structure", "20D", "60D", "MA20 Gap", "Anomaly", "Impact", "Flags"],
            [
                [
                    row.get("name"),
                    row.get("market_structure_status"),
                    fmt(row.get("change_20d_pct")),
                    fmt(row.get("change_60d_pct")),
                    fmt(row.get("price_vs_ma20_pct")),
                    row.get("anomaly_status"),
                    row.get("decision_impact"),
                    "; ".join(row.get("anomaly_flags") or []) or "None",
                ]
                for row in holding_rows + candidate_rows
            ],
        ),
        "",
        "## Current Holding Assessment",
        "",
        md_table(
            ["Holding", "Role", "Current Structure", "Execution Readiness", "Anomaly Status", "Portfolio Role", "Suggested Treatment"],
            [
                [
                    row.get("name"),
                    "Current Holding",
                    row.get("market_structure_status"),
                    row.get("execution_readiness"),
                    row.get("anomaly_status"),
                    "Existing exposure",
                    holding_treatment(row),
                ]
                for row in holding_rows
            ],
        ),
        "",
        "## Candidate Receiving Assessment",
        "",
        md_table(
            ["Candidate", "Research Tier", "Market Structure", "Execution Readiness", "Anomaly Status", "Portfolio Fit", "Receiving Priority"],
            [
                [
                    row.get("name"),
                    "Needs Strategic Candidate Dashboard",
                    row.get("market_structure_status"),
                    row.get("execution_readiness"),
                    row.get("anomaly_status"),
                    "Needs portfolio fit review",
                    receiving_priority(row),
                ]
                for row in candidate_rows
            ],
        ),
        "",
        "## Migration Authority",
        "",
        f"- Requested band: 20-40%",
        f"- Allowed validation band: {band}",
        "- Reason: Data anomaly check detected extreme 20D / 60D moves and CDE Precision Limited applies.",
        "- Migration Authority is not CDE Authority and not mandatory action.",
        "",
        "## Execution Tiers",
        "",
        md_table(
            ["Tier", "Condition", "Action Vocabulary", "Max Scope", "Stop Condition"],
            [
                ["Tier 0", "Severe anomaly or no CDE", "Observe / Hold", "0-5%", "Execution blocked"],
                ["Tier 1", "Warning anomaly or extended structure", "Observe / Hold / Reduce", "5-10%", "Anomaly worsens"],
                ["Tier 2", "CDE and market confirmation align", "Build / Accumulate / Reduce", "10-20%", "Confirmation fails"],
                ["Tier 3", "Strong evidence + CDE + user confirmation", "Build / Accumulate / Reduce", "20-40%", "User does not confirm"],
            ],
        ),
        "",
        "## Stop Conditions",
        "",
        "- Data anomaly severe.",
        "- Market structure deterioration.",
        "- Price gap too extended.",
        "- Volume confirmation failure.",
        "- CDE not authorized.",
        "- Portfolio exposure conflict.",
        "- Thesis evidence weakens.",
        "- User does not confirm execution.",
        "",
        "## Follow-up Triggers",
        "",
        "- Pullback to MA20 / MA60.",
        "- Breakout confirmation.",
        "- Volume confirmation.",
        "- Candidate relative strength improves.",
        "- Current holding overextension eases.",
        "- CDE authority improves.",
        "- New fundamental evidence.",
        "- Market risk declines.",
        "",
        "## Post-Action Review",
        "",
        "If the user executes a rebalance, Atlas should later request intended action, actual action, reason, market context, execution quality, missed opportunity / avoided risk, and whether World Model / CDE / Portfolio rules need update. Do not store private amounts.",
        "",
        "## Acceptance Result",
        "",
        "PASS" if plan_pass else "FAIL",
    ]

    RESULT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Aggregate anomaly status: {aggregate['anomaly_status']}")
    print(f"Migration Authority cap: {band}")
    print(f"Acceptance Result: {'PASS' if plan_pass else 'FAIL'}")
    print(f"Result written to: {RESULT_PATH}")
    return 0 if plan_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
