"""JSONL output logger for Atlas runtime daemon ticks.

Logs runtime metadata and cognition summaries only. It must not store private
portfolio values, account balances, costs, trade orders, or broker data.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

try:
    from runtime.logging import utc_now_iso
    from runtime.telemetry.jsonl import append_jsonl, read_jsonl_tail
except ModuleNotFoundError:  # pragma: no cover
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from runtime.logging import utc_now_iso
    from runtime.telemetry.jsonl import append_jsonl, read_jsonl_tail


DEFAULT_OUTPUT_LOG_PATH = Path("runtime/logs/atlas_runtime.log")


class RuntimeOutputLogger:
    """Append daemon tick records as JSON lines."""

    def __init__(self, log_path: Optional[str] = None) -> None:
        self.log_path = Path(log_path) if log_path else DEFAULT_OUTPUT_LOG_PATH
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_tick(self, entry: Dict[str, Any]) -> Path:
        record = {
            "timestamp": entry.get("timestamp", utc_now_iso()),
            "event": entry.get("event", {}),
            "cognition_summary": entry.get("cognition_summary", {}),
            "regime_state": entry.get("regime_state", {}),
            "decision_brief": entry.get("decision_brief", {}),
            "system_metrics": entry.get("system_metrics", {}),
        }
        append_jsonl(self.log_path, record)
        return self.log_path

    def tail(self, limit: int = 3) -> list[Dict[str, Any]]:
        return read_jsonl_tail(self.log_path, limit)


def read_runtime_log(log_path: Optional[str] = None, limit: int = 3) -> list[Dict[str, Any]]:
    return RuntimeOutputLogger(log_path=log_path).tail(limit=limit)
