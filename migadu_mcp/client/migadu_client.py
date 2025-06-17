#!/usr/bin/env python3
"""
HTTP client for Migadu API
"""

import base64
from typing import Dict, Any
import httpx


class MigaduAPIError(Exception):
    """Custom exception for Migadu API errors"""

    def __init__(self, status_code: int, message: str, is_success: bool = False):
        self.status_code = status_code
        self.is_success = is_success  # For the 500-means-success bug
        super().__init__(message)


class MigaduClient:
    """Simple HTTP client for Migadu API"""

    def __init__(self, email: str, api_key: str):
        credentials = base64.b64encode(f"{email}:{api_key}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json",
        }
        self.base_url = "https://api.migadu.com/v1"

    async def request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to Migadu API"""
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method, f"{self.base_url}{path}", headers=self.headers, **kwargs
            )

            # Handle the special case of DELETE operations that return 500 but succeed
            if response.status_code == 500 and method == "DELETE":
                raise MigaduAPIError(500, response.text, is_success=True)

            if response.status_code >= 400:
                raise MigaduAPIError(response.status_code, response.text)

            return response.json()
