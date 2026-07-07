"""Run hostile cognition scenarios through the real DecisionLoop."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.decision_loop import DecisionLoop, DecisionLoopConfig  # noqa: E402
from runtime.event_stream import EventStream  # noqa: E402
from runtime.state_store import StateStore  # noqa: E402


SCENARIOS = {
    "market_crash_attention_spike": [
        ("market_anomaly", 95, {"index_drop_2h": -7, "liquidity": "contracting"}),
        ("attention_spike", 90, {"attention": "panic", "keywords": ["crash", "liquidity"]}),
        ("volatility_spike", 88, {"volatility": "high"}),
    ],
    "bullish_narrative_collapsing_liquidity": [
        ("news_narrative_spike", 75, {"headline": "bullish AI story", "narrative": "strong"}),
        ("liquidity_shock", 95, {"liquidity": "collapsing"}),
    ],
    "false_viral_rumor": [
        ("news_narrative_spike", 80, {"headline": "unverified viral rumor", "source_quality": "low"}),
        ("attention_spike", 85, {"attention": "viral"}),
    ],
    "strong_price_weak_breadth": [
        ("volume_price_breakout", 82, {"price": "up", "breadth": "weak"}),
        ("market_anomaly", 70, {"breadth": "weak"}),
    ],
    "conflicting_macro_micro": [
        ("market_anomaly", 74, {"macro": "tightening"}),
        ("volume_price_breakout", 78, {"micro": "strong"}),
    ],
    "stale_bullish_fresh_bearish": [
        ("news_narrative_spike", 55, {"headline": "old bullish data", "freshness": "stale"}),
        ("liquidity_shock", 93, {"freshness": "fresh", "liquidity": "down"}),
    ],
    "llm_contradicts_deterministic": [
        ("market_anomaly", 90, {"deterministic": "stress"}),
        ("news_narrative_spike", 60, {"llm_claim": "certain bullish outcome"}),
    ],
    "portfolio_exposed_failing_theme": [
        ("portfolio_drawdown", 100, {"theme": "AI Hardware", "drawdown": "high"}),
        ("liquidity_shock", 90, {"liquidity": "thin"}),
    ],
    "hypothesis_oscillation": [
        ("attention_spike", 80, {"attention": "high"}),
        ("liquidity_shock", 80, {"liquidity": "low"}),
        ("volume_price_breakout", 80, {"price": "up"}),
    ],
    "trust_collapse": [
        ("volatility_spike", 90, {"volatility": "extreme"}),
        ("market_anomaly", 90, {"contradiction": "high"}),
    ],
}


def main() -> None:
    results = {}
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for name, events in SCENARIOS.items():
            db_path = str(root / f"{name}.sqlite")
            log_path = str(root / f"{name}.jsonl")
            inbox = str(root / f"{name}_inbox")
            stream = EventStream(db_path=db_path, inbox_dir=inbox)
            for event_type, priority, payload in events:
                stream.enqueue_event(event_type, priority=priority, payload=payload, source="adversarial_fixture")
            loop = DecisionLoop(
                DecisionLoopConfig(
                    db_path=db_path,
                    log_path=log_path,
                    inbox_dir=inbox,
                    heartbeat_interval_seconds=999999,
                    max_events_per_cycle=10,
                    sleep_interval_seconds=0,
                )
            )
            cycle = loop.run_once()
            store = StateStore(db_path=db_path)
            latest = store.get_latest_decision_brief()
            content = latest.get("content", "")
            cognition = store.get_state("cognition_state")
            assert cycle["status"] == "success"
            assert cycle["raw_events_processed"] >= 1
            assert "Buy" not in content and "Sell" not in content
            trust = store.get_state("system_trust_state")
            structural = store.get_state("structural_coevolution_state")
            results[name] = {
                "state": store.get_system_state().get("current_state"),
                "transition_allowed": store.get_system_state().get("transition_allowed"),
                "decision_brief_available": bool(content),
                "trust": trust.get("rolling_trust_index"),
                "structural_status": structural.get("status"),
                "primary_driver": cognition.get("causal", {}).get("primary_driver"),
            }
    print(json.dumps({"status": "PASS", "scenarios": results}, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
