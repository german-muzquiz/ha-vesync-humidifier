"""DataUpdateCoordinator for vesync_humidifiers."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    VesyncApiAuthenticationError,
    VesyncApiClientError,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import VesyncConfigEntry
from .const import DOMAIN, LOGGER, SCAN_INTERVAL


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class VesyncDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: VesyncConfigEntry

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """
        Update data via library.
        Data: dictionary of humidifer cid and humidifier instance as returned by vesync API.
        """
        try:
            LOGGER.info("Updating data")
            return await self.config_entry.runtime_data.client.async_get_data()
        except VesyncApiAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except VesyncApiClientError as exception:
            raise UpdateFailed(exception) from exception
