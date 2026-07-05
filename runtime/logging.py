"""Minimal JSONL runtime logging for Atlas OS.

This module records runtime execution metadata only. It does not store private
portfolio values, trading orders, costs, balances, or account amounts.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_LOG_PATH = Path("runtime/logs/runtime_runs.jsonl")


def utc_now_iso() -> str:
    """Return an ISO timestamp for runtime records."""

    return datetime.now(timezone.utc).isoformat()


def resolve_log_path(log_path: Optional[str] = None) -> Path:
    """Resolve explicit, environment, or default runtime log path."""

    configured = log_path or os.environ.get("ATLAS_RUNTIME_LOG")
    return Path(configured) if configured else DEFAULT_LOG_PATH


def log_execution(record: Dict[str, Any], log_path: Optional[str] = None) -> Path:
    """Append one runtime record to a JSONL file and return its path."""

    path = resolve_log_path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    safe_record = dict(record)
    safe_record.setdefault("logged_at", utc_now_iso())
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(safe_record, ensure_ascii=False, sort_keys=True) + "\n")
    return path

