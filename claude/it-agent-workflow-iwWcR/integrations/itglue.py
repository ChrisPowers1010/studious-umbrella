"""
ITGlue API client.

Docs: https://api.itglue.com/developer/
Auth: x-api-key header
Format: JSON:API (responses wrapped in {"data": [...], "meta": {...}})
"""

import logging
from typing import Any

import httpx

import config

logger = logging.getLogger(__name__)


def _unwrap(response_json: dict) -> list[dict] | dict:
    """ITGlue wraps results in {"data": ...}. Normalise to a plain list or dict."""
    data = response_json.get("data", response_json)
    if isinstance(data, list):
        return [_flatten(item) for item in data]
    return _flatten(data)


def _flatten(item: dict) -> dict:
    """Merge JSON:API 'attributes' into the top-level record dict."""
    result = {"id": item.get("id")}
    result.update(item.get("attributes", {}))
    return result


class ITGlueClient:
    def __init__(self) -> None:
        self._http = httpx.Client(
            base_url=config.ITGLUE_BASE_URL,
            headers={
                "x-api-key": config.ITGLUE_API_KEY,
                "Content-Type": "application/vnd.api+json",
            },
            timeout=30,
        )

    def _get(self, path: str, params: dict | None = None) -> Any:
        r = self._http.get(path, params=params)
        r.raise_for_status()
        return r.json()

    # ------------------------------------------------------------------
    # Organizations
    # ------------------------------------------------------------------

    def search_organizations(self, name: str) -> list[dict]:
        """Find organizations whose name contains *name*."""
        data = self._get("/organizations", params={"filter[name]": name})
        return _unwrap(data)  # type: ignore[return-value]

    def get_organization(self, org_id: int) -> dict:
        data = self._get(f"/organizations/{org_id}")
        return _unwrap(data)  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Configurations (devices / assets)
    # ------------------------------------------------------------------

    def get_configurations(
        self, org_id: int, name_filter: str | None = None
    ) -> list[dict]:
        """Return configurations (servers, workstations, network gear) for an org."""
        params: dict[str, Any] = {"filter[organization-id]": org_id}
        if name_filter:
            params["filter[name]"] = name_filter
        data = self._get("/configurations", params=params)
        return _unwrap(data)  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Passwords / Credentials
    # ------------------------------------------------------------------

    def get_passwords(
        self, org_id: int, name_filter: str | None = None
    ) -> list[dict]:
        """
        Return password records for an org.

        Note: the returned dicts include 'name', 'username', 'password',
        and 'url' fields depending on your ITGlue API key permissions.
        """
        params: dict[str, Any] = {"filter[organization-id]": org_id}
        if name_filter:
            params["filter[name]"] = name_filter
        data = self._get("/passwords", params=params)
        return _unwrap(data)  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Contacts
    # ------------------------------------------------------------------

    def get_contacts(self, org_id: int) -> list[dict]: