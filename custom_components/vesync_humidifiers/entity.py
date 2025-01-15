"""VesyncEntity class."""

from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION
from .coordinator import VesyncDataUpdateCoordinator


class VesyncEntity(CoordinatorEntity[VesyncDataUpdateCoordinator]):
    """VesyncEntity class."""

    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: VesyncDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
