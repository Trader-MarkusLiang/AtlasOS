"""Append-only LLM trace logger for Atlas runtime observability.

Telemetry must never block runtime execution. All write/read helpers are
best-effort and avoid storing API keys or environment secrets.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

try:
    from runtime.logging import utc_now_iso
    from runtime.telemetry.jsonl import append_jsonl, read_jsonl_tail
except ModuleNotFoundError:  # pragma: no cover
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from runtime.logging import utc_now_iso
    from runtime.telemetry.jsonl import append_jsonl, read_jsonl_tail


DEFAULT_LLM_TRACE_PATH = Path("runtime/logs/llm_traces.jsonl")
_SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_\-]{8,}"),
    re.compile(r"Bearer\s+[A-Za-z0-9_\-\.]{8,}", re.IGNORECASE),
    re.compile(r"(?i)(api[_-]?key|token|secret)['\"]?\s*[:=]\s*['\"][^'\"]+['\"]"),
]


def log_llm_trace(
    *,
    provider: str,
    model: str,
    prompt: str,
    context: Dict[str, Any],
    output_raw: str,
    latency_ms: int,
    decision_packet_id: str = "",
    feedback_applied: bool = False,
    task_role: str = "legacy",
    started_at: str = "",
    completed_at: str = "",
    status: str = "unknown",
    error: str = "",
    fallback_attempts: Any = None,
    trigger_type: str = "unknown",
    usage: Mapping[str, Any] | None = None,
    estimated_cost: float | str = "Unknown",
    cost_status: str = "Unknown",
    cache_status: str = "unknown",
    log_path: Optional[str] = None,
) -> Path:
    """Append one LLM trace record and never raise to callers."""

    path = _resolve_path(log_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        prompt_text = str(prompt or "")
        prompt_hash = hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()
        previous_outputs = _previous_outputs(path, prompt_hash)
        output_text = _mask_secrets(str(output_raw or ""))
        output_stability_score = _output_stability_score(output_text, previous_outputs)
        normalized_usage = _normalize_usage(usage)
        record = {
            "timestamp": utc_now_iso(),
            "started_at": str(started_at or "Unknown"),
            "completed_at": str(completed_at or "Unknown"),
            "task_role": str(task_role or "legacy"),
            "provider": str(provider or "unknown"),
            "model": str(model or "unknown"),
            "prompt_hash": prompt_hash,
            "input_summary": _summarize_context(context),
            "output_raw": output_text,
            "latency_ms": int(latency_ms),
            "decision_packet_id": str(decision_packet_id or ""),
            "feedback_applied": bool(feedback_applied),
            "status": str(status or "unknown"),
            "error": _mask_secrets(str(error or ""))[:240],
            "fallback_attempts": _safe_fallback_attempts(fallback_attempts),
            "trigger_type": str(trigger_type or "unknown")[:120],
            "input_tokens": normalized_usage["input_tokens"],
            "output_tokens": normalized_usage["output_tokens"],
            "total_tokens": normalized_usage["total_tokens"],
            "estimated_cost": estimated_cost if isinstance(estimated_cost, (int, float)) else "Unknown",
            "cost_status": str(cost_status or "Unknown"),
            "cache_status": str(cache_status or "unknown"),
            "output_stability_score": output_stability_score,
            "hallucination_risk_proxy": _hallucination_risk_proxy(output_text),
            "response_consistency_index": output_stability_score,
        }
        append_jsonl(path, record)
    except Exception:
        return path
    return path


def read_llm_traces(log_path: Optional[str] = None, limit: int = 100) -> list[Dict[str, Any]]:
    return _read_jsonl(_resolve_path(log_path), limit)


def _resolve_path(log_path: Optional[str]) -> Path:
    configured = log_path or os.environ.get("ATLAS_LLM_TRACE_LOG")
    return Path(configured) if configured else DEFAULT_LLM_TRACE_PATH


def _summarize_context(context: Dict[str, Any]) -> str:
    if not isinstance(context, dict):
        return "context=missing"
    keys = sorted(context.keys())
    contract = context.get("contract_version", "unknown")
    runtime_context = context.get("runtime_context", {}) if isinstance(context.get("runtime_context"), dict) else {}
    summary = {
        "contract": contract,
        "keys": keys[:12],
        "trigger": runtime_context.get("trigger_type"),
        "event_type": runtime_context.get("event_type"),
        "system_state": runtime_context.get("system_state"),
    }
    return _mask_secrets(json.dumps(summary, ensure_ascii=False, sort_keys=True))


def _mask_secrets(value: str) -> str:
    masked = value
    for env_name in (
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "KIMI_API_KEY",
        "GLM_API_KEY",
        "DEEPSEEK_API_KEY",
        "MORECODE_API_KEY",
        "ARK_API_KEY",
        "VOLCANO_API_KEY",
        "ATLAS_LLM_PROXY_API_KEY",
    ):
        secret = os.environ.get(env_name)
        if secret:
            masked = masked.replace(secret, "***")
    for pattern in _SECRET_PATTERNS:
        masked = pattern.sub("***", masked)
    return masked


def _read_jsonl(path: Path, limit: int) -> list[Dict[str, Any]]:
    return read_jsonl_tail(path, limit)


def _previous_outputs(path: Path, prompt_hash: str) -> list[str]:
    try:
        return [
            str(record.get("output_raw", ""))
            for record in _read_jsonl(path, limit=50)
            if record.get("prompt_hash") == prompt_hash
        ]
    except Exception:
        return []


def _output_stability_score(output: str, previous_outputs: list[str]) -> float:
    if not previous_outputs:
        return 1.0
    matches = sum(1 for item in previous_outputs if item == output)
    return round(matches / len(previous_outputs), 4)


def _hallucination_risk_proxy(output: str) -> float:
    text = output.lower()
    risk = 0.0
    for term in ("guaranteed", "certain", "must", "target weight", "execute", "place order"):
        if term in text:
            risk += 0.18
    if not output.strip().startswith("{"):
        risk += 0.2
    return round(max(0.0, min(1.0, risk)), 4)


def _normalize_usage(value: Mapping[str, Any] | None) -> dict[str, int | None]:
    usage = value if isinstance(value, Mapping) else {}
    return {
        "input_tokens": _optional_int(usage.get("input_tokens")),
        "output_tokens": _optional_int(usage.get("output_tokens")),
        "total_tokens": _optional_int(usage.get("total_tokens")),
    }


def _safe_fallback_attempts(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    result: list[dict[str, str]] = []
    for item in value[:8]:
        if not isinstance(item, Mapping):
            continue
        result.append(
            {
                "provider": str(item.get("provider") or "unknown")[:80],
                "error": _mask_secrets(str(item.get("error") or ""))[:240],
            }
        )
    return result


def _optional_int(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None
