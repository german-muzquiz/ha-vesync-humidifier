"""VeSync API Client."""

from __future__ import annotations

from typing import Any, Optional

import aiohttp
from pyvesync import VeSync


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

    vesync_manager: Optional[VeSync]

    def __init__(
        self,
        username: str,
        password: str,
        timezone: str,
    ) -> None:
        """Vesync API Client."""
        self._username = username
        self._password = password
        self._timezone = timezone

    async def async_get_data(self) -> Any:
        """Get data from the API."""
        if not self.vesync_manager:
            self.vesync_manager = VeSync(self._username, self._password, self._timezone, debug=False, redact=True)
            if not self.vesync_manager.login():
                raise VesyncApiAuthenticationError("Invalid credentials")

        self.vesync_manager.update()
        return self.vesync_manager.fans
