"""Forecast ledger for Atlas prediction accountability.

The ledger records non-binding market-structure forecasts and later compares
them with observed outcomes. It is not a price-target engine and does not
create trading authority.
"""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from pathlib import Path
from typing import Any, Mapping

try:
    from runtime.logging import utc_now_iso
    from runtime.state_store import DEFAULT_DB_PATH
except ModuleNotFoundError:  # pragma: no cover
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from runtime.logging import utc_now_iso
    from runtime.state_store import DEFAULT_DB_PATH


FORECAST_STATUSES = {"OPEN", "MATURED", "VERIFIED", "INVALIDATED", "INCONCLUSIVE"}


def create_forecast(payload: Mapping[str, Any], *, db_path: str | None = None) -> dict[str, Any]:
    """Persist one forecast after schema normalization."""

    now = utc_now_iso()
    forecast_id = str(payload.get("forecast_id") or f"forecast-{uuid.uuid4()}")
    if get_forecast(forecast_id, db_path=db_path):
        return {"status": "error", "error": "forecast_already_exists", "forecast_id": forecast_id}
    record = {
        "forecast_id": forecast_id,
        "created_at": str(payload.get("created_at") or now),
        "horizon": _text(payload.get("horizon"), "unspecified"),
        "subject": _text(payload.get("subject"), "market_structure"),
        "forecast_statement": _text(payload.get("forecast_statement") or payload.get("statement"), "Data Missing"),
        "expected_direction_state": _text(payload.get("expected_direction_state") or payload.get("expected_direction"), "Unknown"),
        "confidence": _confidence(payload.get("confidence")),
        "active_hypothesis": _text(payload.get("active_hypothesis"), "Unknown"),
        "causal_drivers": _list(payload.get("causal_drivers")),
        "invalidation_conditions": _list(payload.get("invalidation_conditions")),
        "expected_observation_window": _text(payload.get("expected_observation_window"), "Unknown"),
        "actual_outcome": _text(payload.get("actual_outcome"), ""),
        "outcome_timestamp": _text(payload.get("outcome_timestamp"), ""),
        "matured_at": "",
        "maturity_evidence": {},
        "prediction_error": None,
        "forecast_error": None,
        "calibration_error": None,
        "explanation_error": {},
        "hypothesis_evaluation": {},
        "trust_update": {},
        "runtime_lineage": _mapping(payload.get("runtime_lineage")),
        "material_signature": _text(payload.get("material_signature"), ""),
        "material_reason": _text(payload.get("material_reason"), ""),
        "lineage": [
            {"event": "created", "timestamp": now, "status": "OPEN"},
        ],
        "status": "OPEN",
        "updated_at": now,
    }
    _write_record(record, db_path=db_path)
    return record


def list_forecasts(*, db_path: str | None = None, status: str | None = None, limit: int = 100) -> dict[str, Any]:
    """Return ledger rows and compact accountability metrics."""

    _ensure_schema(db_path)
    query = "SELECT record_json FROM forecast_ledger"
    params: list[Any] = []
    if status:
        query += " WHERE status = ?"
        params.append(status.upper())
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(int(limit))
    with _connect(db_path) as conn:
        rows = conn.execute(query, params).fetchall()
    forecasts = [json.loads(row["record_json"]) for row in rows]
    return {
        "timestamp": utc_now_iso(),
        "forecasts": forecasts,
        "metrics": ledger_metrics(forecasts),
        "sample_warning": _sample_warning(forecasts),
        "no_trading_execution": True,
    }


def evaluate_forecast(
    forecast_id: str,
    outcome: Mapping[str, Any],
    *,
    db_path: str | None = None,
) -> dict[str, Any]:
    """Evaluate one forecast against a realized state/outcome."""

    record = get_forecast(forecast_id, db_path=db_path)
    if not record:
        return {"status": "error", "error": "forecast_not_found", "forecast_id": forecast_id}
    current_status = str(record.get("status") or "").upper()
    if current_status != "MATURED":
        return {
            "status": "error",
            "error": "forecast_not_matured",
            "forecast_id": forecast_id,
            "current_status": current_status or "Unknown",
        }
    actual = _text(outcome.get("actual_outcome") or outcome.get("outcome"), "Unknown")
    expected = str(record.get("expected_direction_state") or "").strip().lower()
    actual_norm = actual.strip().lower()
    requested_status = str(outcome.get("status", "")).upper()
    if expected and expected != "unknown" and expected in actual_norm:
        status = "VERIFIED"
        error = 0.0
    elif requested_status in {"VERIFIED", "INVALIDATED", "INCONCLUSIVE"}:
        status = requested_status
        error = 0.5 if status == "INCONCLUSIVE" else 1.0
    else:
        status = "INCONCLUSIVE"
        error = 0.5
    confidence = _confidence(record.get("confidence"))
    calibration_error = round(abs(confidence - (1.0 - error)), 4)
    now = utc_now_iso()
    trust_update = _apply_runtime_calibration(record, status, error, db_path=db_path)
    lineage = list(record.get("lineage", [])) if isinstance(record.get("lineage"), list) else []
    lineage.append({"event": "evaluated", "timestamp": now, "status": status, "forecast_error": error})
    record.update(
        {
            "actual_outcome": actual,
            "outcome_timestamp": str(outcome.get("outcome_timestamp") or now),
            "prediction_error": error,
            "forecast_error": error,
            "calibration_error": calibration_error,
            "explanation_error": outcome.get("explanation_error", {}),
            "hypothesis_evaluation": _hypothesis_evaluation(record, status, error),
            "trust_update": trust_update,
            "lineage": lineage,
            "status": status,
            "updated_at": now,
        }
    )
    _write_record(record, db_path=db_path)
    return record


def mark_forecast_matured(
    forecast_id: str,
    evidence: Mapping[str, Any] | None = None,
    *,
    db_path: str | None = None,
) -> dict[str, Any]:
    """Mark a forecast as matured before final outcome evaluation."""

    record = get_forecast(forecast_id, db_path=db_path)
    if not record:
        return {"status": "error", "error": "forecast_not_found", "forecast_id": forecast_id}
    if record.get("status") != "OPEN":
        return record
    now = utc_now_iso()
    lineage = list(record.get("lineage", [])) if isinstance(record.get("lineage"), list) else []
    lineage.append({"event": "matured", "timestamp": now, "status": "MATURED"})
    record.update(
        {
            "status": "MATURED",
            "matured_at": now,
            "maturity_evidence": dict(evidence or {}),
            "updated_at": now,
            "lineage": lineage,
        }
    )
    _write_record(record, db_path=db_path)
    return record


def get_forecast(forecast_id: str, *, db_path: str | None = None) -> dict[str, Any]:
    _ensure_schema(db_path)
    with _connect(db_path) as conn:
        row = conn.execute("SELECT record_json FROM forecast_ledger WHERE forecast_id = ?", (forecast_id,)).fetchone()
    return json.loads(row["record_json"]) if row else {}


def latest_forecast(
    *,
    subject: str | None = None,
    status: str | None = None,
    db_path: str | None = None,
) -> dict[str, Any]:
    """Return the latest matching forecast without changing it."""

    _ensure_schema(db_path)
    clauses = []
    params: list[Any] = []
    if status:
        clauses.append("status = ?")
        params.append(status.upper())
    query = "SELECT record_json FROM forecast_ledger"
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY created_at DESC"
    with _connect(db_path) as conn:
        rows = conn.execute(query, params).fetchall()
    for row in rows:
        record = json.loads(row["record_json"])
        if subject is None or str(record.get("subject")) == subject:
            return record
    return {}


def process_due_runtime_forecast(
    *,
    current_state: str,
    current_cycle_id: str,
    event_ids: list[str],
    db_path: str | None = None,
) -> dict[str, Any]:
    """Close the latest prior-cycle one-step runtime forecast from later observed state."""

    forecast = latest_forecast(subject="runtime_market_structure", status="OPEN", db_path=db_path)
    if not forecast:
        return {"status": "not_available", "reason": "no_open_runtime_forecast"}
    lineage = _mapping(forecast.get("runtime_lineage"))
    if str(lineage.get("decision_brief_id") or "") == str(current_cycle_id or ""):
        return {"status": "not_due", "forecast_id": forecast.get("forecast_id")}
    matured = mark_forecast_matured(
        str(forecast.get("forecast_id")),
        {
            "reason": "next_runtime_cycle_observed",
            "current_cycle_id": current_cycle_id,
            "event_ids": event_ids,
            "observed_state": current_state,
        },
        db_path=db_path,
    )
    if matured.get("status") != "MATURED":
        return matured
    expected = str(matured.get("expected_direction_state") or "Unknown")
    if not current_state or current_state.lower() == "unknown":
        outcome_status = "INCONCLUSIVE"
    elif expected.strip().lower() == current_state.strip().lower():
        outcome_status = "VERIFIED"
    else:
        outcome_status = "INVALIDATED"
    evaluated = evaluate_forecast(
        str(matured.get("forecast_id")),
        {
            "actual_outcome": current_state or "Unknown",
            "status": outcome_status,
            "outcome_timestamp": utc_now_iso(),
            "explanation_error": {
                "source": "later_runtime_state",
                "expected_state": expected,
                "observed_state": current_state or "Unknown",
            },
        },
        db_path=db_path,
    )
    return {
        "status": evaluated.get("status"),
        "forecast_id": evaluated.get("forecast_id"),
        "expected_state": expected,
        "observed_state": current_state or "Unknown",
        "prediction_error": evaluated.get("prediction_error"),
        "calibration_error": evaluated.get("calibration_error"),
        "trust_update": evaluated.get("trust_update", {}),
    }


def ledger_metrics(forecasts: list[Mapping[str, Any]]) -> dict[str, Any]:
    evaluated = [item for item in forecasts if item.get("status") in {"VERIFIED", "INVALIDATED", "INCONCLUSIVE"}]
    verified = [item for item in evaluated if item.get("status") == "VERIFIED"]
    errors = [float(item.get("forecast_error")) for item in evaluated if item.get("forecast_error") is not None]
    calibration = [
        float(item.get("calibration_error")) for item in evaluated if item.get("calibration_error") is not None
    ]
    return {
        "total": len(forecasts),
        "open": sum(1 for item in forecasts if item.get("status") == "OPEN"),
        "matured": sum(1 for item in forecasts if item.get("status") == "MATURED"),
        "evaluated": len(evaluated),
        "verified": len(verified),
        "accuracy": round(len(verified) / len(evaluated), 4) if evaluated else None,
        "mean_forecast_error": round(sum(errors) / len(errors), 4) if errors else None,
        "mean_calibration_error": round(sum(calibration) / len(calibration), 4) if calibration else None,
        "minimum_sample_size_met": len(evaluated) >= 20,
    }


def _write_record(record: Mapping[str, Any], *, db_path: str | None = None) -> None:
    _ensure_schema(db_path)
    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO forecast_ledger (forecast_id, status, created_at, updated_at, record_json)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(forecast_id) DO UPDATE SET
                status = excluded.status,
                updated_at = excluded.updated_at,
                record_json = excluded.record_json
            """,
            (
                record["forecast_id"],
                record["status"],
                record["created_at"],
                record["updated_at"],
                json.dumps(record, ensure_ascii=False, sort_keys=True),
            ),
        )


def _ensure_schema(db_path: str | None) -> None:
    with _connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS forecast_ledger (
                forecast_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                record_json TEXT NOT NULL
            )
            """
        )


def _connect(db_path: str | None) -> sqlite3.Connection:
    configured = db_path or os.environ.get("ATLAS_RUNTIME_DB")
    path = Path(configured) if configured else DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _text(value: Any, fallback: str) -> str:
    text = str(value if value is not None else fallback).replace("\x00", " ").strip()
    return (text or fallback)[:1000]


def _list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).replace("\x00", " ").strip()[:300] for item in value if str(item).strip()]
    if isinstance(value, str):
        return [part.strip()[:300] for part in value.split(",") if part.strip()]
    return []


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _confidence(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if number > 1:
        number /= 100
    return round(max(0.0, min(1.0, number)), 4)


def _sample_warning(forecasts: list[Mapping[str, Any]]) -> str:
    evaluated = [item for item in forecasts if item.get("status") in {"VERIFIED", "INVALIDATED", "INCONCLUSIVE"}]
    if len(evaluated) < 20:
        return "Low sample size: calibration is directional only, not statistically reliable."
    return "Minimum sample size met for basic calibration review."


def _hypothesis_evaluation(record: Mapping[str, Any], status: str, error: float) -> dict[str, Any]:
    active = str(record.get("active_hypothesis") or "Unknown")
    if status == "VERIFIED":
        outcome = "supported"
    elif status == "INVALIDATED":
        outcome = "weakened"
    else:
        outcome = "inconclusive"
    return {
        "active_hypothesis": active,
        "outcome": outcome,
        "forecast_error": error,
        "metadata_only": True,
    }


def _apply_runtime_calibration(
    record: Mapping[str, Any],
    status: str,
    error: float,
    *,
    db_path: str | None = None,
) -> dict[str, Any]:
    try:
        from runtime.state_store import StateStore
    except ModuleNotFoundError:  # pragma: no cover
        return {"status": "not_applied", "reason": "state_store_unavailable"}

    store = StateStore(db_path=db_path)
    trust_state = store.get_state("system_trust_state")
    before = _confidence(trust_state.get("rolling_trust_index", 0.5))
    confidence = _confidence(record.get("confidence"))
    if status == "VERIFIED":
        delta = min(0.05, 0.02 + confidence * 0.03)
    elif status == "INVALIDATED":
        delta = -min(0.12, 0.04 + confidence * 0.08)
    else:
        delta = -min(0.04, 0.02 + error * 0.04)
    after = round(max(0.0, min(1.0, before + delta)), 4)
    updated_trust = {
        **trust_state,
        "rolling_trust_index": after,
        "trust_direction": "improving" if after >= before else "decaying",
        "trust_adjustment_reason": "forecast_outcome_calibration",
        "latest_forecast_calibration": {
            "forecast_id": record.get("forecast_id"),
            "status": status,
            "forecast_error": error,
            "delta": round(delta, 4),
        },
    }
    store.set_state("system_trust_state", updated_trust)

    calibration_state = store.get_state("forecast_calibration_state")
    count = int(calibration_state.get("evaluated_count", 0)) + 1
    previous_mean = float(calibration_state.get("mean_forecast_error", 0.0) or 0.0)
    mean_error = round(((previous_mean * (count - 1)) + error) / count, 4)
    store.set_state(
        "forecast_calibration_state",
        {
            **calibration_state,
            "evaluated_count": count,
            "mean_forecast_error": mean_error,
            "last_forecast_id": record.get("forecast_id"),
            "last_status": status,
            "minimum_sample_size_met": count >= 20,
        },
    )

    hypothesis_memory = store.get_state("causal_hypothesis_memory")
    history = list(hypothesis_memory.get("forecast_outcome_history", [])) if isinstance(hypothesis_memory.get("forecast_outcome_history"), list) else []
    history.append(
        {
            "forecast_id": record.get("forecast_id"),
            "active_hypothesis": record.get("active_hypothesis"),
            "status": status,
            "forecast_error": error,
        }
    )
    store.set_state(
        "causal_hypothesis_memory",
        {
            **hypothesis_memory,
            "forecast_outcome_history": history[-30:],
            "last_forecast_outcome": history[-1],
        },
    )
    return {
        "status": "applied",
        "rolling_trust_before": before,
        "rolling_trust_after": after,
        "delta": round(delta, 4),
        "bounded": True,
    }
