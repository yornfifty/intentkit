import asyncio
import logging
import time
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


class DeribitCredential:
    def __init__(
        self,
        access_token: str,
        expires_in: int,
        refresh_token: str,
        scope: str,
        token_type: str,
    ):
        self.access_token: str = access_token
        self.expires_in: int = expires_in
        self.refresh_token: str = refresh_token
        self.scope: str = scope
        self.token_type: str = token_type
        self.expiry_time: float = time.time() + expires_in

    def is_expired(self) -> bool:
        """Check if the token has expired, with a 60-second early buffer."""
        return time.time() > (self.expiry_time - 60)


class DeribitApi:
    def __init__(self, client_id: str, client_secret: str, base_url: str):
        self.base_url: str = base_url.rstrip("/")
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.credentials: Optional[DeribitCredential] = None
        self._refresh_lock = asyncio.Lock()
        self._client = httpx.AsyncClient()  # using the same http client instance

    async def getCredential(self) -> DeribitCredential:
        """Gets a valid credential, ensuring only one refresh happens at a time."""

        logger.error("getCredential 1")

        # --- Optimistic check first (avoids locking if token is valid) ---
        if self.credentials and not self.credentials.is_expired():
            return self.credentials

        logger.error("getCredential 2")
        # --- Token is None or expired, need to potentially refresh ---
        async with self._refresh_lock:
            logger.error("getCredential 3")
            # --- Double-check inside the lock ---
            # Another coroutine might have refreshed the token while we were
            # waiting for the lock. Check again to prevent redundant refresh.
            if self.credentials and not self.credentials.is_expired():
                return self.credentials

            logger.error("getCredential 4")
            # --- Still None or expired: Proceed with the refresh ---
            # Only the coroutine holding the lock will execute this block.
            # print("Acquired lock and refreshing token...") # Optional: for debugging
            refreshed_credential = await self._refreshCredential()
            # print("Token refreshed and lock released.") # Optional: for debugging
            logger.error("getCredential 5")
            return refreshed_credential
            # Lock is automatically released when exiting the 'async with' block

    async def _refreshCredential(self) -> DeribitCredential:
        """Fetch new credentials from the API."""
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }

        url = f"{self.base_url}/api/v2/public/auth"

        response = await self._client.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            result = data["result"]

            new_credential = DeribitCredential(
                access_token=result["access_token"],
                expires_in=result["expires_in"],
                refresh_token=result["refresh_token"],
                scope=result["scope"],
                token_type=result["token_type"],
            )

            self.credentials = new_credential
            return self.credentials
        else:
            raise Exception(f"Error: {response.status_code}, {response.text}")

    async def get(
        self, path: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Middleware for authenticated GET requests."""
        credential = await self.getCredential()

        headers = {
            "Authorization": f"Bearer {credential.access_token}",
            "Content-Type": "application/json",
        }

        url = f"{self.base_url}{path}"
        logger.info(f"Sending GET request to {url} with params {params}")

        try:
            response = await self._client.get(url, params=params, headers=headers)
            logger.info(f"response {response.json()}")

            response.raise_for_status()
        except httpx.RequestError as exc:
            logger.error(f"Network error while requesting {exc.request.url!r}: {exc}")
            raise Exception(
                f"Network error while requesting {exc.request.url!r}: {exc}"
            ) from exc
        except httpx.HTTPStatusError as exc:
            try:
                error_data = exc.response.json()
            except Exception:
                error_data = {"error": exc.response.text}
            logger.error(f"Backend error {exc.response.status_code}: {error_data}")
            raise Exception(
                f"Authenticated GET error: {exc.response.status_code}, {error_data}"
            ) from exc

        logger.info(f"Received response: {response.status_code}")
        return response.json()
