"""
AutoTask REST API client.

Docs: https://webservices2.autotask.net/atservicesrest/swagger/ui/index
Auth: Username + IntegrationCode headers
Zone: auto-discovered from the username's email domain via the zone-info endpoint.
"""

import json
import logging
from typing import Any

import httpx

import config

logger = logging.getLogger(__name__)

# Ticket status codes
STATUS_NEW = 1
STATUS_IN_PROGRESS = 8
STATUS_WAITING_CUSTOMER = 11
STATUS_COMPLETE = 5

# Ticket priorities
PRIORITY_CRITICAL = 1
PRIORITY_HIGH = 2
PRIORITY_MEDIUM = 3
PRIORITY_LOW = 4

# Note publish targets
PUBLISH_ALL = 1       # visible to client
PUBLISH_INTERNAL = 2  # internal only


class AutoTaskClient:
    def __init__(self) -> None:
        self.username = config.AUTOTASK_USERNAME
        self.integration_code = config.AUTOTASK_INTEGRATION_CODE
        self._zone_url = config.AUTOTASK_ZONE_URL or None
        self._http: httpx.Client | None = None

    def _get_zone_url(self) -> str:
        if self._zone_url:
            return self._zone_url
        discovery_url = (
            "https://webservices1.autotask.net/ATServicesRest/V1.0/zoneInformation"
        )
        r = httpx.get(
            discovery_url,
            params={"user": self.username},
            timeout=10,
        )
        r.raise_for_status()
        url = r.json().get("url", "").rstrip("/")
        if not url:
            raise ValueError("AutoTask zone discovery returned empty URL")
        self._zone_url = url
        return url

    def _client(self) -> httpx.Client:
        if self._http is None:
            base = f"{self._get_zone_url()}/ATServicesRest/V1.0"
            self._http = httpx.Client(
                base_url=base,
                headers={
                    "UserName": self.username,
                    "IntegrationCode": self.integration_code,
                    "Content-Type": "application/json",
                },
                timeout=30,
            )
        return self._http

    def _get(self, path: str, params: dict | None = None) -> Any:
        r = self._client().get(path, params=params)
        r.raise_for_status()
        return r.json()

    def _post(self, path: str, body: dict) -> Any:
        r = self._client().post(path, json=body)
        r.raise_for_status()
        return r.json()

    def _patch(self, path: str, body: dict) -> Any:
        r = self._client().patch(path, json=body)
        r.raise_for_status()
        return r.json()

    # ------------------------------------------------------------------
    # Tickets
    # ------------------------------------------------------------------

    def get_ticket(self, ticket_id: int) -> dict:
        """Fetch a single ticket by ID."""
        data = self._get(f"/Tickets/{ticket_id}")
        return data.get("item", data)

    def list_tickets(
        self,