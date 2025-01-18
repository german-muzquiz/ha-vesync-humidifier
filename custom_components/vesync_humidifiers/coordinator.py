"""DataUpdateCoordinator for vesync_humidifiers."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any, Optional

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.dispatcher import async_dispatcher_send
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
        self._previous_data: Optional[dict[str, Any]] = None

    async def _async_update_data(self) -> dict[str, Any]:
        """
        Update data via library.
        Data: dictionary of humidifer cid and humidifier instance as returned by vesync API.
        """
        try:
            new_data = await self.config_entry.runtime_data.client.async_get_data()

            # Check for state changes
            if self._previous_data is not None:
                for device_id, current_device in new_data.items():
                    if device_id in self._previous_data:
                        previous_device = self._previous_data[device_id]
                        if self._has_state_changed(previous_device, current_device):
                            LOGGER.debug(
                                "Device %s state changed externally: %s -> %s",
                                device_id,
                                previous_device,
                                current_device,
                            )
                            # Force an immediate update of the entity
                            async_dispatcher_send(
                                self.hass,
                                f"{DOMAIN}_device_update_{device_id}",
                            )

            self._previous_data = new_data
            return new_data
        except VesyncApiAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except VesyncApiClientError as exception:
            raise UpdateFailed(exception) from exception

    @staticmethod
    def _has_state_changed(previous: Any, current: Any) -> bool:
        """Determine if the device state has changed."""
        return (
            previous.device_status != current.device_status
            or previous.auto_humidity != current.auto_humidity
            or previous.humidity != current.humidity
            or previous.connection_status != current.connection_status
        )
