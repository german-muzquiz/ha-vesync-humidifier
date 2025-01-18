"""Humidifier platform for vesync_humidifiers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.humidifier import HumidifierEntity, HumidifierEntityDescription
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .api import VesyncApiClientCommunicationError
from .const import DOMAIN
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
            cid=cid,
        )
        for cid in entry.runtime_data.coordinator.data
    )


class VesyncHumidifier(VesyncEntity, HumidifierEntity):
    """vesync_humidifier class."""

    def __init__(
        self,
        coordinator: VesyncDataUpdateCoordinator,
        cid: str,  # Identifier of the humidifier
    ) -> None:
        """Initialize the humidifier class."""
        super().__init__(coordinator)
        self._attr_unique_id = cid
        self.cid = cid
        coordinator.async_add_listener(self._on_refresh)
        self._on_refresh()

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()

        # Add state change listener
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{DOMAIN}_device_update_{self.cid}",
                self._handle_device_update,
            )
        )

    @callback
    def _handle_device_update(self):
        """Handle device state changes."""
        self.async_write_ha_state()

    def _on_refresh(self):
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    self.coordinator.config_entry.domain,
                    self.cid,
                ),
            },
            name=self.coordinator.data[self.cid].device_name,
            model=self.coordinator.data[self.cid].device_type,
        )
        self.entity_description = HumidifierEntityDescription(
            key=f"vesync_humidifier_{self.cid}",
            name=self.coordinator.data[self.cid].device_name,
            icon="mdi:format-quote-close",
        )
        self._attr_current_humidity = self.coordinator.data[self.cid].humidity

    @property
    def is_on(self) -> bool:
        """Return true if the humidifier is on."""
        return self.coordinator.data[self.cid].device_status == "on"

    @property
    def target_humidity(self) -> float:
        """Return the target humidity."""
        return self.coordinator.data[self.cid].auto_humidity

    @property
    def current_humidity(self) -> float:
        """Return the current humidity."""
        return self.coordinator.data[self.cid].humidity

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.data[self.cid].connection_status == "online"

    @property
    def mode(self) -> str | None:
        """Return the current mode, e.g., home, auto, baby, etc."""
        return self.coordinator.data[self.cid].details["mode"]

    async def async_turn_on(self, **_: Any) -> None:
        """Turn on the humidifier."""
        try:
            if not await self.coordinator.config_entry.runtime_data.client.run_blocking_call(
                self.coordinator.data[self.cid].turn_on
            ):
                raise VesyncApiClientCommunicationError("Unable to turn on the humidifier")
        finally:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **_: Any) -> None:
        """Turn off the humidifier."""
        try:
            if not await self.coordinator.config_entry.runtime_data.client.run_blocking_call(
                self.coordinator.data[self.cid].turn_off
            ):
                raise VesyncApiClientCommunicationError("Unable to turn off the humidifier")
        finally:
            await self.coordinator.async_request_refresh()

    async def async_set_humidity(self, humidity: int) -> None:
        """Set the target humidity."""
        try:
            if not await self.coordinator.config_entry.runtime_data.client.run_blocking_call(
                self.coordinator.data[self.cid].set_humidity, humidity
            ):
                raise VesyncApiClientCommunicationError("Unable to set the target humidity")
        finally:
            await self.coordinator.async_request_refresh()
