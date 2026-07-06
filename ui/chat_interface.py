"""Minimal chat interface boundary for Atlas UI v0.1.

User queries are written as sanitized `user_input_event` files for the runtime
inbox. The UI does not call cognition modules or mutate cognitive state.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from runtime.logging import utc_now_iso
from runtime.state_store import StateStore


DEFAULT_INBOX_DIR = Path("runtime/events/inbox")


def submit_query(
    query: str,
    *,
    inbox_dir: Optional[str] = None,
    source: str = "ui.chat_interface",
) -> Dict[str, Any]:
    """Submit a natural-language query through the runtime event inbox."""

    clean_query = _sanitize_text(query)
    if not clean_query:
        raise ValueError("query is empty after sanitization")

    path = _inbox_path(inbox_dir)
    path.mkdir(parents=True, exist_ok=True)
    event_id = f"ui-query-{uuid.uuid4()}"
    event = {
        "event_type": "user_input_event",
        "source": source,
        "created_at": utc_now_iso(),
        "priority": 60,
        "payload": {
            "query": clean_query,
            "interface": "chat",
            "read_only_request": True,
            "no_cognition_direct_call": True,
        },
    }
    event_file = path / f"{event_id}.json"
    event_file.write_text(json.dumps(event, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    return {
        "status": "queued",
        "event_id": event_id,
        "event_file": str(event_file),
        "message": "Query queued for Atlas runtime processing.",
    }


def latest_decision_packet(*, db_path: Optional[str] = None) -> Dict[str, Any]:
    """Return the latest runtime DecisionPacket for display."""

    latest = StateStore(db_path=db_path).get_latest_decision_brief()
    metadata = latest.get("metadata", {}) if isinstance(latest, dict) else {}
    packet = metadata.get("decision_packet", {}) if isinstance(metadata, dict) else {}
    return {
        "decision_brief_id": latest.get("id"),
        "created_at": latest.get("created_at"),
        "decision_packet": packet if isinstance(packet, dict) else {},
    }


def chat(query: str, *, inbox_dir: Optional[str] = None, db_path: Optional[str] = None) -> Dict[str, Any]:
    """Queue a query and return the current display state."""

    submission = submit_query(query, inbox_dir=inbox_dir)
    return {
        "submission": submission,
        "latest_decision": latest_decision_packet(db_path=db_path),
        "system_view": current_chat_system_view(db_path=db_path),
    }


def current_chat_system_view(*, db_path: Optional[str] = None) -> Dict[str, Any]:
    store = StateStore(db_path=db_path)
    cognition = store.get_state("cognition_state")
    trust = store.get_state("system_trust_state")
    self_organization = store.get_state("self_organization_state")
    system_state = store.get_system_state()
    return {
        "regime_state": system_state.get("current_state", "Unknown"),
        "proposed_state": system_state.get("proposed_state", "Unknown"),
        "trust_score": trust.get("latest_trust_score", {}),
        "rolling_trust_index": trust.get("rolling_trust_index"),
        "attention_state": cognition.get("fusion", {}).get("attention_pressure"),
        "liquidity_state": cognition.get("fusion", {}).get("liquidity_score"),
        "trust_field": self_organization.get("trust_field_state", {}).get("trust_field", {}),
    }


def render_chat_command_center() -> str:
    """Render the center command surface without calling cognition."""

    return """
    <main class="panel center-panel" data-component="chat-command-center">
      <div class="panel-header">
        <span class="panel-kicker">Command</span>
        <h2>Chat + Decision View</h2>
      </div>
      <section class="decision-card">
        <div class="decision-topline">
          <span id="decision-action" class="decision-action">neutral</span>
          <span id="decision-confidence" class="decision-confidence">Confidence 0.00</span>
        </div>
        <div class="decision-grid">
          <div><span>Risk</span><strong id="decision-risk">unknown</strong></div>
          <div><span>Attention</span><strong id="decision-attention">Unknown</strong></div>
          <div><span>Liquidity</span><strong id="decision-liquidity">Unknown</strong></div>
        </div>
        <p id="decision-summary" class="decision-summary">Waiting for DecisionPacket.</p>
      </section>
      <section class="chat-console">
        <div id="chat-messages" class="chat-messages" aria-live="polite"></div>
        <form id="chat-form" class="chat-form">
          <textarea id="chat-input" name="message" rows="3" maxlength="2000" placeholder="Send a runtime-safe Atlas query"></textarea>
          <button class="control-button" type="submit">Send</button>
        </form>
      </section>
    </main>
    """


def _inbox_path(inbox_dir: Optional[str]) -> Path:
    return Path(inbox_dir) if inbox_dir else DEFAULT_INBOX_DIR


def _sanitize_text(value: str) -> str:
    text = str(value or "").replace("\x00", " ").strip()
    return text[:2000]
