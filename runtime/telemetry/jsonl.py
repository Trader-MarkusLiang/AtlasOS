"""Bounded JSONL IO shared by runtime telemetry writers and readers."""

from __future__ import annotations

import json
import os
from collections import deque
from pathlib import Path
from threading import Lock
from typing import Any, Mapping


DEFAULT_MAX_BYTES = 64 * 1024 * 1024
DEFAULT_BACKUP_COUNT = 5
_ROTATION_LOCK = Lock()


def read_jsonl_tail(path: Path, limit: int) -> list[dict[str, Any]]:
    """Read at most the final ``limit`` records without loading the file."""

    bounded = max(0, int(limit or 0))
    if bounded == 0 or not path.exists():
        return []
    lines: deque[str] = deque(maxlen=bounded)
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                if line.strip():
                    lines.append(line)
    except OSError:
        return []
    records: list[dict[str, Any]] = []
    for line in lines:
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            value = {"status": "invalid_log_record"}
        records.append(value if isinstance(value, dict) else {"status": "invalid_log_record"})
    return records


def append_jsonl(
    path: Path,
    record: Mapping[str, Any],
    *,
    max_bytes: int | None = None,
    backup_count: int | None = None,
) -> Path:
    """Append one record and rotate bounded backups before the write."""

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(dict(record), ensure_ascii=False, sort_keys=True) + "\n"
    limit = _positive_int(max_bytes, "ATLAS_TELEMETRY_MAX_BYTES", DEFAULT_MAX_BYTES)
    backups = _positive_int(backup_count, "ATLAS_TELEMETRY_BACKUPS", DEFAULT_BACKUP_COUNT)
    with _ROTATION_LOCK:
        try:
            if path.exists() and path.stat().st_size + len(payload.encode("utf-8")) > limit:
                _rotate(path, backups)
            with path.open("a", encoding="utf-8") as handle:
                handle.write(payload)
        except OSError:
            return path
    return path


def _rotate(path: Path, backup_count: int) -> None:
    if backup_count <= 0:
        path.unlink(missing_ok=True)
        return
    oldest = path.with_name(f"{path.name}.{backup_count}")
    oldest.unlink(missing_ok=True)
    for index in range(backup_count - 1, 0, -1):
        source = path.with_name(f"{path.name}.{index}")
        if source.exists():
            source.replace(path.with_name(f"{path.name}.{index + 1}"))
    if path.exists():
        path.replace(path.with_name(f"{path.name}.1"))


def _positive_int(value: int | None, env_name: str, fallback: int) -> int:
    candidate: Any = value if value is not None else os.environ.get(env_name, fallback)
    try:
        parsed = int(candidate)
    except (TypeError, ValueError):
        parsed = fallback
    return max(1, parsed)
