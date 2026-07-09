"""Read-only Home intelligence presentation adapter.

This module only projects existing Atlas repository/runtime evidence into UI
view models. It does not create forecasts, mutate cognition, alter portfolio
state, or change trading authority.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping


CANDIDATE_SOURCE_PATH = Path("02_Databases/AI_Shovel_100.md")
FORECAST_STATUSES = ("OPEN", "MATURED", "VERIFIED", "INVALIDATED", "INCONCLUSIVE")
NO_TRADE_ACTIONS = {"buy", "sell"}


def build_home_intelligence(state: Mapping[str, Any]) -> dict[str, Any]:
    """Build all read-only Home intelligence panels from current state."""

    ledger = _mapping(state.get("forecast_ledger"))
    candidate_pool = _mapping(state.get("candidate_pool")) or build_candidate_pool(
        portfolio_context=_mapping(state.get("portfolio_context"))
    )
    return {
        "market_outlook": build_market_outlook(state, ledger),
        "forecast_accountability": build_forecast_accountability(ledger),
        "candidate_pool": candidate_pool,
        "expert_analysis": build_expert_analysis(state, ledger),
        "source_boundaries": {
            "read_only": True,
            "no_new_cognition": True,
            "no_trading_execution": True,
            "candidate_ranking_not_buy_recommendation": True,
        },
    }


def build_candidate_pool(
    *,
    portfolio_context: Mapping[str, Any] | None = None,
    source_path: Path | str = CANDIDATE_SOURCE_PATH,
) -> dict[str, Any]:
    """Parse the existing repository candidate pool into a safe UI view."""

    source = Path(source_path)
    if not source.exists():
        return {
            "status": "absent",
            "source": str(source),
            "items": [],
            "changes": [],
            "filters": {},
            "absence_reason": "candidate source file not found",
            "candidate_ranking_not_buy_recommendation": True,
        }
    text = source.read_text(encoding="utf-8")
    portfolio = _portfolio_needles(portfolio_context or {})
    items: list[dict[str, Any]] = []
    items.extend(_parse_priority_table(text, "Priority S", "S", portfolio, source))
    items.extend(_parse_priority_table(text, "Priority A", "A", portfolio, source))
    items.extend(_parse_watch_pool(text, portfolio, source))
    items = [_sanitize_candidate(item) for item in items]
    items = [item for item in items if item.get("asset")]
    changes = _candidate_changes(items)
    return {
        "status": "available" if items else "empty",
        "source": str(source),
        "items": items,
        "top_items": items[:5],
        "changes": changes,
        "filters": {
            "all": len(items),
            "portfolio_related": sum(1 for item in items if item.get("portfolio_relationship") != "None"),
            "high_priority": sum(1 for item in items if item.get("current_priority") in {"S", "A"}),
            "new": sum(1 for item in changes if item.get("change_type") == "entered_candidate_pool"),
            "changed_recently": len(changes),
        },
        "candidate_ranking_not_buy_recommendation": True,
        "no_trading_execution": True,
    }


def build_market_outlook(state: Mapping[str, Any], ledger: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Create a current forward view from existing state and ledger evidence."""

    ledger = _mapping(ledger)
    forecasts = _list(ledger.get("forecasts"))
    latest = _mapping(forecasts[0]) if forecasts else {}
    packet = _mapping(state.get("last_decision_packet"))
    regime = _text(state.get("regime_state") or packet.get("regime_state"), "Unknown")
    confidence = latest.get("confidence")
    if confidence is None:
        confidence = packet.get("confidence", 0.0)
    expected_state = _text(latest.get("expected_direction_state") or regime, "Unknown")
    statement = _text(latest.get("forecast_statement"), "")
    base_case = statement if statement else f"Current runtime state remains anchored around {expected_state} until contradicted."
    if not latest and regime.lower() == "unknown":
        base_case = "Insufficient evidence to form a forward view."
    invalidations = _list(latest.get("invalidation_conditions"))
    if not invalidations:
        invalidations = _default_invalidations(state)
    return {
        "status": "available" if latest or regime.lower() != "unknown" else "insufficient_evidence",
        "source": "forecast_ledger + current_runtime_state" if latest else "current_runtime_state",
        "base_case": base_case,
        "base_state": expected_state,
        "upside_scenario": _scenario_text(expected_state, "upside"),
        "downside_scenario": _scenario_text(expected_state, "downside"),
        "horizon": _text(latest.get("horizon"), "insufficient evidence"),
        "confidence": _safe_confidence(confidence),
        "invalidation_conditions": invalidations[:5],
        "distinct_from_forecast_ledger": True,
        "latest_forecast_id": latest.get("forecast_id"),
    }


def build_forecast_accountability(ledger: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Summarize existing forecast ledger accountability without changing it."""

    ledger = _mapping(ledger)
    forecasts = [_mapping(item) for item in _list(ledger.get("forecasts")) if isinstance(item, Mapping)]
    metrics = _mapping(ledger.get("metrics"))
    counts = {status.lower(): sum(1 for item in forecasts if _text(item.get("status"), "").upper() == status) for status in FORECAST_STATUSES}
    evaluated = [
        item
        for item in forecasts
        if _text(item.get("status"), "").upper() in {"VERIFIED", "INVALIDATED", "INCONCLUSIVE"}
    ]
    misses = [item for item in forecasts if _text(item.get("status"), "").upper() == "INVALIDATED"]
    return {
        "status": "available" if forecasts else "empty",
        "counts": counts,
        "metrics": metrics,
        "sample_warning": _text(ledger.get("sample_warning"), "Low sample size: calibration is directional only."),
        "latest": forecasts[:5],
        "recent_miss": misses[0] if misses else {},
        "evaluated_count": len(evaluated),
        "ledger_link": "/predictions",
        "learning_link": "/learning",
    }


def build_expert_analysis(state: Mapping[str, Any], ledger: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build structured expert analysis from state, ledger, and data quality."""

    ledger = _mapping(ledger)
    forecasts = [_mapping(item) for item in _list(ledger.get("forecasts")) if isinstance(item, Mapping)]
    latest_forecast = forecasts[0] if forecasts else {}
    packet = _mapping(state.get("last_decision_packet"))
    market = _mapping(state.get("market_intelligence"))
    portfolio = _mapping(state.get("portfolio_context"))
    edges = _top_edges(state)
    causal_chain = _causal_chain(edges, packet)
    channels = _mapping(market.get("channels"))
    live = sum(1 for value in channels.values() if _text(value, "").upper() == "LIVE")
    simulated = sum(1 for value in channels.values() if _text(value, "").upper() == "SIMULATED")
    missing = sum(1 for value in channels.values() if _text(value, "").upper() == "NOT_CONFIGURED")
    stale = sum(1 for value in channels.values() if _text(value, "").upper() in {"DELAYED", "CACHED", "RATE_LIMITED", "FAILED"})
    confidence_components = _confidence_components(state, ledger)
    raw_evidence = {
        "regime_state": state.get("regime_state"),
        "last_decision_packet": packet,
        "market_intelligence": {
            "status": market.get("status"),
            "channels": channels,
            "degraded": market.get("degraded"),
            "observations": _list(market.get("observations"))[:5],
        },
        "portfolio_context": {
            "status": portfolio.get("status"),
            "privacy": portfolio.get("privacy"),
            "exposure_sum_pct": portfolio.get("exposure_sum_pct"),
            "cash_or_unassigned_pct": portfolio.get("cash_or_unassigned_pct"),
            "exposure_map": portfolio.get("exposure_map"),
        },
        "forecast_ledger_summary": {
            "metrics": _mapping(ledger.get("metrics")),
            "sample_warning": ledger.get("sample_warning"),
            "latest_forecast_id": latest_forecast.get("forecast_id"),
        },
        "structural_coevolution_state": _compact_mapping(_mapping(state.get("structural_coevolution_state"))),
        "self_organization_state": _compact_mapping(_mapping(state.get("self_organization_state"))),
    }
    return {
        "status": "available",
        "section_count": 9,
        "causal_chain": causal_chain,
        "causal_edges": edges,
        "hypothesis_state": {
            "active": _text(latest_forecast.get("active_hypothesis"), "Insufficient system context"),
            "competing": _competing_hypotheses(state, latest_forecast),
            "confidence": _safe_confidence(latest_forecast.get("confidence", packet.get("confidence", 0.0))),
            "recent_change": _recent_hypothesis_change(state),
        },
        "regime_state": {
            "current": _text(state.get("regime_state"), "Unknown"),
            "proposed": _text(state.get("proposed_state"), "Unknown"),
            "volatility": _text(state.get("volatility"), "Unknown"),
        },
        "confidence_composition": confidence_components,
        "data_quality": {
            "live_channels": live,
            "simulated_channels": simulated,
            "missing_channels": missing,
            "stale_channels": stale,
            "limitation": _data_quality_limitation(live, simulated, missing, stale),
        },
        "portfolio_sensitivity": {
            "largest_positions": _list(_mapping(portfolio.get("exposure_map")).get("asset_concentration"))[:3],
            "theme_concentration": _mapping(_mapping(portfolio.get("exposure_map")).get("theme_concentration")),
            "cash_or_unassigned_pct": portfolio.get("cash_or_unassigned_pct"),
            "privacy": portfolio.get("privacy", "percentage_only_no_account_amounts"),
        },
        "forecast_evidence": {
            "latest_forecast_id": latest_forecast.get("forecast_id"),
            "status": latest_forecast.get("status"),
            "horizon": latest_forecast.get("horizon"),
            "statement": latest_forecast.get("forecast_statement"),
            "drivers": _list(latest_forecast.get("causal_drivers")),
        },
        "invalidation_conditions": _list(latest_forecast.get("invalidation_conditions")) or _default_invalidations(state),
        "raw_evidence": raw_evidence,
    }


def _parse_priority_table(
    text: str,
    heading: str,
    priority: str,
    portfolio_needles: set[str],
    source: Path,
) -> list[dict[str, Any]]:
    section = _section_after_heading(text, heading)
    rows = _table_rows(section)
    items: list[dict[str, Any]] = []
    for row in rows:
        if len(row) < 17:
            continue
        company = row[0]
        thesis = row[9]
        portfolio_relation = _portfolio_relationship(row, portfolio_needles)
        items.append(
            {
                "asset": company,
                "theme": row[2],
                "current_priority": priority,
                "portfolio_relationship": portfolio_relation,
                "evidence_strength": row[14],
                "thesis_direction": thesis,
                "status": "Elevated" if priority == "S" else "Research",
                "source_category": f"Priority {priority}",
                "source": str(source),
                "key_risk": row[11],
                "next_trigger": row[12],
                "last_update": row[15],
                "review_frequency": row[16],
                "reason": row[10],
            }
        )
    return items


def _parse_watch_pool(text: str, portfolio_needles: set[str], source: Path) -> list[dict[str, Any]]:
    section = _section_after_heading(text, "Priority B")
    rows = _table_rows(section)
    items: list[dict[str, Any]] = []
    for row in rows:
        if len(row) < 10:
            continue
        items.append(
            {
                "asset": row[0],
                "theme": row[2],
                "current_priority": "B",
                "portfolio_relationship": _portfolio_relationship(row, portfolio_needles),
                "evidence_strength": row[8],
                "thesis_direction": row[5],
                "status": "Watch",
                "source_category": "Priority B",
                "source": str(source),
                "key_risk": "Evidence not yet sufficient for promotion",
                "next_trigger": row[6],
                "last_update": row[9],
                "review_frequency": "event-driven",
                "reason": row[5],
            }
        )
    return items


def _section_after_heading(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.find(marker)
    if start < 0:
        return ""
    rest = text[start + len(marker) :]
    next_heading = rest.find("\n## ")
    return rest[:next_heading] if next_heading >= 0 else rest


def _table_rows(section: str) -> list[list[str]]:
    lines = [line.strip() for line in section.splitlines() if line.strip().startswith("|")]
    rows: list[list[str]] = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not cells or all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        if cells[0].lower() in {"company", "company / chain"}:
            continue
        rows.append(cells)
    return rows


def _portfolio_needles(portfolio_context: Mapping[str, Any]) -> set[str]:
    needles: set[str] = set()
    for item in _list(portfolio_context.get("positions")):
        if not isinstance(item, Mapping):
            continue
        for key in ("asset", "user_thesis"):
            text = _text(item.get(key), "")
            if text:
                if key == "asset":
                    needles.add(text.lower())
                for token in _portfolio_tokens(text):
                    if token:
                        needles.add(token.lower())
    return needles


def _portfolio_tokens(text: str) -> list[str]:
    separators = "/,;，；()（）[]【】"
    cleaned = text
    for separator in separators:
        cleaned = cleaned.replace(separator, " ")
    stopwords = {
        "pcb",
        "materials",
        "material",
        "ai",
        "hardware",
        "exposure",
        "chain",
        "semiconductor",
        "infrastructure",
        "manufacturing",
        "risk",
        "requires",
        "monitoring",
        "thesis",
    }
    tokens = []
    for token in cleaned.split():
        stripped = token.strip(".:：")
        if not stripped:
            continue
        if stripped.lower() in stopwords:
            continue
        if any("\u4e00" <= char <= "\u9fff" for char in stripped):
            if len(stripped) >= 3:
                tokens.append(stripped)
            continue
        if "." in stripped or stripped.isupper() or stripped in {"Kingboard", "Dongshan", "Anji"}:
            tokens.append(stripped)
    return tokens


def _portfolio_relationship(row: list[str], portfolio_needles: set[str]) -> str:
    joined = " ".join(row).lower()
    if " yes " in f" {joined} " or "|yes|" in joined:
        return "Direct"
    if any(needle and needle in joined for needle in portfolio_needles):
        return "Direct"
    return "None"


def _sanitize_candidate(item: Mapping[str, Any]) -> dict[str, Any]:
    record = dict(item)
    for key, value in list(record.items()):
        if isinstance(value, str):
            text = value.replace("\x00", " ").strip()
            for forbidden in NO_TRADE_ACTIONS:
                text = text.replace(forbidden.title(), "Capital Action").replace(forbidden.upper(), "CAPITAL ACTION")
            record[key] = text
    status = _text(record.get("status"), "Watch")
    if status not in {"Observe", "Research", "Watch", "Elevated", "Deprioritized"}:
        status = "Watch"
    record["status"] = status
    return record


def _candidate_changes(items: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    changes = []
    for item in items[:6]:
        change = "entered_candidate_pool"
        if item.get("current_priority") == "S":
            change = "priority_raised"
        changes.append(
            {
                "asset": item.get("asset"),
                "change_type": change,
                "why": item.get("reason") or item.get("next_trigger") or "Repository candidate pool evidence",
                "last_update": item.get("last_update"),
            }
        )
    return changes


def _scenario_text(base_state: str, kind: str) -> str:
    state = base_state.upper().replace(" ", "_")
    if kind == "upside":
        if state in {"RISK_OFF", "LIQUIDITY_STRESS"}:
            return "Liquidity improves while market breadth and data freshness recover."
        if state in {"ATTENTION_EXPANSION", "BREAKOUT"}:
            return "Attention converts into broader market participation and confirmed liquidity."
        return "Evidence quality improves and the current state stabilizes."
    if state in {"RISK_OFF", "LIQUIDITY_STRESS"}:
        return "Liquidity and credit-sensitive signals deteriorate together."
    if state in {"ATTENTION_EXPANSION", "BREAKOUT"}:
        return "Attention remains elevated but liquidity confirmation fails."
    return "Trust, data freshness, or portfolio-sensitive channels weaken."


def _default_invalidations(state: Mapping[str, Any]) -> list[str]:
    market = _mapping(state.get("market_intelligence"))
    channels = _mapping(market.get("channels"))
    items = ["trust_score_deteriorates", "portfolio_exposure_changes_materially"]
    if channels:
        items.insert(0, "live_market_channel_interrupts_or_delays")
    else:
        items.insert(0, "market_data_remains_unavailable")
    return items


def _top_edges(state: Mapping[str, Any]) -> list[dict[str, Any]]:
    structural = _mapping(state.get("structural_coevolution_state"))
    self_org = _mapping(state.get("self_organization_state"))
    candidates: dict[str, float] = {}
    for source in (
        _mapping(_mapping(structural.get("applied_drift")).get("edge_weights")),
        _mapping(_mapping(structural.get("mutation")).get("edge_weight_updates")),
        _mapping(self_org.get("causal_reweight_delta")),
    ):
        for key, value in source.items():
            try:
                candidates[str(key)] = float(value)
            except (TypeError, ValueError):
                continue
    edges = []
    for key, value in sorted(candidates.items(), key=lambda pair: abs(pair[1]), reverse=True)[:6]:
        parts = key.split("->") if "->" in key else key.split(":")
        edges.append(
            {
                "from": parts[0].strip() if parts else "Source",
                "to": parts[1].strip() if len(parts) > 1 else "Target",
                "weight_delta": round(value, 4),
            }
        )
    return edges


def _causal_chain(edges: list[Mapping[str, Any]], packet: Mapping[str, Any]) -> list[str]:
    if edges:
        chain = []
        for edge in edges[:4]:
            chain.append(f"{edge.get('from')} -> {edge.get('to')}")
        return chain
    summary = _text(packet.get("causal_summary"), "")
    if summary and "unavailable" not in summary.lower():
        return [summary]
    return ["Insufficient causal-chain evidence in current state."]


def _competing_hypotheses(state: Mapping[str, Any], latest_forecast: Mapping[str, Any]) -> list[str]:
    distribution = _mapping(
        _mapping(state.get("last_decision_packet")).get("causal_hypothesis_score_distribution")
    )
    if distribution:
        return [str(key) for key, _ in sorted(distribution.items(), key=lambda pair: pair[1], reverse=True)[:3]]
    active = _text(latest_forecast.get("active_hypothesis"), "")
    if active:
        return ["No competing hypothesis exposed by current state."]
    return ["Insufficient hypothesis evidence."]


def _recent_hypothesis_change(state: Mapping[str, Any]) -> str:
    self_org = _mapping(state.get("self_organization_state"))
    shift = self_org.get("structural_shift_index") or _mapping(state.get("structural_coevolution_state")).get("structural_shift_index")
    if shift is None:
        return "No recent hypothesis change exposed."
    return f"Structural shift index {shift}"


def _confidence_components(state: Mapping[str, Any], ledger: Mapping[str, Any]) -> list[dict[str, Any]]:
    market = _mapping(state.get("market_intelligence"))
    channels = _mapping(market.get("channels"))
    total = max(1, len(channels))
    live_or_sim = sum(1 for value in channels.values() if _text(value, "").upper() in {"LIVE", "SIMULATED", "CACHED", "DELAYED"})
    trust = _safe_float(state.get("trust_index"), 0.0)
    portfolio = _mapping(state.get("portfolio_context"))
    relevance = _safe_float(_mapping(portfolio.get("exposure_map")).get("portfolio_relevance_score"), 0.0) / 100.0
    metrics = _mapping(ledger.get("metrics"))
    evaluated = _safe_float(metrics.get("evaluated"), 0.0)
    return [
        {"name": "evidence_quality", "value": round(min(1.0, live_or_sim / total), 4), "source": "market channel status"},
        {"name": "market_data_completeness", "value": round(min(1.0, live_or_sim / total), 4), "source": "market_intelligence.channels"},
        {"name": "hypothesis_stability", "value": round(max(0.0, min(1.0, trust)), 4), "source": "system_trust_state"},
        {"name": "portfolio_relevance", "value": round(max(0.0, min(1.0, relevance)), 4), "source": "portfolio_context"},
        {"name": "forecast_history", "value": round(min(1.0, evaluated / 20.0), 4), "source": "forecast_ledger"},
    ]


def _data_quality_limitation(live: int, simulated: int, missing: int, stale: int) -> str:
    if missing or stale:
        return "Confidence is limited by missing, stale, or unconfigured market channels."
    if simulated:
        return "Confidence is limited because some channels are simulated."
    if live:
        return "Live channels are available, but forecast outcomes still need accumulation."
    return "Confidence is limited because no market channels are currently available."


def _compact_mapping(value: Mapping[str, Any]) -> dict[str, Any]:
    keys = (
        "status",
        "bounded",
        "trust_gate",
        "structural_shift_index",
        "mutation_intensity",
        "graph_edge_count",
        "graph_node_count",
        "no_node_creation",
        "no_topology_rewrite",
    )
    return {key: value.get(key) for key in keys if key in value}


def _safe_confidence(value: Any) -> float:
    return round(max(0.0, min(1.0, _safe_float(value, 0.0))), 4)


def _safe_float(value: Any, fallback: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return fallback
    if number > 1:
        number /= 100
    return number


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def _text(value: Any, fallback: str) -> str:
    if value is None:
        return fallback
    text = str(value).replace("\x00", " ").strip()
    if not text or text.lower() in {"none", "null"}:
        return fallback
    return text
