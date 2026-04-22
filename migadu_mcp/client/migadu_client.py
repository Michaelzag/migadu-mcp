"""HTTP client for the Migadu API."""

from __future__ import annotations

import base64
from typing import Any

import httpx


class MigaduAPIError(Exception):
    """Raised for non-success responses from the Migadu API."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        super().__init__(message)


class MigaduClient:
    """Async HTTP client for Migadu. The underlying httpx.AsyncClient is created lazily
    and reused for the lifetime of this instance. Call `aclose()` on shutdown.

    Migadu returns HTTP 500 on successful DELETEs. `delete()` treats that as success.
    """

    BASE_URL = "https://api.migadu.com/v1"

    def __init__(self, email: str, api_key: str) -> None:
        credentials = base64.b64encode(f"{email}:{api_key}".encode()).decode()
        self._headers = {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json",
        }
        self._client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers=self._headers,
                timeout=httpx.Timeout(30.0, connect=10.0),
            )
        return self._client

    async def aclose(self) -> None:
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
        self._client = None

    async def request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        client = self._get_client()
        response = await client.request(method, path, **kwargs)
        if response.status_code >= 400:
            raise MigaduAPIError(response.status_code, response.text)
        if not response.content:
            return {}
        return response.json()  # type: ignore[no-any-return]

    async def get(self, path: str, **kwargs: Any) -> dict[str, Any]:
        return await self.request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs: Any) -> dict[str, Any]:
        return await self.request("POST", path, **kwargs)

    async def put(self, path: str, **kwargs: Any) -> dict[str, Any]:
        return await self.request("PUT", path, **kwargs)

    async def patch(self, path: str, **kwargs: Any) -> dict[str, Any]:
        return await self.request("PATCH", path, **kwargs)

    async def delete(self, path: str) -> None:
        """DELETE returning None on success.

        Migadu has a known bug where successful DELETEs return HTTP 500.
        This method treats 200 and 500 as success. 404 is also treated as
        success (idempotent delete — already gone). Other errors raise.
        """
        client = self._get_client()
        response = await client.request("DELETE", path)
        if response.status_code in (200, 204, 404, 500):
            return None
        raise MigaduAPIError(response.status_code, response.text)
