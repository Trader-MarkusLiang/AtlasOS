"""Provider router for Atlas LLM runtime.

The router is an adapter boundary. It returns raw text in a unified envelope
and never validates or changes DecisionPacket semantics.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any, Mapping

from runtime.llm.provider_registry import (
    SUPPORTED_PROVIDER_TYPES,
    load_provider_registry,
    provider_api_key,
    record_provider_result,
)


def route_llm_request(
    *,
    prompt: str,
    context: Mapping[str, Any] | None = None,
    provider_id: str | None = None,
    model: str | None = None,
    config_path: str | None = None,
) -> dict[str, Any]:
    """Route one LLM call through configured providers with fallback."""

    registry = load_provider_registry(config_path)
    providers = {str(item.get("id")): dict(item) for item in registry.get("providers", []) if isinstance(item, Mapping)}
    chain = _routing_chain(registry, provider_id)
    errors: list[dict[str, Any]] = []
    for current_id in chain:
        provider = providers.get(current_id)
        if not provider or not provider.get("enabled", True):
            errors.append({"provider": current_id, "error": "provider_disabled_or_missing"})
            continue
        if model:
            provider["model"] = model
        result = _call_provider(provider, prompt, dict(context or {}))
        record_provider_result(
            current_id,
            ok=result["status"] == "ok",
            latency_ms=int(result.get("latency_ms", 0)),
            error=str(result.get("error") or ""),
            path=config_path,
        )
        if result["status"] == "ok":
            result["fallback_attempts"] = errors
            return result
        errors.append({"provider": current_id, "error": result.get("error", "provider_error")})
    return {
        "status": "failsafe",
        "provider": provider_id or registry.get("active_provider", "unknown"),
        "model": model or "",
        "content": _failsafe_raw_json("all_providers_failed"),
        "latency_ms": 0,
        "error": "all_providers_failed",
        "fallback_attempts": errors,
    }


def _routing_chain(registry: Mapping[str, Any], provider_id: str | None) -> list[str]:
    active = str(provider_id or registry.get("active_provider") or "openai")
    fallback = registry.get("fallback_chain", [])
    chain = [active]
    if isinstance(fallback, list):
        chain.extend(str(item) for item in fallback if str(item) != active)
    return [item for item in chain if item]


def _call_provider(provider: Mapping[str, Any], prompt: str, context: Mapping[str, Any]) -> dict[str, Any]:
    provider_id = str(provider.get("id") or "unknown")
    provider_type = str(provider.get("type") or provider_id)
    protocol = SUPPORTED_PROVIDER_TYPES.get(provider_type, SUPPORTED_PROVIDER_TYPES["custom"])["protocol"]
    started = time.time()
    try:
        if protocol == "anthropic":
            content = _call_anthropic(provider, prompt, context)
        elif protocol == "ollama":
            content = _call_ollama(provider, prompt, context)
        elif protocol == "proxy":
            content = _call_proxy(provider, prompt, context)
        else:
            content = _call_openai_compatible(provider, prompt, context)
        return {
            "status": "ok",
            "provider": provider_id,
            "provider_type": provider_type,
            "model": str(provider.get("model") or ""),
            "content": content,
            "latency_ms": int((time.time() - started) * 1000),
            "error": "",
        }
    except (urllib.error.URLError, TimeoutError, KeyError, ValueError, OSError) as exc:
        return {
            "status": "error",
            "provider": provider_id,
            "provider_type": provider_type,
            "model": str(provider.get("model") or ""),
            "content": "",
            "latency_ms": int((time.time() - started) * 1000),
            "error": str(exc)[:240],
        }


def _call_openai_compatible(provider: Mapping[str, Any], prompt: str, context: Mapping[str, Any]) -> str:
    api_key = provider_api_key(provider)
    if not api_key:
        raise ValueError("api_key_missing")
    endpoint = str(provider.get("base_url") or "")
    if not endpoint:
        raise ValueError("base_url_missing")
    payload = {
        "model": str(provider.get("model") or "gpt-5.5"),
        "messages": [
            {"role": "system", "content": "You are Atlas OS runtime. Never output trade execution."},
            {"role": "user", "content": f"{prompt}\n\nContext:\n{json.dumps(context, ensure_ascii=False)}"},
        ],
        "temperature": 0.2,
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))
    return str(data["choices"][0]["message"]["content"])


def _call_anthropic(provider: Mapping[str, Any], prompt: str, context: Mapping[str, Any]) -> str:
    api_key = provider_api_key(provider)
    if not api_key:
        raise ValueError("api_key_missing")
    payload = {
        "model": str(provider.get("model") or "claude-sonnet-4-20250514"),
        "max_tokens": 1200,
        "temperature": 0.2,
        "messages": [
            {"role": "user", "content": f"{prompt}\n\nContext:\n{json.dumps(context, ensure_ascii=False)}"}
        ],
    }
    request = urllib.request.Request(
        str(provider.get("base_url") or "https://api.anthropic.com/v1/messages"),
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))
    return str(data["content"][0]["text"])


def _call_ollama(provider: Mapping[str, Any], prompt: str, context: Mapping[str, Any]) -> str:
    endpoint = str(provider.get("base_url") or "http://localhost:11434/api/generate").rstrip("/")
    if not endpoint.endswith("/api/generate"):
        endpoint += "/api/generate"
    payload = {
        "model": str(provider.get("model") or "llama3.1"),
        "prompt": f"{prompt}\n\nContext:\n{json.dumps(context, ensure_ascii=False)}",
        "stream": False,
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))
    return str(data.get("response", ""))


def _call_proxy(provider: Mapping[str, Any], prompt: str, context: Mapping[str, Any]) -> str:
    endpoint = str(provider.get("base_url") or "")
    if not endpoint:
        raise ValueError("base_url_missing")
    payload = {
        "model": str(provider.get("model") or "custom-default"),
        "prompt": prompt,
        "context": context,
    }
    headers = {"Content-Type": "application/json"}
    api_key = provider_api_key(provider)
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))
    if isinstance(data, dict):
        return str(data.get("content") or data.get("text") or data.get("response") or "")
    return str(data)


def _failsafe_raw_json(reason: str) -> str:
    return json.dumps(
        {
            "regime_state": "unknown",
            "confidence": 0.0,
            "risk_level": "unknown",
            "attention_state": "unknown",
            "liquidity_state": "unknown",
            "causal_summary": "LLM reasoning unavailable or invalid.",
            "recommended_action": "neutral",
            "reasoning_trace": reason[:200],
        },
        ensure_ascii=False,
        sort_keys=True,
    )

