"""Provider router for Atlas LLM runtime.

The router is an adapter boundary. It returns raw text in a unified envelope
and never validates or changes DecisionPacket semantics.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from urllib.parse import urlsplit
from typing import Any, Mapping

from runtime.llm.provider_registry import (
    SUPPORTED_PROVIDER_TYPES,
    load_provider_registry,
    provider_api_key,
    record_provider_result,
)


DEFAULT_PROVIDER_TIMEOUT_SECONDS = 8.0


def route_llm_request(
    *,
    prompt: str,
    context: Mapping[str, Any] | None = None,
    provider_id: str | None = None,
    model: str | None = None,
    fallback_chain: list[str] | None = None,
    request_options: Mapping[str, Any] | None = None,
    config_path: str | None = None,
) -> dict[str, Any]:
    """Route one LLM call through configured providers with fallback."""

    registry = load_provider_registry(config_path)
    providers = {str(item.get("id")): dict(item) for item in registry.get("providers", []) if isinstance(item, Mapping)}
    chain = _routing_chain(registry, provider_id, fallback_chain)
    errors: list[dict[str, Any]] = []
    for index, current_id in enumerate(chain):
        provider = providers.get(current_id)
        if not provider or not provider.get("enabled", True):
            errors.append({"provider": current_id, "error": "provider_disabled_or_missing"})
            continue
        if model and index == 0:
            provider["model"] = model
        for key in ("timeout_seconds", "max_output_tokens"):
            if isinstance(request_options, Mapping) and request_options.get(key) not in (None, ""):
                provider[key] = request_options[key]
        if index == 0 and isinstance(request_options, Mapping) and "reasoning_effort" in request_options:
            provider["reasoning_effort"] = request_options.get("reasoning_effort") or ""
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
        "usage": _unknown_usage(),
        "error": "all_providers_failed",
        "fallback_attempts": errors,
    }


def _routing_chain(
    registry: Mapping[str, Any],
    provider_id: str | None,
    fallback_chain: list[str] | None = None,
) -> list[str]:
    active = str(provider_id or registry.get("active_provider") or "openai")
    fallback = fallback_chain if fallback_chain is not None else registry.get("fallback_chain", [])
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
            response = _call_anthropic(provider, prompt, context)
        elif protocol == "ollama":
            response = _call_ollama(provider, prompt, context)
        elif protocol == "proxy":
            response = _call_proxy(provider, prompt, context)
        else:
            response = _call_openai_compatible(provider, prompt, context)
        content = str(response.get("content") or "")
        if not str(content or "").strip():
            raise ValueError("empty_response")
        return {
            "status": "ok",
            "provider": provider_id,
            "provider_type": provider_type,
            "model": str(provider.get("model") or ""),
            "content": content,
            "usage": _normalize_usage(response.get("usage")),
            "latency_ms": int((time.time() - started) * 1000),
            "error": "",
        }
    except json.JSONDecodeError as exc:
        return {
            "status": "error",
            "provider": provider_id,
            "provider_type": provider_type,
            "model": str(provider.get("model") or ""),
            "content": "",
            "usage": _unknown_usage(),
            "latency_ms": int((time.time() - started) * 1000),
            "error": f"malformed_response: {exc}"[:240],
        }
    except urllib.error.HTTPError as exc:
        return {
            "status": "error",
            "provider": provider_id,
            "provider_type": provider_type,
            "model": str(provider.get("model") or ""),
            "content": "",
            "usage": _unknown_usage(),
            "latency_ms": int((time.time() - started) * 1000),
            "error": f"http_{exc.code}",
        }
    except (urllib.error.URLError, TimeoutError, KeyError, ValueError, OSError) as exc:
        return {
            "status": "error",
            "provider": provider_id,
            "provider_type": provider_type,
            "model": str(provider.get("model") or ""),
            "content": "",
            "usage": _unknown_usage(),
            "latency_ms": int((time.time() - started) * 1000),
            "error": str(exc)[:240],
        }


def _call_openai_compatible(provider: Mapping[str, Any], prompt: str, context: Mapping[str, Any]) -> dict[str, Any]:
    api_key = provider_api_key(provider)
    endpoint = str(provider.get("base_url") or "")
    if not endpoint:
        raise ValueError("base_url_missing")
    local_endpoint = _is_loopback_url(endpoint)
    if not api_key and not local_endpoint:
        raise ValueError("api_key_missing")
    payload = {
        "model": _provider_request_model(provider),
        "messages": [
            {"role": "system", "content": "You are Atlas OS runtime. Never output trade execution."},
            {"role": "user", "content": f"{prompt}\n\nContext:\n{json.dumps(context, ensure_ascii=False)}"},
        ],
        "temperature": 0.2,
    }
    reasoning_effort = _reasoning_effort(provider)
    if reasoning_effort:
        payload["reasoning_effort"] = reasoning_effort
    max_tokens = provider.get("max_output_tokens", provider.get("max_tokens"))
    if max_tokens not in (None, ""):
        payload["max_tokens"] = int(max_tokens)
    elif local_endpoint:
        payload["max_tokens"] = 2048
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request_data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(endpoint, data=request_data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=_provider_timeout_seconds(provider)) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code != 401 or not local_endpoint or "Authorization" not in headers:
            raise
        request = urllib.request.Request(
            endpoint,
            data=request_data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=_provider_timeout_seconds(provider)) as response:
            data = json.loads(response.read().decode("utf-8"))
    return {
        "content": str(data["choices"][0]["message"]["content"]),
        "usage": _usage_from_openai(data.get("usage")),
    }


def _is_loopback_url(value: str) -> bool:
    host = urlsplit(value).hostname or ""
    return host in {"localhost", "127.0.0.1", "::1"}


def _call_anthropic(provider: Mapping[str, Any], prompt: str, context: Mapping[str, Any]) -> dict[str, Any]:
    api_key = provider_api_key(provider)
    if not api_key:
        raise ValueError("api_key_missing")
    payload = {
        "model": str(provider.get("model") or "claude-sonnet-4-20250514"),
        "max_tokens": int(provider.get("max_output_tokens") or 1200),
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
    with urllib.request.urlopen(request, timeout=_provider_timeout_seconds(provider)) as response:
        data = json.loads(response.read().decode("utf-8"))
    return {
        "content": str(data["content"][0]["text"]),
        "usage": _usage_from_anthropic(data.get("usage")),
    }


def _call_ollama(provider: Mapping[str, Any], prompt: str, context: Mapping[str, Any]) -> dict[str, Any]:
    endpoint = str(provider.get("base_url") or "http://localhost:11434/api/generate").rstrip("/")
    if not endpoint.endswith("/api/generate"):
        endpoint += "/api/generate"
    payload = {
        "model": str(provider.get("model") or "llama3.1"),
        "prompt": f"{prompt}\n\nContext:\n{json.dumps(context, ensure_ascii=False)}",
        "stream": False,
    }
    if provider.get("max_output_tokens") not in (None, ""):
        payload["options"] = {"num_predict": int(provider["max_output_tokens"])}
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=_provider_timeout_seconds(provider)) as response:
        data = json.loads(response.read().decode("utf-8"))
    return {
        "content": str(data.get("response", "")),
        "usage": {
            "input_tokens": _optional_int(data.get("prompt_eval_count")),
            "output_tokens": _optional_int(data.get("eval_count")),
            "total_tokens": None,
        },
    }


def _call_proxy(provider: Mapping[str, Any], prompt: str, context: Mapping[str, Any]) -> dict[str, Any]:
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
    with urllib.request.urlopen(request, timeout=_provider_timeout_seconds(provider)) as response:
        data = json.loads(response.read().decode("utf-8"))
    if isinstance(data, dict):
        return {
            "content": str(data.get("content") or data.get("text") or data.get("response") or ""),
            "usage": _usage_from_openai(data.get("usage")),
        }
    return {"content": str(data), "usage": _unknown_usage()}


def _provider_timeout_seconds(provider: Mapping[str, Any]) -> float:
    value = provider.get("timeout_seconds", os.environ.get("ATLAS_LLM_PROVIDER_TIMEOUT_SECONDS", DEFAULT_PROVIDER_TIMEOUT_SECONDS))
    try:
        timeout = float(value)
    except (TypeError, ValueError):
        timeout = DEFAULT_PROVIDER_TIMEOUT_SECONDS
    return max(0.25, timeout)


def _provider_request_model(provider: Mapping[str, Any]) -> str:
    model = str(provider.get("model") or "gpt5.5").strip()
    if str(provider.get("id") or provider.get("type") or "").lower() == "morecode" and model == "gpt5.5":
        return "gpt-5.5"
    return model


def _reasoning_effort(provider: Mapping[str, Any]) -> str:
    value = str(provider.get("reasoning_effort") or provider.get("reasoning_level") or "").strip().lower()
    allowed = {"low", "medium", "high"}
    return value if value in allowed else ""


def _usage_from_openai(value: Any) -> dict[str, int | None]:
    usage = value if isinstance(value, Mapping) else {}
    return _normalize_usage(
        {
            "input_tokens": usage.get("prompt_tokens", usage.get("input_tokens")),
            "output_tokens": usage.get("completion_tokens", usage.get("output_tokens")),
            "total_tokens": usage.get("total_tokens"),
        }
    )


def _usage_from_anthropic(value: Any) -> dict[str, int | None]:
    usage = value if isinstance(value, Mapping) else {}
    return _normalize_usage(
        {
            "input_tokens": usage.get("input_tokens"),
            "output_tokens": usage.get("output_tokens"),
            "total_tokens": None,
        }
    )


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


def _optional_int(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


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
