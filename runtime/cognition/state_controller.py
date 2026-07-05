"""Anti-overwrite state controller for Atlas Runtime v0.3."""

from __future__ import annotations

from typing import Any, Dict

try:
    from runtime.logging import utc_now_iso
except ModuleNotFoundError:  # pragma: no cover
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from runtime.logging import utc_now_iso


RISK_STATES = {"CRASH_STRESS", "RISK_OFF", "HIGH_VOLATILITY", "DISTRIBUTION"}


class AntiOverwriteStateController:
    """Validate state transitions against memory and stability thresholds."""

    def __init__(self, stability_threshold: int = 55, crash_cooldown_cycles: int = 3) -> None:
        self.stability_threshold = stability_threshold
        self.crash_cooldown_cycles = crash_cooldown_cycles

    def decide(
        self,
        previous_state: str,
        fusion: Dict[str, Any],
        memory_summary: Dict[str, Any],
        causal: Dict[str, Any],
    ) -> Dict[str, Any]:
        proposed = fusion.get("proposed_state", "NORMAL")
        stability = int(fusion.get("stability_score", 0))
        dominant = memory_summary.get("dominant_state", previous_state)
        weighted_scores = memory_summary.get("weighted_scores", {})

        final_state = proposed
        reason = "Proposed state accepted from fused market reality."
        transition_allowed = True

        crash_memory = weighted_scores.get("CRASH_STRESS", 0)
        high_vol_memory = weighted_scores.get("HIGH_VOLATILITY", 0)

        if dominant == "CRASH_STRESS" and proposed == "ATTENTION_EXPANSION":
            final_state = "CRASH_STRESS"
            transition_allowed = False
            reason = "Crash memory cooldown blocks attention overwrite."
        elif previous_state in {"HIGH_VOLATILITY", "RISK_OFF", "CRASH_STRESS"} and proposed == "ATTENTION_EXPANSION":
            if fusion.get("stress_score", 0) >= 45 or causal.get("primary_driver") in {"Liquidity Stress", "Market Stress"}:
                final_state = previous_state
                transition_allowed = False
                reason = "Risk state cannot be overwritten by attention without validation."
        elif proposed not in RISK_STATES and (crash_memory >= 0.9 or high_vol_memory >= 1.2):
            final_state = dominant if dominant in RISK_STATES else previous_state
            transition_allowed = False
            reason = "Weighted regime memory keeps risk state active."
        elif stability < self.stability_threshold and proposed != previous_state:
            final_state = previous_state
            transition_allowed = False
            reason = "Transition stability below threshold."

        return {
            "previous_state": previous_state,
            "proposed_state": proposed,
            "current_state": final_state,
            "transition_allowed": transition_allowed,
            "reason": reason,
            "stability_score": stability,
            "memory_dominant_state": dominant,
            "causal_primary_driver": causal.get("primary_driver", "Unknown"),
            "confidence": "Medium" if transition_allowed else "Low",
            "updated_at": utc_now_iso(),
        }
