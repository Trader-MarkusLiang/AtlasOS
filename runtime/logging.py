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

from runtime.telemetry.jsonl import append_jsonl, read_jsonl_tail


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
    safe_record = dict(record)
    safe_record.setdefault("logged_at", utc_now_iso())
    return append_jsonl(path, safe_record)


def read_log_records(log_path: Optional[str] = None, limit: int = 50) -> list[Dict[str, Any]]:
    """Read recent JSONL runtime records."""

    path = resolve_log_path(log_path)
    return read_jsonl_tail(path, limit)
