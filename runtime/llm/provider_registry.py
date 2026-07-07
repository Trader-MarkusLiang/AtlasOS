"""Local LLM provider registry for Atlas Runtime.

This module is infrastructure only. It stores provider connection metadata in
`runtime/config/user_config.json`, masks secrets for UI output, and keeps
latency/health information for routing. It does not parse DecisionPackets or
modify cognition.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import platform
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Mapping


CONFIG_PATH = Path("runtime/config/user_config.json")
SUPPORTED_PROVIDER_TYPES = {
    "openai": {
        "label": "OpenAI",
        "base_url": "https://api.openai.com/v1/chat/completions",
        "model": "gpt-5.5",
        "protocol": "openai_compatible",
    },
    "claude": {
        "label": "Claude",
        "base_url": "https://api.anthropic.com/v1/messages",
        "model": "claude-sonnet-4-20250514",
        "protocol": "anthropic",
    },
    "ollama": {
        "label": "Ollama",
        "base_url": "http://localhost:11434/api/generate",
        "model": "llama3.1",
        "protocol": "ollama",
    },
    "morecode": {
        "label": "MoreCode / cc switch",
        "base_url": "",
        "model": "morecode-default",
        "protocol": "openai_compatible",
    },
    "ark": {
        "label": "ARK Coding",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        "model": "doubao-seed-1-6",
        "protocol": "openai_compatible",
    },
    "volcano": {
        "label": "Volcano Coding",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        "model": "doubao-seed-1-6",
        "protocol": "openai_compatible",
    },
    "custom": {
        "label": "Custom Proxy",
        "base_url": "",
        "model": "custom-default",
        "protocol": "proxy",
    },
}


def default_provider_registry() -> dict[str, Any]:
    providers = []
    for provider_id, meta in SUPPORTED_PROVIDER_TYPES.items():
        providers.append(
            {
                "id": provider_id,
                "type": provider_id,
                "label": meta["label"],
                "enabled": provider_id in {"openai", "ollama"},
                "base_url": meta["base_url"],
                "model": meta["model"],
                "api_key_encrypted": "",
                "health": "unknown",
                "last_latency_ms": None,
                "last_error": "",
            }
        )
    return {
        "active_provider": "openai",
        "fallback_chain": ["openai", "claude", "ollama", "custom"],
        "providers": providers,
    }


def load_provider_registry(path: str | None = None) -> dict[str, Any]:
    config = _load_config(path)
    registry = config.get("llm_registry")
    if not isinstance(registry, dict):
        registry = _registry_from_legacy(config.get("llm", {}))
    return _normalize_registry(registry)


def save_provider_registry(registry: Mapping[str, Any], path: str | None = None) -> dict[str, Any]:
    config = _load_config(path)
    normalized = _normalize_registry(registry)
    config["llm_registry"] = normalized
    config["llm"] = _legacy_llm_from_registry(normalized)
    target = Path(path) if path else CONFIG_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(config, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return safe_registry_view(normalized)


def update_provider_registry(payload: Mapping[str, Any], path: str | None = None) -> dict[str, Any]:
    incoming = payload.get("llm_registry", payload)
    raw_keys: dict[str, str] = {}
    if isinstance(incoming, Mapping):
        for provider in incoming.get("providers", []):
            if isinstance(provider, Mapping):
                provider_id = _safe_provider_id(str(provider.get("id") or provider.get("type") or "custom"))
                raw_key = str(provider.get("api_key", "") or "")
                if raw_key and raw_key != "***":
                    raw_keys[provider_id] = raw_key
    registry = _normalize_registry(incoming)
    providers = []
    for provider in registry["providers"]:
        item = dict(provider)
        raw_key = raw_keys.get(str(item.get("id")), "")
        if raw_key and raw_key != "***":
            item["api_key_encrypted"] = encrypt_api_key(raw_key)
        providers.append(item)
    registry["providers"] = providers
    return save_provider_registry(registry, path)


def get_provider(provider_id: str | None = None, path: str | None = None) -> dict[str, Any] | None:
    registry = load_provider_registry(path)
    target_id = provider_id or registry.get("active_provider")
    for provider in registry.get("providers", []):
        if provider.get("id") == target_id:
            return dict(provider)
    return None


def provider_api_key(provider: Mapping[str, Any]) -> str:
    encrypted = str(provider.get("api_key_encrypted", "") or "")
    if encrypted:
        return decrypt_api_key(encrypted)
    env_name = f"ATLAS_LLM_{str(provider.get('id', '')).upper()}_API_KEY"
    if os.environ.get(env_name):
        return os.environ[env_name]
    legacy_names = {
        "openai": "OPENAI_API_KEY",
        "claude": "ANTHROPIC_API_KEY",
        "ark": "ARK_API_KEY",
        "volcano": "VOLCANO_API_KEY",
        "morecode": "MORECODE_API_KEY",
        "custom": "ATLAS_LLM_PROXY_API_KEY",
    }
    return os.environ.get(legacy_names.get(str(provider.get("id")), ""), "")


def safe_registry_view(registry: Mapping[str, Any] | None = None) -> dict[str, Any]:
    normalized = _normalize_registry(registry or load_provider_registry())
    safe_providers = []
    for provider in normalized["providers"]:
        item = dict(provider)
        item["api_key"] = "***" if item.get("api_key_encrypted") else ""
        item.pop("api_key_encrypted", None)
        safe_providers.append(item)
    return {
        "active_provider": normalized["active_provider"],
        "fallback_chain": list(normalized["fallback_chain"]),
        "providers": safe_providers,
        "supported_provider_types": SUPPORTED_PROVIDER_TYPES,
    }


def record_provider_result(
    provider_id: str,
    *,
    ok: bool,
    latency_ms: int,
    error: str = "",
    health: str | None = None,
    path: str | None = None,
) -> None:
    config = _load_config(path)
    registry = _normalize_registry(config.get("llm_registry", default_provider_registry()))
    for provider in registry["providers"]:
        if provider.get("id") == provider_id:
            provider["health"] = str(health or ("healthy" if ok else "error"))
            provider["last_latency_ms"] = int(latency_ms)
            provider["last_error"] = str(error)[:240]
            provider["last_checked_at"] = int(time.time())
            break
    config["llm_registry"] = registry
    target = Path(path) if path else CONFIG_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(config, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def health_check_provider(provider_id: str, path: str | None = None, timeout: float = 6.0) -> dict[str, Any]:
    provider = get_provider(provider_id, path)
    if not provider:
        return {"provider": provider_id, "status": "missing", "latency_ms": 0, "error": "provider_not_found"}
    started = time.time()
    status = "unknown"
    error = ""
    try:
        base_url = str(provider.get("base_url", "") or "")
        if provider.get("type") == "ollama":
            endpoint = base_url.rstrip("/")
            endpoint = endpoint.replace("/api/generate", "/api/tags")
            with urllib.request.urlopen(endpoint, timeout=timeout) as response:
                status = "healthy" if response.status < 500 else "error"
        elif not base_url:
            status = "not_configured"
            error = "base_url_missing"
        elif provider_api_key(provider) or provider.get("type") in {"custom", "morecode"}:
            request = urllib.request.Request(base_url, method="HEAD")
            try:
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    status = "healthy" if response.status < 500 else "error"
            except urllib.error.HTTPError as exc:
                status = "reachable" if exc.code in {401, 403, 404, 405, 501} else "error"
                error = f"http_{exc.code}"
        else:
            status = "not_configured"
            error = "api_key_missing"
    except (OSError, urllib.error.URLError, TimeoutError) as exc:
        status = "error"
        error = str(exc)[:240]
    latency_ms = int((time.time() - started) * 1000)
    record_provider_result(
        provider_id,
        ok=status in {"healthy", "reachable"},
        latency_ms=latency_ms,
        error=error,
        health=status,
        path=path,
    )
    return {"provider": provider_id, "status": status, "latency_ms": latency_ms, "error": error}


def encrypt_api_key(value: str) -> str:
    raw = value.encode("utf-8")
    nonce = hashlib.sha256(f"{time.time()}:{os.getpid()}".encode("utf-8")).digest()[:12]
    stream = _keystream(nonce, len(raw))
    cipher = bytes(byte ^ stream[index] for index, byte in enumerate(raw))
    mac = hmac.new(_secret_key(), nonce + cipher, hashlib.sha256).digest()[:16]
    return base64.urlsafe_b64encode(nonce + mac + cipher).decode("ascii")


def decrypt_api_key(value: str) -> str:
    try:
        payload = base64.urlsafe_b64decode(value.encode("ascii"))
        nonce, mac, cipher = payload[:12], payload[12:28], payload[28:]
        expected = hmac.new(_secret_key(), nonce + cipher, hashlib.sha256).digest()[:16]
        if not hmac.compare_digest(mac, expected):
            return ""
        stream = _keystream(nonce, len(cipher))
        raw = bytes(byte ^ stream[index] for index, byte in enumerate(cipher))
        return raw.decode("utf-8")
    except (ValueError, UnicodeDecodeError, OSError):
        return ""


def _load_config(path: str | None = None) -> dict[str, Any]:
    target = Path(path) if path else CONFIG_PATH
    if not target.exists():
        return {}
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _normalize_registry(value: Mapping[str, Any]) -> dict[str, Any]:
    default = default_provider_registry()
    providers_by_id = {provider["id"]: provider for provider in default["providers"]}
    incoming = value if isinstance(value, Mapping) else {}
    for provider in incoming.get("providers", []):
        if not isinstance(provider, Mapping):
            continue
        provider_id = _safe_provider_id(str(provider.get("id") or provider.get("type") or "custom"))
        provider_type = str(provider.get("type") or provider_id)
        base = providers_by_id.get(provider_id, {}).copy()
        if not base:
            meta = SUPPORTED_PROVIDER_TYPES.get(provider_type, SUPPORTED_PROVIDER_TYPES["custom"])
            base = {
                "id": provider_id,
                "type": provider_type,
                "label": meta["label"],
                "enabled": True,
                "base_url": meta["base_url"],
                "model": meta["model"],
                "api_key_encrypted": "",
                "health": "unknown",
                "last_latency_ms": None,
                "last_error": "",
            }
        base.update({key: provider[key] for key in provider if key != "api_key"})
        base["id"] = provider_id
        base["type"] = provider_type if provider_type in SUPPORTED_PROVIDER_TYPES else "custom"
        providers_by_id[provider_id] = base
    active = str(incoming.get("active_provider") or default["active_provider"])
    fallback = incoming.get("fallback_chain", default["fallback_chain"])
    fallback_chain = [_safe_provider_id(str(item)) for item in fallback if str(item).strip()] if isinstance(fallback, list) else default["fallback_chain"]
    return {
        "active_provider": _safe_provider_id(active),
        "fallback_chain": fallback_chain,
        "providers": list(providers_by_id.values()),
    }


def _registry_from_legacy(legacy: Any) -> dict[str, Any]:
    registry = default_provider_registry()
    if not isinstance(legacy, Mapping):
        return registry
    provider_name = str(legacy.get("provider", "openai")).strip().lower()
    provider_id = {
        "openai": "openai",
        "gpt": "openai",
        "claude": "claude",
        "anthropic": "claude",
        "ollama": "ollama",
        "local": "ollama",
        "custom api": "custom",
        "custom": "custom",
    }.get(provider_name, provider_name or "openai")
    registry["active_provider"] = provider_id
    for provider in registry["providers"]:
        if provider["id"] == provider_id:
            provider["enabled"] = True
            provider["base_url"] = str(legacy.get("base_url") or provider.get("base_url") or "")
            provider["model"] = str(legacy.get("model") or provider.get("model") or "")
            key = str(legacy.get("api_key") or "")
            if key:
                provider["api_key_encrypted"] = encrypt_api_key(key)
    return registry


def _legacy_llm_from_registry(registry: Mapping[str, Any]) -> dict[str, Any]:
    provider = get_provider(str(registry.get("active_provider")), None) or {}
    for item in registry.get("providers", []):
        if isinstance(item, Mapping) and item.get("id") == registry.get("active_provider"):
            provider = dict(item)
            break
    return {
        "provider": str(provider.get("label") or provider.get("id") or "OpenAI"),
        "api_key": "***" if provider.get("api_key_encrypted") else "",
        "base_url": str(provider.get("base_url") or ""),
        "model": str(provider.get("model") or ""),
    }


def _safe_provider_id(value: str) -> str:
    clean = "".join(ch for ch in value.strip().lower().replace(" ", "_") if ch.isalnum() or ch in {"_", "-"})
    return clean or "custom"


def _secret_key() -> bytes:
    seed = os.environ.get("ATLAS_CONFIG_SECRET")
    if not seed:
        seed = f"{platform.node()}:{os.environ.get('USER', '')}:{Path.home()}"
    return hashlib.sha256(seed.encode("utf-8")).digest()


def _keystream(nonce: bytes, length: int) -> bytes:
    blocks = []
    counter = 0
    while sum(len(block) for block in blocks) < length:
        blocks.append(hashlib.sha256(_secret_key() + nonce + counter.to_bytes(4, "big")).digest())
        counter += 1
    return b"".join(blocks)[:length]
