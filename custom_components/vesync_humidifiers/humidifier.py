"""Humidifier platform for vesync_humidifiers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.humidifier import HumidifierEntity, HumidifierEntityDescription

from .entity import VesyncEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import VesyncDataUpdateCoordinator
    from .data import VesyncConfigEntry

ENTITY_DESCRIPTIONS = (
    HumidifierEntityDescription(
        key="vesync_humidifier",
        name="VeSync Humidifier",
        icon="mdi:format-quote-close",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: VesyncConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    async_add_entities(
        VesyncHumidifier(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class VesyncHumidifier(VesyncEntity, HumidifierEntity):
    """vesync_humidifier class."""

    def __init__(
        self,
        coordinator: VesyncDataUpdateCoordinator,
        entity_description: HumidifierEntityDescription,
    ) -> None:
        """Initialize the humidifier class."""
        super().__init__(coordinator)
        self.entity_description = entity_description

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return self.coordinator.data.get("title", "") == "foo"

    async def async_turn_on(self, **_: Any) -> None:
        """Turn on the humidifier."""
        await self.coordinator.config_entry.runtime_data.client.async_set_title("bar")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **_: Any) -> None:
        """Turn off the humidifier."""
        await self.coordinator.config_entry.runtime_data.client.async_set_title("foo")
        await self.coordinator.async_request_refresh()
