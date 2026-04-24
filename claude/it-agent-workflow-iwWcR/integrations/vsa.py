"""
Kaseya VSA REST API client.

Docs: https://{your-vsa}/api/v1.0/swagger/ui/index
Auth: Two-step — get a challenge token, hash the credentials, exchange for a Bearer token.

VSA auth steps:
  1. GET  /api/v1.0/auth  → {"Result": {"RandomNumber": "...", "SHA256Hash": "..."}}
  2. Hash: SHA256(SHA256(password) + SHA256(username + SHA256(SHA256(password))) + random_number)
  3. POST /api/v1.0/auth with the computed hash → {"Result": {"Token": "Bearer ..."}}
"""

import hashlib
import logging
from typing import Any

import httpx

import config

logger = logging.getLogger(__name__)


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


class VSAClient:
    def __init__(self) -> None:
        self._base_url = config.VSA_BASE_URL.rstrip("/")
        self._username = config.VSA_USERNAME
        self._password = config.VSA_PASSWORD
        self._token: str | None = None
        self._http: httpx.Client | None = None

    def _authenticate(self) -> str:
        # Step 1: get the random challenge
        r = httpx.get(
            f"{self._base_url}/api/v1.0/auth",
            params={"username": self._username, "rememberMe": "false"},
            timeout=15,
        )
        r.raise_for_status()
        result = r.json().get("Result", {})
        random_number = result.get("RandomNumber", "")

        # Step 2: compute the hashed credential
        pw_hash = _sha256(self._password)
        username_pw_hash = _sha256(self._username + _sha256(_sha256(self._password)))
        encoded_pw = _sha256(pw_hash + username_pw_hash + random_number)

        # Step 3: exchange for a Bearer token
        r2 = httpx.post(
            f"{self._base_url}/api/v1.0/auth",
            json={
                "username": self._username,
                "password": encoded_pw,
                "rememberMe": False,
            },
            timeout=15,
        )
        r2.raise_for_status()
        token = r2.json().get("Result", {}).get("Token", "")
        if not token:
            raise ValueError("VSA authentication failed: no token returned")
        return token

    def _client(self) -> httpx.Client:
        if self._http is None:
            self._token = self._authenticate()
            self._http = httpx.Client(
                base_url=f"{self._base_url}/api/v1.0",
                headers={
                    "Authorization": self._token,
                    "Content-Type": "application/json",
                },
                timeout=30,
            )
        return self._http

    def _get(self, path: str, params: dict | None = None) -> Any:
        r = self._client().get(path, params=params)
        if r.status_code == 401:
            # Token expired — re-authenticate once
            self._http = None
            r = self._client().get(path, params=params)
        r.raise_for_status()
        return r.json()

    def _put(self, path: str, body: dict | None = None) -> Any:
        r = self._client().put(path, json=body or {})
        r.raise_for_status()
        return r.json()

    def _post(self, path: str, body: dict | None = None) -> Any:
        r = self._client().post(path, json=body or {})
        r.raise_for_status()
        return r.json()

    # ------------------------------------------------------------------