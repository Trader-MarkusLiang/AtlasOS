"""Lightweight multi-provider LLM router for Atlas Runtime.

The router uses only the Python standard library. If provider credentials are
missing, it returns an explicit offline result instead of blocking runtime.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Optional


SUPPORTED_PROVIDERS = {
    "gpt-5.5": {
        "provider": "openai",
        "env_key": "OPENAI_API_KEY",
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "default_model": "gpt-5.5",
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
    """Call a configured LLM provider or return an offline placeholder."""

    config = SUPPORTED_PROVIDERS.get(model)
    if not config:
        return LLMResult(
            model=model,
            provider="unknown",
            status="unsupported_model",
            content="LLM model unsupported. Runtime continues with deterministic brief.",
            error="unsupported_model",
        ).to_dict()

    api_key = os.environ.get(config["env_key"])
    if not api_key:
        return LLMResult(
            model=config["default_model"],
            provider=config["provider"],
            status="offline_no_api_key",
            content=(
                "LLM credentials unavailable. Runtime generated a deterministic non-binding "
                "Decision Brief from local context only."
            ),
        ).to_dict()

    try:
        if config["provider"] == "anthropic":
            content = _call_anthropic(config, api_key, prompt, context)
        else:
            content = _call_openai_compatible(config, api_key, prompt, context)
        return LLMResult(
            model=config["default_model"],
            provider=config["provider"],
            status="success",
            content=content,
        ).to_dict()
    except (urllib.error.URLError, TimeoutError, KeyError, ValueError) as exc:
        return LLMResult(
            model=config["default_model"],
            provider=config["provider"],
            status="provider_error",
            content="LLM provider call failed. Runtime continues with deterministic brief.",
            error=str(exc),
        ).to_dict()


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
            "configured": str(bool(os.environ.get(config["env_key"]))),
        }
        for name, config in SUPPORTED_PROVIDERS.items()
    }
