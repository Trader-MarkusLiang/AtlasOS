"""Task-aware provider routing policy for Atlas Runtime.

This module selects provider adapters for bounded LLM responsibilities. It is
not a cognition layer and never validates or mutates a DecisionPacket.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Mapping

from runtime.llm.provider_registry import CONFIG_PATH, load_provider_registry
from runtime.llm.provider_router import route_llm_request
from runtime.logging import utc_now_iso
from runtime.telemetry.llm_trace_logger import log_llm_trace


TASK_ROLES = ("workhorse", "research", "decision")
_ROLE_DEFAULTS = {
    "workhorse": {"enabled": True, "timeout_seconds": 20, "max_output_tokens": 2000},
    "research": {"enabled": True, "timeout_seconds": 30, "max_output_tokens": 4000},
    "decision": {"enabled": True, "timeout_seconds": 45, "max_output_tokens": 4000},
}


def default_task_routes(registry: Mapping[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    provider_registry = dict(registry or load_provider_registry())
    active = str(provider_registry.get("active_provider") or "openai")
    providers = {
        str(item.get("id")): item
        for item in provider_registry.get("providers", [])
        if isinstance(item, Mapping)
    }
    active_provider = providers.get(active, {})
    fallback = [str(item) for item in provider_registry.get("fallback_chain", []) if str(item)]
    routes: dict[str, dict[str, Any]] = {}
    for role in TASK_ROLES:
        defaults = _ROLE_DEFAULTS[role]
        routes[role] = {
            "enabled": bool(defaults["enabled"]),
            "provider_id": active,
            "model": _preferred_model(role, active_provider),
            "fallback_chain": [item for item in fallback if item != active],
            "timeout_seconds": int(defaults["timeout_seconds"]),
            "max_output_tokens": int(defaults["max_output_tokens"]),
            "reasoning_effort": "medium" if role == "decision" else "",
        }
    return routes


def _preferred_model(role: str, provider: Mapping[str, Any]) -> str:
    available = [str(item) for item in provider.get("available_models", [])] if isinstance(provider.get("available_models"), list) else []
    if role in {"workhorse", "research"} and "kimi-k2.6" in available:
        return "kimi-k2.6"
    if role == "decision" and "gpt5.5" in available:
        return "gpt5.5"
    return str(provider.get("model") or "")


def load_task_routes(config_path: str | None = None) -> dict[str, dict[str, Any]]:
    registry = load_provider_registry(config_path)
    config = _load_config(config_path)
    return normalize_task_routes(config.get("llm_task_routes"), registry)


def normalize_task_routes(
    value: Any,
    registry: Mapping[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    provider_registry = dict(registry or load_provider_registry())
    defaults = default_task_routes(provider_registry)
    incoming = value if isinstance(value, Mapping) else {}
    routes: dict[str, dict[str, Any]] = {}
    for role in TASK_ROLES:
        item = incoming.get(role, {}) if isinstance(incoming.get(role, {}), Mapping) else {}
        route = dict(defaults[role])
        route.update({key: item[key] for key in item if key in route})
        route["enabled"] = bool(route.get("enabled", defaults[role]["enabled"]))
        route["provider_id"] = _safe_id(route.get("provider_id"))
        route["model"] = str(route.get("model") or "").strip()[:160]
        route["fallback_chain"] = _normalize_fallback(route.get("fallback_chain"), route["provider_id"])
        route["timeout_seconds"] = _bounded_int(route.get("timeout_seconds"), 1, 120, defaults[role]["timeout_seconds"])
        route["max_output_tokens"] = _bounded_int(
            route.get("max_output_tokens"), 128, 32000, defaults[role]["max_output_tokens"]
        )
        effort = str(route.get("reasoning_effort") or "").strip().lower()
        route["reasoning_effort"] = effort if effort in {"low", "medium", "high"} else ""
        routes[role] = route
    return routes


def save_task_routes(routes: Mapping[str, Any], config_path: str | None = None) -> dict[str, Any]:
    target = _config_path(config_path)
    config = _load_config(config_path)
    normalized = normalize_task_routes(routes, load_provider_registry(config_path))
    config["llm_task_routes"] = normalized
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(config, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return safe_task_routes_view(normalized, load_provider_registry(config_path))


def resolve_task_route(
    task_type: str,
    config: Mapping[str, Any] | None = None,
    *,
    config_path: str | None = None,
) -> dict[str, Any]:
    role = str(task_type or "").strip().lower()
    if role not in TASK_ROLES:
        raise ValueError(f"unsupported_task_role:{role or 'missing'}")
    registry = load_provider_registry(config_path)
    routes = normalize_task_routes(
        config.get("llm_task_routes") if isinstance(config, Mapping) else _load_config(config_path).get("llm_task_routes"),
        registry,
    )
    route = {"task_role": role, **routes[role]}
    route["validation"] = validate_task_route(route, registry)
    route["route_status"] = (
        "DISABLED"
        if not route["enabled"]
        else "ACTIVE"
        if route["validation"]["valid"]
        else "INVALID"
    )
    return route


def validate_task_route(route: Mapping[str, Any], provider_registry: Mapping[str, Any]) -> dict[str, Any]:
    providers = {
        str(item.get("id")): item
        for item in provider_registry.get("providers", [])
        if isinstance(item, Mapping)
    }
    provider_id = str(route.get("provider_id") or "")
    provider = providers.get(provider_id)
    errors: list[str] = []
    warnings: list[str] = []
    if not provider:
        errors.append("provider_not_found")
    elif not provider.get("enabled", True):
        errors.append("provider_disabled")
    model = str(route.get("model") or "")
    available_models = provider.get("available_models", []) if isinstance(provider, Mapping) else []
    aliases = {model}
    if isinstance(provider, Mapping) and str(provider.get("type") or provider.get("id")) == "morecode" and model == "gpt5.5":
        aliases.add("gpt-5.5")
    if model and isinstance(available_models, list) and available_models and not aliases.intersection(available_models):
        warnings.append("custom_or_unlisted_model")
    for fallback_id in route.get("fallback_chain", []):
        fallback = providers.get(str(fallback_id))
        if not fallback:
            warnings.append(f"fallback_missing:{fallback_id}")
        elif not fallback.get("enabled", True):
            warnings.append(f"fallback_disabled:{fallback_id}")
    return {"valid": not errors, "errors": errors, "warnings": warnings}


def safe_task_routes_view(
    routes: Mapping[str, Any] | None = None,
    registry: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    provider_registry = dict(registry or load_provider_registry())
    normalized = normalize_task_routes(routes, provider_registry)
    providers = {
        str(item.get("id")): item
        for item in provider_registry.get("providers", [])
        if isinstance(item, Mapping)
    }
    result: dict[str, Any] = {}
    for role in TASK_ROLES:
        route = {"task_role": role, **normalized[role]}
        validation = validate_task_route(route, provider_registry)
        provider = providers.get(route["provider_id"], {})
        result[role] = {
            **route,
            "route_status": "DISABLED" if not route["enabled"] else "ACTIVE" if validation["valid"] else "INVALID",
            "validation": validation,
            "provider_health": provider.get("health", "missing"),
            "provider_latency_ms": provider.get("last_latency_ms"),
            "available_models": list(provider.get("available_models", [])) if isinstance(provider.get("available_models"), list) else [],
        }
    return result


def route_task_request(
    task_type: str,
    prompt: str,
    context: Mapping[str, Any] | None,
    config: Mapping[str, Any] | None = None,
    *,
    config_path: str | None = None,
    cache_status: str = "miss",
) -> dict[str, Any]:
    route = resolve_task_route(task_type, config, config_path=config_path)
    role = route["task_role"]
    if route["route_status"] != "ACTIVE":
        return {
            "status": "not_called",
            "task_role": role,
            "route_status": route["route_status"],
            "provider": route.get("provider_id"),
            "model": route.get("model"),
            "content": "",
            "latency_ms": 0,
            "usage": _unknown_usage(),
            "estimated_cost": "Unknown",
            "cost_status": "Unknown",
            "cache_status": cache_status,
            "error": ",".join(route["validation"]["errors"]) or "route_disabled",
            "fallback_attempts": [],
        }

    started_at = utc_now_iso()
    started = time.time()
    result = route_llm_request(
        prompt=prompt,
        context=context,
        provider_id=route["provider_id"],
        model=route["model"] or None,
        fallback_chain=route["fallback_chain"],
        request_options={
            "timeout_seconds": route["timeout_seconds"],
            "max_output_tokens": route["max_output_tokens"],
            "reasoning_effort": route["reasoning_effort"],
        },
        config_path=config_path,
    )
    latency_ms = int((time.time() - started) * 1000)
    result["latency_ms"] = latency_ms
    result["task_role"] = role
    result["route_status"] = route["route_status"]
    result["cache_status"] = cache_status
    result["usage"] = _normalize_usage(result.get("usage"))
    estimated_cost, cost_status = _estimate_cost(result, load_provider_registry(config_path))
    result["estimated_cost"] = estimated_cost
    result["cost_status"] = cost_status
    completed_at = utc_now_iso()
    runtime_context = context.get("runtime_context", {}) if isinstance(context, Mapping) else {}
    trigger_type = str(runtime_context.get("trigger_type") or runtime_context.get("event_type") or "unknown")
    log_llm_trace(
        provider=str(result.get("provider") or route["provider_id"]),
        model=str(result.get("model") or route.get("model") or "unknown"),
        prompt=prompt,
        context=dict(context or {}),
        output_raw=str(result.get("content") or ""),
        latency_ms=latency_ms,
        decision_packet_id=str(runtime_context.get("decision_packet_id") or ""),
        feedback_applied=bool(role == "decision" and runtime_context.get("feedback_applied", False)),
        task_role=role,
        started_at=started_at,
        completed_at=completed_at,
        status=str(result.get("status") or "unknown"),
        error=str(result.get("error") or ""),
        fallback_attempts=result.get("fallback_attempts", []),
        trigger_type=trigger_type,
        usage=result["usage"],
        estimated_cost=estimated_cost,
        cost_status=cost_status,
        cache_status=cache_status,
    )
    return result


def _estimate_cost(result: Mapping[str, Any], registry: Mapping[str, Any]) -> tuple[float | str, str]:
    provider_id = str(result.get("provider") or "")
    provider = next(
        (item for item in registry.get("providers", []) if isinstance(item, Mapping) and item.get("id") == provider_id),
        {},
    )
    usage = _normalize_usage(result.get("usage"))
    input_rate = _optional_float(provider.get("input_cost_per_million"))
    output_rate = _optional_float(provider.get("output_cost_per_million"))
    input_tokens = usage.get("input_tokens")
    output_tokens = usage.get("output_tokens")
    if input_rate is None or output_rate is None:
        return "Unknown", "pricing_not_configured"
    if input_tokens is None or output_tokens is None:
        return "Unknown", "usage_not_returned"
    cost = (input_tokens * input_rate + output_tokens * output_rate) / 1_000_000
    return round(cost, 8), "estimated"


def _normalize_usage(value: Any) -> dict[str, int | None]:
    usage = value if isinstance(value, Mapping) else {}
    input_tokens = _optional_int(usage.get("input_tokens"))
    output_tokens = _optional_int(usage.get("output_tokens"))
    total_tokens = _optional_int(usage.get("total_tokens"))
    if total_tokens is None and input_tokens is not None and output_tokens is not None:
        total_tokens = input_tokens + output_tokens
    return {"input_tokens": input_tokens, "output_tokens": output_tokens, "total_tokens": total_tokens}


def _unknown_usage() -> dict[str, None]:
    return {"input_tokens": None, "output_tokens": None, "total_tokens": None}


def _load_config(config_path: str | None) -> dict[str, Any]:
    path = _config_path(config_path)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _config_path(config_path: str | None) -> Path:
    configured = config_path or os.environ.get("ATLAS_USER_CONFIG")
    return Path(configured) if configured else CONFIG_PATH


def _safe_id(value: Any) -> str:
    clean = "".join(ch for ch in str(value or "").strip().lower().replace(" ", "_") if ch.isalnum() or ch in {"_", "-"})
    return clean or "openai"


def _normalize_fallback(value: Any, primary: str) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        provider_id = _safe_id(item)
        if provider_id != primary and provider_id not in result:
            result.append(provider_id)
    return result[:8]


def _bounded_int(value: Any, minimum: int, maximum: int, fallback: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = fallback
    return max(minimum, min(maximum, parsed))


def _optional_int(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _optional_float(value: Any) -> float | None:
    try:
        return float(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None
