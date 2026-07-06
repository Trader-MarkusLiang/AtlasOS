"""Regime topology overlay for Atlas Runtime v0.4.

Regimes are represented as deformable attractor basins. This module reads
existing latent structure and trust metadata, then emits a bounded topology
overlay without changing LMSE or state-controller internals.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping


LOW_TRUST_THRESHOLD = 0.35
MAX_ATTRACTOR_SHIFT = 0.06
MAX_BASIN_DEFORMATION = 0.08


def evolve_regime_topology(
    *,
    latent_structure: Mapping[str, Any],
    mutation_state: Mapping[str, Any],
    trust_score: Mapping[str, Any],
    feedback_delta: Mapping[str, Any],
    previous_topology: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Return trust-sensitive regime topology metadata."""

    trust = _clamp01(_float(trust_score.get("global_trust_index"), 0.5))
    previous = previous_topology if isinstance(previous_topology, Mapping) else {}
    if trust < LOW_TRUST_THRESHOLD:
        return {
            "attractor_shift": 0.0,
            "basin_deformation": 0.0,
            "transition_barriers": dict(previous.get("transition_barriers", {})),
            "stability_landscape": dict(previous.get("stability_landscape", {})),
            "status": "frozen",
            "reason": "low_trust_freeze",
            "trust_gate": "closed",
            "global_trust_index": round(trust, 4),
            "bounded": True,
        }

    attractors = _as_mapping(latent_structure.get("regime_attractors"))
    basins = _as_mapping(attractors.get("basins"))
    latent = _as_mapping(latent_structure.get("latent_variables"))
    phase = _as_mapping(latent_structure.get("phase_space_geometry"))
    feedback = _feedback_magnitude(feedback_delta)
    mutation_intensity = _float(mutation_state.get("mutation_intensity"), 0.0)
    trust_window = max(0.0, trust - LOW_TRUST_THRESHOLD) / (1.0 - LOW_TRUST_THRESHOLD)

    basin_gap = _basin_strength_gap(basins)
    curvature = _float(phase.get("phase_curvature"), 0.0) / 100.0
    liquidity_attention_spread = abs(
        _float(latent.get("attention_persistence_field"), 0.0)
        - _float(latent.get("structural_liquidity_pressure"), 0.0)
    ) / 100.0

    attractor_shift = round(
        min(MAX_ATTRACTOR_SHIFT, (1.0 - basin_gap) * mutation_intensity * 0.8 + feedback * 0.05) * trust_window,
        4,
    )
    basin_deformation = round(
        min(MAX_BASIN_DEFORMATION, (curvature * 0.04 + liquidity_attention_spread * 0.04 + mutation_intensity))
        * trust_window,
        4,
    )
    transition_barriers = {
        name: _barrier_from_basin(value, basin_deformation)
        for name, value in basins.items()
        if isinstance(value, Mapping)
    }
    stability_landscape = {
        "dominant_attractor_basin": attractors.get("dominant_attractor_basin", "unknown"),
        "basin_gap": round(basin_gap, 4),
        "phase_curvature": int(_float(phase.get("phase_curvature"), 0.0)),
        "liquidity_attention_spread": round(liquidity_attention_spread, 4),
        "trust_sensitive": True,
        "label_override": False,
    }
    return {
        "attractor_shift": attractor_shift,
        "basin_deformation": basin_deformation,
        "transition_barriers": transition_barriers,
        "stability_landscape": stability_landscape,
        "status": "evolved" if basin_deformation or attractor_shift else "stable",
        "trust_gate": "open",
        "global_trust_index": round(trust, 4),
        "bounded": True,
    }


def _basin_strength_gap(basins: Mapping[str, Any]) -> float:
    strengths = sorted(
        (_float(value.get("attractor_strength"), 0.0) for value in basins.values() if isinstance(value, Mapping)),
        reverse=True,
    )
    if len(strengths) < 2:
        return 1.0
    return max(0.0, min(1.0, (strengths[0] - strengths[1]) / 100.0))


def _barrier_from_basin(basin: Mapping[str, Any], deformation: float) -> float:
    strength = _float(basin.get("attractor_strength"), 0.0)
    depth = _float(basin.get("basin_depth"), basin.get("transition_barrier", 50.0))
    raw = (depth * 0.6 + strength * 0.4) / 100.0 - deformation
    return round(max(0.0, min(1.0, raw)), 4)


def _feedback_magnitude(feedback_delta: Mapping[str, Any]) -> float:
    values: list[float] = []
    for value in (feedback_delta if isinstance(feedback_delta, Mapping) else {}).values():
        if isinstance(value, Mapping):
            values.extend(abs(_float(item, 0.0)) for item in value.values())
        else:
            values.append(abs(_float(value, 0.0)))
    return max(values, default=0.0)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))
