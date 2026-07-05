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
                """
            )

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
