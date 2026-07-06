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
except ModuleNotFoundError:  # pragma: no cover
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from runtime.logging import utc_now_iso


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
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        return self.log_path

    def tail(self, limit: int = 3) -> list[Dict[str, Any]]:
        if not self.log_path.exists():
            return []
        lines = self.log_path.read_text(encoding="utf-8").splitlines()
        records = []
        for line in lines[-limit:]:
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                records.append({"timestamp": utc_now_iso(), "system_metrics": {"status": "invalid_log_record"}})
        return records


def read_runtime_log(log_path: Optional[str] = None, limit: int = 3) -> list[Dict[str, Any]]:
    return RuntimeOutputLogger(log_path=log_path).tail(limit=limit)
