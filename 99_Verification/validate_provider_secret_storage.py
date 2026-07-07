"""Validate provider secret storage safety without touching real Keychain."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.llm.provider_registry import (  # noqa: E402
    decrypt_api_key,
    default_provider_registry,
    load_provider_registry,
    safe_registry_view,
    update_provider_registry,
)


def main() -> None:
    previous = os.environ.get("ATLAS_DISABLE_KEYCHAIN")
    os.environ["ATLAS_DISABLE_KEYCHAIN"] = "1"
    try:
        with TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "user_config.json")
            registry = default_provider_registry()
            for provider in registry["providers"]:
                if provider["id"] == "openai":
                    provider["api_key"] = "atlas_fake_validation_secret"
                    provider["enabled"] = True
            update_provider_registry(registry, path)
            loaded = load_provider_registry(path)
            openai = next(provider for provider in loaded["providers"] if provider["id"] == "openai")
            assert openai["api_key_storage"] == "local_secret_storage"
            assert decrypt_api_key(openai["api_key_encrypted"]) == "atlas_fake_validation_secret"
            safe = safe_registry_view(loaded)
            safe_openai = next(provider for provider in safe["providers"] if provider["id"] == "openai")
            assert safe_openai["api_key"] == "***"
            assert "api_key_encrypted" not in safe_openai
            assert "api_key_keychain_account" not in safe_openai
            assert "atlas_fake_validation_secret" not in str(safe)

            for provider in safe["providers"]:
                if provider["id"] == "openai":
                    provider["model"] = "gpt-validation"
            update_provider_registry(safe, path)
            reloaded = load_provider_registry(path)
            reloaded_openai = next(provider for provider in reloaded["providers"] if provider["id"] == "openai")
            assert decrypt_api_key(reloaded_openai["api_key_encrypted"]) == "atlas_fake_validation_secret"
            assert reloaded_openai["model"] == "gpt-validation"
    finally:
        if previous is None:
            os.environ.pop("ATLAS_DISABLE_KEYCHAIN", None)
        else:
            os.environ["ATLAS_DISABLE_KEYCHAIN"] = previous

    print("Provider secret storage validation PASS")


if __name__ == "__main__":
    main()
