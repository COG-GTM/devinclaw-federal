"""Vault Abstraction — pluggable secrets management interface.

Provides a common contract for secrets storage with two implementations:
  - EnvVarBackend: reads secrets from environment variables (default / air-gapped)
  - HashiCorpVaultBackend: stub for HashiCorp Vault integration (production)

STIG V-220633/634: No hardcoded secrets.  All secrets accessed via this layer.
"""

from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger("devinclaw.vault")


class VaultBackend(ABC):
    """Abstract secrets management interface.

    Every backend MUST implement get_secret and store_secret.
    Implementations should never log secret values.
    """

    @abstractmethod
    async def get_secret(self, key: str) -> str | None:
        """Retrieve a secret by key.  Returns None if not found."""

    @abstractmethod
    async def store_secret(self, key: str, value: str, metadata: dict[str, Any] | None = None) -> bool:
        """Store a secret.  Returns True on success."""

    @abstractmethod
    async def delete_secret(self, key: str) -> bool:
        """Delete a secret.  Returns True if deleted."""

    @abstractmethod
    async def list_keys(self, prefix: str = "") -> list[str]:
        """List available secret keys, optionally filtered by prefix."""

    async def health_check(self) -> bool:
        """Verify the backend is reachable."""
        return True


# ---------------------------------------------------------------------------
# Environment Variable Backend (default — works air-gapped)
# ---------------------------------------------------------------------------


class EnvVarBackend(VaultBackend):
    """Reads secrets from OS environment variables.

    Convention: keys are upper-cased and prefixed with ``DEVINCLAW_SECRET_``.
    Example: get_secret("devin_api_key") → os.environ["DEVINCLAW_SECRET_DEVIN_API_KEY"]
    """

    PREFIX = "DEVINCLAW_SECRET_"

    def _env_key(self, key: str) -> str:
        return f"{self.PREFIX}{key.upper()}"

    async def get_secret(self, key: str) -> str | None:
        env_key = self._env_key(key)
        value = os.environ.get(env_key)
        if value is None:
            logger.debug("Secret not found in env: %s", env_key)
        return value

    async def store_secret(self, key: str, value: str, metadata: dict[str, Any] | None = None) -> bool:
        env_key = self._env_key(key)
        os.environ[env_key] = value
        logger.info("Secret stored in env: %s", env_key)
        return True

    async def delete_secret(self, key: str) -> bool:
        env_key = self._env_key(key)
        if env_key in os.environ:
            del os.environ[env_key]
            return True
        return False

    async def list_keys(self, prefix: str = "") -> list[str]:
        full_prefix = self._env_key(prefix)
        return [
            k.removeprefix(self.PREFIX).lower()
            for k in os.environ
            if k.startswith(full_prefix)
        ]


# ---------------------------------------------------------------------------
# HashiCorp Vault Backend (stub — production)
# ---------------------------------------------------------------------------


class HashiCorpVaultBackend(VaultBackend):
    """HashiCorp Vault KV-v2 integration (stub).

    In production this would use the ``hvac`` library to communicate with
    a Vault cluster over mTLS.  For now it provides the interface contract
    so that the rest of the codebase can program against it.

    Configuration via environment:
      - VAULT_ADDR: Vault server URL
      - VAULT_TOKEN or VAULT_ROLE_ID + VAULT_SECRET_ID for AppRole auth
      - VAULT_MOUNT_PATH: KV-v2 mount point (default: ``secret``)
    """

    def __init__(
        self,
        addr: str | None = None,
        token: str | None = None,
        mount_path: str = "secret",
        path_prefix: str = "devinclaw/",
    ) -> None:
        self.addr = addr or os.environ.get("VAULT_ADDR", "https://vault.local:8200")
        self.token = token or os.environ.get("VAULT_TOKEN", "")
        self.mount_path = mount_path
        self.path_prefix = path_prefix
        self._connected = False

    async def _ensure_connected(self) -> None:
        if not self._connected:
            logger.info("Connecting to Vault at %s (mount=%s)", self.addr, self.mount_path)
            # In production: initialise hvac client, authenticate via AppRole/Token
            self._connected = True

    async def get_secret(self, key: str) -> str | None:
        await self._ensure_connected()
        path = f"{self.path_prefix}{key}"
        logger.debug("Vault GET %s/%s", self.mount_path, path)
        # Stub: would call self._client.secrets.kv.v2.read_secret_version(path=path)
        return None

    async def store_secret(self, key: str, value: str, metadata: dict[str, Any] | None = None) -> bool:
        await self._ensure_connected()
        path = f"{self.path_prefix}{key}"
        logger.debug("Vault PUT %s/%s", self.mount_path, path)
        # Stub: would call self._client.secrets.kv.v2.create_or_update_secret(path=path, secret={"value": value})
        return True

    async def delete_secret(self, key: str) -> bool:
        await self._ensure_connected()
        path = f"{self.path_prefix}{key}"
        logger.debug("Vault DELETE %s/%s", self.mount_path, path)
        return True

    async def list_keys(self, prefix: str = "") -> list[str]:
        await self._ensure_connected()
        path = f"{self.path_prefix}{prefix}"
        logger.debug("Vault LIST %s/%s", self.mount_path, path)
        return []

    async def health_check(self) -> bool:
        try:
            await self._ensure_connected()
            # Stub: would call self._client.sys.read_health_status()
            return True
        except Exception:
            logger.exception("Vault health check failed")
            return False


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

_BACKENDS: dict[str, type[VaultBackend]] = {
    "env": EnvVarBackend,
    "hashicorp": HashiCorpVaultBackend,
}


def get_vault_backend(backend_type: str = "env", **kwargs: Any) -> VaultBackend:
    """Return a vault backend instance by type name."""
    cls = _BACKENDS.get(backend_type)
    if cls is None:
        raise ValueError(f"Unknown vault backend: {backend_type}. Available: {list(_BACKENDS.keys())}")
    return cls(**kwargs)
