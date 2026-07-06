"""Append-only decision trace logger for Atlas runtime observability."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from runtime.logging import utc_now_iso
except ModuleNotFoundError:  # pragma: no cover
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from runtime.logging import utc_now_iso


DEFAULT_DECISION_TRACE_PATH = Path("runtime/logs/decision_traces.jsonl")


def log_decision_trace(
    *,
    tick: int,
    event: Any,
    regime_state: str,
    attention_state: Any,
    causal_summary: str,
    llm_decision_packet: Dict[str, Any],
    feedback_delta: Dict[str, Any],
    calibrated_confidence: Optional[float] = None,
    confidence_adjustment_factor: Optional[float] = None,
    log_path: Optional[str] = None,
) -> Path:
    """Append one decision trace and never raise to callers."""

    path = _resolve_path(log_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "timestamp": utc_now_iso(),
            "tick": int(tick),
            "event": event,
            "regime_state": str(regime_state or "Unknown"),
            "attention_state": attention_state,
            "causal_summary": str(causal_summary or "Unknown"),
            "llm_decision_packet": llm_decision_packet if isinstance(llm_decision_packet, dict) else {},
            "feedback_delta": {
                "attention": _number(feedback_delta.get("attention")) if isinstance(feedback_delta, dict) else 0,
                "causal": _number(feedback_delta.get("causal")) if isinstance(feedback_delta, dict) else 0,
                "risk": _number(feedback_delta.get("risk")) if isinstance(feedback_delta, dict) else 0,
            },
            "calibrated_confidence": _number(calibrated_confidence)
            if calibrated_confidence is not None
            else _number((llm_decision_packet or {}).get("confidence")),
            "confidence_adjustment_factor": _number(confidence_adjustment_factor)
            if confidence_adjustment_factor is not None
            else 1.0,
        }
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    except Exception:
        return path
    return path


def read_decision_traces(log_path: Optional[str] = None, limit: int = 100) -> list[Dict[str, Any]]:
    path = _resolve_path(log_path)
    if not path.exists():
        return []
    records: list[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines()[-limit:]:
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            records.append({"timestamp": utc_now_iso(), "status": "invalid_log_record"})
    return records


def _resolve_path(log_path: Optional[str]) -> Path:
    configured = log_path or os.environ.get("ATLAS_DECISION_TRACE_LOG")
    return Path(configured) if configured else DEFAULT_DECISION_TRACE_PATH


def _number(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
