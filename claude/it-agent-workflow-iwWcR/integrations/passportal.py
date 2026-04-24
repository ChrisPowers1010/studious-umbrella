"""
N-able Passportal API client.

Docs: https://documentation.n-able.com/passportal/userguide/content/passportal-api.htm
Auth: Bearer token via x-api-key header (or Authorization: Bearer depending on version).
"""

import logging
from typing import Any

import httpx

import config

logger = logging.getLogger(__name__)


class PassportalClient:
    def __init__(self) -> None:
        self._http = httpx.Client(
            base_url=config.PASSPORTAL_BASE_URL,
            headers={
                "Authorization": f"Bearer {config.PASSPORTAL_API_KEY}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=30,
        )

    def _get(self, path: str, params: dict | None = None) -> Any:
        r = self._http.get(path, params=params)
        r.raise_for_status()
        return r.json()

    # ------------------------------------------------------------------
    # Clients / Sites
    # ------------------------------------------------------------------

    def list_clients(self) -> list[dict]:
        """Return all Passportal clients (companies)."""
        data = self._get("/api/v1/clients")
        return data if isinstance(data, list) else data.get("data", [])

    def search_clients(self, name: str) -> list[dict]:
        """Search clients by name."""
        clients = self.list_clients()
        name_lower = name.lower()
        return [c for c in clients if name_lower in c.get("name", "").lower()]

    # ------------------------------------------------------------------
    # Credentials / Passwords
    # ------------------------------------------------------------------

    def search_credentials(
        self,
        client_id: str | None = None,
        search_term: str | None = None,
        credential_type: str | None = None,
    ) -> list[dict]:
        """
        Search credentials across the vault.

        Pass client_id to scope to a specific client.
        Pass search_term to filter by name/username/url.
        """
        params: dict[str, Any] = {}
        if client_id:
            params["clientId"] = client_id
        if search_term:
            params["search"] = search_term
        if credential_type:
            params["type"] = credential_type

        path = "/api/v1/passwords"
        data = self._get(path, params=params if params else None)
        return data if isinstance(data, list) else data.get("data", [])

    def get_credential(self, credential_id: str) -> dict:
        """Retrieve a single credential record including the password value."""
        data = self._get(f"/api/v1/passwords/{credential_id}")
        return data if isinstance(data, dict) else {}

    def close(self) -> None:
        self._http.close()