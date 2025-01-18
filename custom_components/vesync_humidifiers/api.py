"""VeSync API Client."""

from __future__ import annotations

import asyncio
from typing import Any, Optional

import aiohttp
from pyvesync import VeSync

from .const import LOGGER


class VesyncApiClientError(Exception):
    """Exception to indicate a general API error."""


class VesyncApiClientCommunicationError(
    VesyncApiClientError,
):
    """Exception to indicate a communication error."""


class VesyncApiAuthenticationError(
    VesyncApiClientError,
):
    """Exception to indicate an authentication error."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise VesyncApiAuthenticationError(
            msg,
        )
    response.raise_for_status()


class VesyncApiClient:
    """Vesync API Client."""

    vesync_manager: Optional[VeSync] = None

    def __init__(
        self,
        username: str,
        password: str,
    ) -> None:
        """Vesync API Client."""
        self._username = username
        self._password = password
        self.vesync_manager = None

    async def async_get_data(self) -> Any:
        """Get data from the API."""
        LOGGER.info("Getting data from API")
        if not self.vesync_manager:
            self.vesync_manager = VeSync(self._username, self._password, "America/Monterrey", debug=False, redact=True)
            if not await self.run_blocking_call(self.vesync_manager.login):
                raise VesyncApiAuthenticationError("Invalid credentials")

        await self.run_blocking_call(self.vesync_manager.update)
        return self.vesync_manager.fans

    async def run_blocking_call(self, f, *args):
        LOGGER.info("Running blocking call")
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, f, *args)
