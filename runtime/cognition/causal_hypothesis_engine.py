"""Causal hypothesis generation for Atlas Runtime v0.7.

Explanations are represented as competing hypotheses, not truth claims. This
module generates deterministic structural variants only; it does not train,
predict, trade, or rewrite the core causal graph.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping


BASE_NODES = [
    "Attention",
    "Liquidity",
    "Price Momentum",
    "Volatility",
    "Narrative Pressure",
    "Institutional Flow",
    "Retail Flow",
]


def generate_causal_hypotheses(
    *,
    event_stream: Iterable[Mapping[str, Any]],
    regime_state: str,
    lmse_structure: Mapping[str, Any],
    explanation_error_history: Iterable[Mapping[str, Any]],
) -> Dict[str, Any]:
    """Generate multiple structurally different causal explanations."""

    events = list(event_stream or [])
    errors = list(explanation_error_history or [])
    regime = str(regime_state or "UNKNOWN").upper()
    latent = _as_mapping(lmse_structure.get("latent_variables"))
    attention = _score(latent.get("attention_persistence_field"), _event_pressure(events, "attention", 50.0))
    liquidity = _score(latent.get("structural_liquidity_pressure"), _event_pressure(events, "liquidity", 50.0))
    risk = _score(latent.get("hidden_risk_compression"), _event_pressure(events, "stress", 50.0))
    narrative = _score(latent.get("narrative_propagation_inertia"), _event_pressure(events, "narrative", 50.0))
    error_pressure = _avg_error(errors)

    templates = [
        {
            "id": "H_ATTENTION_FLOW",
            "extra_edges": [
                ("Narrative Pressure", "Attention", "narrative primes attention"),
                ("Attention", "Retail Flow", "attention converts into participation"),
                ("Retail Flow", "Price Momentum", "retail participation accelerates price"),
                ("Price Momentum", "Attention", "momentum feeds back into attention"),
            ],
            "assumptions": ["attention field persists", "retail flow is the marginal transmitter"],
            "evidence_terms": ["attention", "narrative", "retail"],
            "base": attention * 0.4 + narrative * 0.25 + error_pressure * 0.2,
        },
        {
            "id": "H_LIQUIDITY_STRESS",
            "extra_edges": [
                ("Institutional Flow", "Liquidity", "institutional depth controls liquidity"),
                ("Liquidity", "Volatility", "thin liquidity amplifies volatility"),
                ("Volatility", "Attention", "stress attracts attention"),
            ],
            "assumptions": ["liquidity is the hidden driver", "volatility is an amplification path"],
            "evidence_terms": ["liquidity", "volatility", "stress"],
            "base": liquidity * 0.35 + risk * 0.35 + error_pressure * 0.2,
        },
        {
            "id": "H_INSTITUTIONAL_ROTATION",
            "extra_edges": [
                ("Institutional Flow", "Liquidity", "institutional repositioning alters depth"),
                ("Institutional Flow", "Price Momentum", "rotation changes price pressure"),
                ("Price Momentum", "Retail Flow", "price confirms retail participation"),
            ],
            "assumptions": ["institutional flow leads", "retail flow reacts after price confirmation"],
            "evidence_terms": ["institutional", "liquidity", "momentum"],
            "base": liquidity * 0.25 + risk * 0.15 + (1.0 - attention) * 0.15 + error_pressure * 0.15,
        },
        {
            "id": "H_NARRATIVE_REFLEXIVITY",
            "extra_edges": [
                ("Narrative Pressure", "Attention", "narrative propagates attention"),
                ("Narrative Pressure", "Retail Flow", "narrative mobilizes retail flow"),
                ("Attention", "Volatility", "attention crowding expands volatility"),
            ],
            "assumptions": ["narrative is reflexive", "attention can amplify volatility without liquidity confirmation"],
            "evidence_terms": ["narrative", "attention", "volatility"],
            "base": narrative * 0.35 + attention * 0.25 + risk * 0.1,
        },
    ]
    hypotheses = []
    for template in templates:
        score = _regime_adjusted_confidence(template["base"], regime, template["id"])
        hypotheses.append(
            {
                "id": template["id"],
                "causal_graph_variant": _graph_variant(template["extra_edges"]),
                "confidence": round(max(0.05, min(0.95, score)), 4),
                "structural_assumptions": list(template["assumptions"]),
                "supporting_evidence": _supporting_evidence(events, template["evidence_terms"], errors),
                "structural_signature": _signature(template["extra_edges"]),
                "not_truth_claim": True,
            }
        )
    return {
        "hypotheses": hypotheses,
        "hypothesis_count": len(hypotheses),
        "multiple_explanations": len(hypotheses) >= 3,
        "metadata_only": True,
    }


def _graph_variant(edges: list[tuple[str, str, str]]) -> Dict[str, Any]:
    return {
        "nodes": BASE_NODES,
        "edges": [
            {"from": source, "to": target, "relationship": relation}
            for source, target, relation in edges
        ],
        "topology_rewrite_applied": False,
        "variant_only": True,
    }


def _supporting_evidence(
    events: list[Mapping[str, Any]],
    terms: list[str],
    errors: list[Mapping[str, Any]],
) -> list[str]:
    evidence: list[str] = []
    joined_terms = " ".join(terms).lower()
    for event in events[:6]:
        payload = event.get("payload", {}) if isinstance(event, Mapping) else {}
        text = f"{event.get('event_type', '')} {event.get('source', '')} {payload}".lower()
        if any(term in text for term in terms):
            evidence.append(str(event.get("event_type", "event_match")))
    for error in errors[-3:]:
        for factor in error.get("underestimated_factors", []):
            if str(factor).lower().split()[0] in joined_terms:
                evidence.append(f"underestimated:{factor}")
    return evidence[:6] or ["structural_prior"]


def _event_pressure(events: list[Mapping[str, Any]], key: str, default: float) -> float:
    values = []
    for event in events:
        payload = event.get("payload", {}) if isinstance(event, Mapping) else {}
        if isinstance(payload, Mapping):
            for name, value in payload.items():
                if key in str(name).lower():
                    values.append(_float(value, default))
    return sum(values) / len(values) if values else default


def _avg_error(errors: list[Mapping[str, Any]]) -> float:
    if not errors:
        return 0.2
    values = [_float(item.get("explanation_error_score"), 0.0) for item in errors[-6:]]
    return max(0.0, min(1.0, sum(values) / max(1, len(values))))


def _score(value: Any, fallback: float = 50.0) -> float:
    return max(0.0, min(1.0, _float(value, fallback) / 100.0))


def _regime_adjusted_confidence(base: float, regime: str, hypothesis_id: str) -> float:
    boost = 0.0
    if regime in {"HIGH_VOLATILITY", "RISK_OFF"} and hypothesis_id == "H_LIQUIDITY_STRESS":
        boost = 0.18
    elif regime == "ATTENTION_EXPANSION" and hypothesis_id in {"H_ATTENTION_FLOW", "H_NARRATIVE_REFLEXIVITY"}:
        boost = 0.12
    elif regime == "DISTRIBUTION" and hypothesis_id == "H_INSTITUTIONAL_ROTATION":
        boost = 0.12
    return 0.25 + base + boost


def _signature(edges: list[tuple[str, str, str]]) -> str:
    return "|".join(f"{source}->{target}" for source, target, _ in edges)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

