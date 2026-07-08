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
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlsplit, urlunsplit


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
                "api_key_storage": "none",
                "api_key_keychain_account": "",
                "health": "unknown",
                "last_latency_ms": None,
                "last_error": "",
                "available_models": [],
                "last_models_error": "",
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
    target = _config_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(config, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return safe_registry_view(normalized)


def update_provider_registry(payload: Mapping[str, Any], path: str | None = None) -> dict[str, Any]:
    incoming = payload.get("llm_registry", payload)
    existing_registry = _normalize_registry(_load_config(path).get("llm_registry", default_provider_registry()))
    existing_keys = {
        str(provider.get("id")): str(provider.get("api_key_encrypted") or "")
        for provider in existing_registry.get("providers", [])
        if isinstance(provider, Mapping)
    }
    existing_keychain_refs = {
        str(provider.get("id")): str(provider.get("api_key_keychain_account") or "")
        for provider in existing_registry.get("providers", [])
        if isinstance(provider, Mapping)
    }
    existing_storage = {
        str(provider.get("id")): str(provider.get("api_key_storage") or "none")
        for provider in existing_registry.get("providers", [])
        if isinstance(provider, Mapping)
    }
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
            keychain_account = _keychain_account(str(item.get("id")))
            if _store_keychain_secret(keychain_account, raw_key):
                item["api_key_encrypted"] = ""
                item["api_key_keychain_account"] = keychain_account
                item["api_key_storage"] = "macos_keychain"
            else:
                item["api_key_encrypted"] = encrypt_api_key(raw_key)
                item["api_key_keychain_account"] = ""
                item["api_key_storage"] = "local_secret_storage"
        elif not item.get("api_key_encrypted") and existing_keys.get(str(item.get("id"))):
            item["api_key_encrypted"] = existing_keys[str(item.get("id"))]
            item["api_key_storage"] = item.get("api_key_storage") or "local_secret_storage"
        elif not item.get("api_key_keychain_account") and existing_keychain_refs.get(str(item.get("id"))):
            item["api_key_keychain_account"] = existing_keychain_refs[str(item.get("id"))]
            item["api_key_storage"] = existing_storage.get(str(item.get("id")), "macos_keychain")
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
    keychain_account = str(provider.get("api_key_keychain_account", "") or "")
    if keychain_account:
        keychain_value = _read_keychain_secret(keychain_account)
        if keychain_value:
            return keychain_value
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
        item["api_key"] = "***" if item.get("api_key_encrypted") or item.get("api_key_keychain_account") else ""
        item.pop("api_key_encrypted", None)
        item.pop("api_key_keychain_account", None)
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
    target = _config_path(path)
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
        elif provider_api_key(provider) or _is_local_url(base_url) or provider.get("type") in {"custom", "morecode"}:
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


def list_provider_models(provider_id: str, path: str | None = None, timeout: float = 8.0) -> dict[str, Any]:
    """Fetch and cache model names exposed by a provider endpoint."""

    provider = get_provider(provider_id, path)
    if not provider:
        return {"provider": provider_id, "status": "missing", "models": [], "latency_ms": 0, "error": "provider_not_found"}
    started = time.time()
    models: list[str] = []
    status = "unknown"
    error = ""
    try:
        base_url = str(provider.get("base_url", "") or "")
        if not base_url:
            status = "not_configured"
            error = "base_url_missing"
        elif provider.get("type") == "ollama":
            endpoint = base_url.rstrip("/").replace("/api/generate", "/api/tags")
            with urllib.request.urlopen(endpoint, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8") or "{}")
            models = _extract_model_names(payload)
            status = "ok"
        elif provider_api_key(provider) or _is_local_url(base_url) or provider.get("type") in {"custom", "morecode"}:
            endpoint = _models_endpoint(base_url)
            request = urllib.request.Request(endpoint, headers=_model_request_headers(provider), method="GET")
            try:
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    payload = json.loads(response.read().decode("utf-8") or "{}")
            except urllib.error.HTTPError as exc:
                if exc.code != 401 or not _is_local_url(endpoint):
                    raise
                request = urllib.request.Request(endpoint, headers={"Accept": "application/json"}, method="GET")
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    payload = json.loads(response.read().decode("utf-8") or "{}")
            models = _extract_model_names(payload)
            status = "ok"
        else:
            status = "not_configured"
            error = "api_key_missing"
    except urllib.error.HTTPError as exc:
        status = "error"
        error = f"http_{exc.code}"
    except (OSError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        status = "error"
        error = str(exc)[:240]
    latency_ms = int((time.time() - started) * 1000)
    _record_provider_models(provider_id, models, status=status, latency_ms=latency_ms, error=error, path=path)
    return {"provider": provider_id, "status": status, "models": models, "latency_ms": latency_ms, "error": error}


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
    target = _config_path(path)
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
                "api_key_storage": "none",
                "api_key_keychain_account": "",
                "health": "unknown",
                "last_latency_ms": None,
                "last_error": "",
                "available_models": [],
                "last_models_error": "",
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
                provider["api_key_storage"] = "local_secret_storage"
    return registry


def _legacy_llm_from_registry(registry: Mapping[str, Any]) -> dict[str, Any]:
    provider = get_provider(str(registry.get("active_provider")), None) or {}
    for item in registry.get("providers", []):
        if isinstance(item, Mapping) and item.get("id") == registry.get("active_provider"):
            provider = dict(item)
            break
    return {
        "provider": str(provider.get("label") or provider.get("id") or "OpenAI"),
        "api_key": "***" if provider.get("api_key_encrypted") or provider.get("api_key_keychain_account") else "",
        "base_url": str(provider.get("base_url") or ""),
        "model": str(provider.get("model") or ""),
    }


def _safe_provider_id(value: str) -> str:
    clean = "".join(ch for ch in value.strip().lower().replace(" ", "_") if ch.isalnum() or ch in {"_", "-"})
    return clean or "custom"


def _record_provider_models(
    provider_id: str,
    models: list[str],
    *,
    status: str,
    latency_ms: int,
    error: str,
    path: str | None = None,
) -> None:
    config = _load_config(path)
    registry = _normalize_registry(config.get("llm_registry", default_provider_registry()))
    for provider in registry["providers"]:
        if provider.get("id") == provider_id:
            if status == "ok":
                provider["available_models"] = models
            provider["last_models_status"] = status
            provider["last_models_latency_ms"] = int(latency_ms)
            provider["last_models_error"] = str(error)[:240]
            provider["last_models_checked_at"] = int(time.time())
            break
    config["llm_registry"] = registry
    target = _config_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(config, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _config_path(path: str | None = None) -> Path:
    configured = path or os.environ.get("ATLAS_USER_CONFIG")
    return Path(configured) if configured else CONFIG_PATH


def _keychain_available() -> bool:
    if os.environ.get("ATLAS_DISABLE_KEYCHAIN") == "1":
        return False
    return platform.system() == "Darwin"


def _keychain_service() -> str:
    return os.environ.get("ATLAS_KEYCHAIN_SERVICE", "AtlasOS LLM Providers")


def _keychain_account(provider_id: str) -> str:
    return f"atlas-llm-{_safe_provider_id(provider_id)}"


def _store_keychain_secret(account: str, value: str) -> bool:
    if not _keychain_available() or not value:
        return False
    try:
        subprocess.run(
            [
                "security",
                "add-generic-password",
                "-a",
                account,
                "-s",
                _keychain_service(),
                "-w",
                value,
                "-U",
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


def _read_keychain_secret(account: str) -> str:
    if not _keychain_available() or not account:
        return ""
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-a", account, "-s", _keychain_service(), "-w"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return ""
    return result.stdout.strip()


def _models_endpoint(base_url: str) -> str:
    url = base_url.rstrip("/")
    for suffix in ("/chat/completions", "/responses", "/messages", "/generate"):
        if url.endswith(suffix):
            url = url[: -len(suffix)]
            break
    if url.endswith("/v1") or url.endswith("/v3"):
        return url + "/models"
    parsed = urlsplit(url)
    path = parsed.path.rstrip("/")
    if path.endswith("/v1") or path.endswith("/v3"):
        endpoint_path = path + "/models"
    else:
        endpoint_path = path + "/models"
    return urlunsplit((parsed.scheme, parsed.netloc, endpoint_path, "", ""))


def _is_local_url(value: str) -> bool:
    host = urlsplit(value).hostname or ""
    return host in {"localhost", "127.0.0.1", "::1"}


def _model_request_headers(provider: Mapping[str, Any]) -> dict[str, str]:
    headers = {"Accept": "application/json"}
    api_key = provider_api_key(provider)
    if api_key:
        if provider.get("type") == "claude":
            headers["x-api-key"] = api_key
            headers["anthropic-version"] = "2023-06-01"
        else:
            headers["Authorization"] = f"Bearer {api_key}"
    return headers


def _extract_model_names(payload: Any) -> list[str]:
    candidates: list[Any]
    if isinstance(payload, Mapping):
        if isinstance(payload.get("data"), list):
            candidates = payload["data"]
        elif isinstance(payload.get("models"), list):
            candidates = payload["models"]
        elif isinstance(payload.get("tags"), list):
            candidates = payload["tags"]
        else:
            candidates = [payload]
    elif isinstance(payload, list):
        candidates = payload
    else:
        candidates = []
    names: list[str] = []
    for item in candidates:
        if isinstance(item, Mapping):
            value = item.get("id") or item.get("name") or item.get("model")
        else:
            value = item
        clean = str(value or "").strip()
        if clean and clean not in names:
            names.append(clean[:160])
    return sorted(names)[:200]


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
