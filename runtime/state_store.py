"""SQLite state store for Atlas OS lightweight runtime.

The store keeps runtime state and redacted portfolio metadata only. It must not
store private account values, costs, balances, net worth, or position amounts.
"""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from runtime.logging import utc_now_iso
except ModuleNotFoundError:  # pragma: no cover
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from runtime.logging import utc_now_iso


DEFAULT_DB_PATH = Path("runtime/state/atlas_runtime.sqlite")


class StateStore:
    """Small SQLite wrapper for runtime state."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        configured = db_path or os.environ.get("ATLAS_RUNTIME_DB")
        self.db_path = Path(configured) if configured else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS kv_state (
                    key TEXT PRIMARY KEY,
                    value_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS decision_briefs (
                    id TEXT PRIMARY KEY,
                    trigger_type TEXT NOT NULL,
                    event_type TEXT,
                    content TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS attention_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    signal_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    record_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE NOT NULL,
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    source TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS state_transitions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transition_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )

    def ensure_event_schema(self) -> None:
        self._init_schema()

    def set_state(self, key: str, value: Dict[str, Any]) -> None:
        now = utc_now_iso()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO kv_state (key, value_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value_json = excluded.value_json,
                    updated_at = excluded.updated_at
                """,
                (key, json.dumps(value, ensure_ascii=False, sort_keys=True), now),
            )

    def get_state(self, key: str) -> Dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute("SELECT value_json FROM kv_state WHERE key = ?", (key,)).fetchone()
        if not row:
            return {}
        return json.loads(row["value_json"])

    def save_portfolio_snapshot(self, snapshot: Dict[str, Any]) -> None:
        redacted = dict(snapshot)
        redacted["privacy"] = redacted.get("privacy", "redacted")
        redacted.pop("amount", None)
        redacted.pop("cost", None)
        redacted.pop("balance", None)
        redacted.pop("net_worth", None)
        self.set_state("portfolio_snapshot", redacted)

    def get_latest_portfolio_snapshot(self) -> Dict[str, Any]:
        return self.get_state("portfolio_snapshot")

    def save_regime_state(self, state: Dict[str, Any]) -> None:
        self.set_state("regime_state", state)

    def get_regime_state(self) -> Dict[str, Any]:
        return self.get_state("regime_state")

    def save_system_state(self, state: Dict[str, Any]) -> None:
        self.set_state("system_state", state)

    def get_system_state(self) -> Dict[str, Any]:
        return self.get_state("system_state")

    def append_attention_signal(self, signal: Dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO attention_history (signal_json, created_at) VALUES (?, ?)",
                (json.dumps(signal, ensure_ascii=False, sort_keys=True), utc_now_iso()),
            )

    def get_attention_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT signal_json, created_at FROM attention_history ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {"created_at": row["created_at"], **json.loads(row["signal_json"])}
            for row in rows
        ]

    def save_decision_brief(
        self,
        brief_id: str,
        trigger_type: str,
        event_type: Optional[str],
        content: str,
        metadata: Dict[str, Any],
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO decision_briefs
                    (id, trigger_type, event_type, content, metadata_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    brief_id,
                    trigger_type,
                    event_type,
                    content,
                    json.dumps(metadata, ensure_ascii=False, sort_keys=True),
                    utc_now_iso(),
                ),
            )

    def get_latest_decision_brief(self) -> Dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT id, trigger_type, event_type, content, metadata_json, created_at
                FROM decision_briefs
                ORDER BY created_at DESC
                LIMIT 1
                """
            ).fetchone()
        if not row:
            return {}
        return {
            "id": row["id"],
            "trigger_type": row["trigger_type"],
            "event_type": row["event_type"],
            "content": row["content"],
            "metadata": json.loads(row["metadata_json"]),
            "created_at": row["created_at"],
        }

    def append_system_log(self, record: Dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO system_logs (record_json, created_at) VALUES (?, ?)",
                (json.dumps(record, ensure_ascii=False, sort_keys=True), utc_now_iso()),
            )

    def get_system_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT record_json, created_at FROM system_logs ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [{"created_at": row["created_at"], **json.loads(row["record_json"])} for row in rows]

    def append_event(self, event: Dict[str, Any], status: str = "pending") -> None:
        now = utc_now_iso()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO events
                    (event_id, event_type, payload_json, priority, source, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event["event_id"],
                    event["event_type"],
                    json.dumps(event.get("payload", {}), ensure_ascii=False, sort_keys=True),
                    int(event.get("priority", 50)),
                    event.get("source", "runtime"),
                    status,
                    event.get("created_at", now),
                    now,
                ),
            )

    def get_pending_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT event_id, event_type, payload_json, priority, source, status, created_at, updated_at
                FROM events
                WHERE status = 'pending'
                ORDER BY priority DESC, created_at ASC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [_event_row_to_dict(row) for row in rows]

    def update_event_status(self, event_id: str, status: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE events SET status = ?, updated_at = ? WHERE event_id = ?",
                (status, utc_now_iso(), event_id),
            )

    def get_event_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT event_id, event_type, payload_json, priority, source, status, created_at, updated_at
                FROM events
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [_event_row_to_dict(row) for row in rows]

    def append_state_transition(self, transition: Dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO state_transitions (transition_json, created_at) VALUES (?, ?)",
                (json.dumps(transition, ensure_ascii=False, sort_keys=True), utc_now_iso()),
            )

    def get_state_transitions(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT transition_json, created_at FROM state_transitions ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {"created_at": row["created_at"], **json.loads(row["transition_json"])}
            for row in rows
        ]

    def query_series(self, table: str, limit: int = 50) -> List[Dict[str, Any]]:
        allowed = {
            "events": self.get_event_history,
            "state_transitions": self.get_state_transitions,
            "attention_history": self.get_attention_history,
            "system_logs": self.get_system_logs,
        }
        if table not in allowed:
            raise ValueError(f"unsupported time-series table: {table}")
        return allowed[table](limit=limit)


def _event_row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "event_id": row["event_id"],
        "event_type": row["event_type"],
        "payload": json.loads(row["payload_json"]),
        "priority": row["priority"],
        "source": row["source"],
        "status": row["status"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }
