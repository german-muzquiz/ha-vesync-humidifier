"""Humidifier platform for vesync_humidifiers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.humidifier import HumidifierEntity, HumidifierEntityDescription
from homeassistant.helpers.device_registry import DeviceInfo

from .api import VesyncApiClientCommunicationError
from .entity import VesyncEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import VesyncDataUpdateCoordinator
    from .data import VesyncConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: VesyncConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the humidifier platform."""
    async_add_entities(
        VesyncHumidifier(
            coordinator=entry.runtime_data.coordinator,
            humidifier=humidifier,
        )
        for humidifier in entry.runtime_data.coordinator.data
    )


class VesyncHumidifier(VesyncEntity, HumidifierEntity):
    """vesync_humidifier class."""

    def __init__(
        self,
        coordinator: VesyncDataUpdateCoordinator,
        humidifier: Any,  # Data coming from vesync api
    ) -> None:
        """Initialize the humidifier class."""
        super().__init__(coordinator)
        self._attr_unique_id = humidifier.cid
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    coordinator.config_entry.domain,
                    humidifier.cid,
                ),
            },
            name=humidifier.device_name,
            model=humidifier.device_type,
        )
        self.entity_description = HumidifierEntityDescription(
            key=f"vesync_humidifier_{humidifier.cid}",
            name="VeSync Humidifier",
            icon="mdi:format-quote-close",
        )
        self.humidifier = humidifier
        self._attr_current_humidity = humidifier.humidity

    @property
    def is_on(self) -> bool:
        """Return true if the humidifier is on."""
        return self.humidifier.is_on

    async def async_turn_on(self, **_: Any) -> None:
        """Turn on the humidifier."""
        if not await self.coordinator.config_entry.runtime_data.client.run_blocking_call(self.humidifier.turn_on):
            raise VesyncApiClientCommunicationError("Unable to turn on the humidifier")
        await self.coordinator.config_entry.runtime_data.client.run_blocking_call(self.humidifier.update)

    async def async_turn_off(self, **_: Any) -> None:
        """Turn off the humidifier."""
        if not await self.coordinator.config_entry.runtime_data.client.run_blocking_call(self.humidifier.turn_off):
            raise VesyncApiClientCommunicationError("Unable to turn off the humidifier")
        await self.coordinator.config_entry.runtime_data.client.run_blocking_call(self.humidifier.update)
