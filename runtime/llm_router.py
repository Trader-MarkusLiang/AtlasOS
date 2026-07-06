"""Lightweight multi-provider LLM router for Atlas Runtime.

The v0.2 contract path returns raw text only. DecisionPacket parsing and
validation must happen in `runtime.cognition.decision_contract`, not here.
If provider credentials are missing, the router returns raw failsafe JSON so
the runtime can continue without crashing.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
import importlib
from dataclasses import dataclass
from typing import Any, Dict, Optional

try:
    from runtime.telemetry.llm_trace_logger import log_llm_trace
except ModuleNotFoundError:  # pragma: no cover
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from runtime.telemetry.llm_trace_logger import log_llm_trace


SUPPORTED_PROVIDERS = {
    "openai": {
        "provider": "openai",
        "env_key": "OPENAI_API_KEY",
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "default_model": "gpt-5.5",
    },
    "gpt": {
        "provider": "openai",
        "env_key": "OPENAI_API_KEY",
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "default_model": "gpt-5.5",
    },
    "gpt-5.5": {
        "provider": "openai",
        "env_key": "OPENAI_API_KEY",
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "default_model": "gpt-5.5",
    },
    "claude": {
        "provider": "anthropic",
        "env_key": "ANTHROPIC_API_KEY",
        "endpoint": "https://api.anthropic.com/v1/messages",
        "default_model": "claude-sonnet-4-20250514",
    },
    "claude-sonnet": {
        "provider": "anthropic",
        "env_key": "ANTHROPIC_API_KEY",
        "endpoint": "https://api.anthropic.com/v1/messages",
        "default_model": "claude-sonnet-4-20250514",
    },
    "kimi": {
        "provider": "openai_compatible",
        "env_key": "KIMI_API_KEY",
        "endpoint": "https://api.moonshot.cn/v1/chat/completions",
        "default_model": "moonshot-v1-32k",
    },
    "glm": {
        "provider": "openai_compatible",
        "env_key": "GLM_API_KEY",
        "endpoint": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        "default_model": "glm-4-plus",
    },
    "local": {
        "provider": "ollama",
        "env_key": "",
        "endpoint": "http://localhost:11434/api/generate",
        "default_model": "llama3.1",
    },
    "ollama": {
        "provider": "ollama",
        "env_key": "",
        "endpoint": "http://localhost:11434/api/generate",
        "default_model": "llama3.1",
    },
    "proxy": {
        "provider": "proxy",
        "env_key": "ATLAS_LLM_PROXY_API_KEY",
        "endpoint": "",
        "default_model": "atlas-proxy-default",
    },
}


@dataclass
class LLMResult:
    model: str
    provider: str
    status: str
    content: str
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "provider": self.provider,
            "status": self.status,
            "content": self.content,
            "error": self.error,
        }


def call_llm(model: str, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Compatibility wrapper around the v0.2 raw-text router."""

    config = _provider_config(model)
    raw_text = call_llm_raw(model, prompt, context)
    return LLMResult(
        model=config["default_model"],
        provider=config["provider"],
        status="raw_text_returned",
        content=raw_text,
    ).to_dict()


def call_llm_raw(model: str, prompt: str, context: Dict[str, Any]) -> str:
    """Call a configured provider and return raw text only."""

    started = time.time()
    config = _provider_config(model)
    output = ""
    backend = os.environ.get("ATLAS_LLM_BACKEND", "native").strip().lower()
    try:
        if backend == "litellm":
            output = _call_litellm_backend_raw(model, prompt, context)
        elif model not in SUPPORTED_PROVIDERS:
            output = _failsafe_raw_json("unsupported_model")
        elif config["provider"] == "ollama":
            output = _call_ollama(config, prompt, context)
        elif config["provider"] == "proxy":
            output = _call_proxy(config, prompt, context)
        else:
            api_key = os.environ.get(config["env_key"])
            if not api_key:
                output = _failsafe_raw_json("offline_no_api_key")
            elif config["provider"] == "anthropic":
                output = _call_anthropic(config, api_key, prompt, context)
            else:
                output = _call_openai_compatible(config, api_key, prompt, context)
    except (urllib.error.URLError, TimeoutError, KeyError, ValueError) as exc:
        output = _failsafe_raw_json(f"provider_error: {exc}")

    runtime_context = context.get("runtime_context", {}) if isinstance(context, dict) else {}
    log_llm_trace(
        provider=config.get("provider", "unknown"),
        model=config.get("default_model", model),
        prompt=prompt,
        context=context,
        output_raw=output,
        latency_ms=int((time.time() - started) * 1000),
        decision_packet_id=str(runtime_context.get("decision_packet_id", "")) if isinstance(runtime_context, dict) else "",
        feedback_applied=bool(runtime_context.get("feedback_applied", False)) if isinstance(runtime_context, dict) else False,
    )
    return output


def _call_openai_compatible(
    config: Dict[str, str],
    api_key: str,
    prompt: str,
    context: Dict[str, Any],
) -> str:
    payload = {
        "model": config["default_model"],
        "messages": [
            {"role": "system", "content": "You are Atlas OS runtime. Never output trade execution."},
            {"role": "user", "content": f"{prompt}\n\nContext:\n{json.dumps(context, ensure_ascii=False)}"},
        ],
        "temperature": 0.2,
    }
    request = urllib.request.Request(
        config["endpoint"],
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


def _call_anthropic(
    config: Dict[str, str],
    api_key: str,
    prompt: str,
    context: Dict[str, Any],
) -> str:
    payload = {
        "model": config["default_model"],
        "max_tokens": 1200,
        "temperature": 0.2,
        "messages": [
            {
                "role": "user",
                "content": f"{prompt}\n\nContext:\n{json.dumps(context, ensure_ascii=False)}",
            }
        ],
    }
    request = urllib.request.Request(
        config["endpoint"],
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
    return data["content"][0]["text"]


def supported_models() -> Dict[str, Dict[str, str]]:
    """Return supported provider metadata without secrets."""

    return {
        name: {
            "provider": config["provider"],
            "default_model": config["default_model"],
            "configured": str(config["provider"] == "ollama" or bool(os.environ.get(config["env_key"]))),
        }
        for name, config in SUPPORTED_PROVIDERS.items()
    }


def backend_status() -> Dict[str, str]:
    backend = os.environ.get("ATLAS_LLM_BACKEND", "native").strip().lower()
    return {
        "backend": backend,
        "role": "infrastructure_only",
        "litellm_available": str(_litellm_available()),
    }


def _call_litellm_backend_raw(model: str, prompt: str, context: Dict[str, Any]) -> str:
    if not _litellm_available():
        return _failsafe_raw_json("litellm_not_installed")
    try:  # pragma: no cover - depends on optional infrastructure
        litellm = importlib.import_module("litellm")
        response = litellm.completion(
            model=model,
            messages=[
                {"role": "system", "content": "You are Atlas OS runtime. Never output trade execution."},
                {"role": "user", "content": f"{prompt}\n\nContext:\n{json.dumps(context, ensure_ascii=False)}"},
            ],
            temperature=0.2,
        )
        return response["choices"][0]["message"]["content"]
    except Exception as exc:
        return _failsafe_raw_json(f"litellm_provider_error: {exc}")


def _litellm_available() -> bool:
    try:
        importlib.import_module("litellm")
    except ModuleNotFoundError:
        return False
    return True


def _call_ollama(config: Dict[str, str], prompt: str, context: Dict[str, Any]) -> str:
    endpoint = os.environ.get("OLLAMA_HOST", config["endpoint"]).rstrip("/")
    if not endpoint.endswith("/api/generate"):
        endpoint = endpoint + "/api/generate"
    payload = {
        "model": os.environ.get("ATLAS_OLLAMA_MODEL", config["default_model"]),
        "prompt": f"{prompt}\n\nContext:\n{json.dumps(context, ensure_ascii=False)}",
        "stream": False,
    }
    try:
        request = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
        return str(data.get("response", ""))
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        return _failsafe_raw_json(f"ollama_error: {exc}")


def _call_proxy(config: Dict[str, str], prompt: str, context: Dict[str, Any]) -> str:
    endpoint = os.environ.get("ATLAS_LLM_PROXY_URL", "").strip()
    if not endpoint:
        return _failsafe_raw_json("proxy_url_missing")
    api_key = os.environ.get(config["env_key"], "")
    payload = {
        "model": os.environ.get("ATLAS_LLM_PROXY_MODEL", config["default_model"]),
        "prompt": prompt,
        "context": context,
    }
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    try:
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
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        return _failsafe_raw_json(f"proxy_error: {exc}")


def _provider_config(model: str) -> Dict[str, str]:
    return SUPPORTED_PROVIDERS.get(
        model,
        {
            "provider": "unknown",
            "env_key": "",
            "endpoint": "",
            "default_model": model,
        },
    )


def provider_metadata(model: str) -> Dict[str, str]:
    config = _provider_config(model)
    return {
        "provider": config["provider"],
        "model": config["default_model"],
        "raw_text_only": "true",
    }


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
            "reasoning_trace": str(reason)[:200],
        },
        ensure_ascii=False,
        sort_keys=True,
    )
