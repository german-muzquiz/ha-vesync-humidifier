"""Custom types for vesync_humidifiers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import VesyncApiClient
    from .coordinator import VesyncDataUpdateCoordinator


type VesyncConfigEntry = ConfigEntry[VesyncData]


@dataclass
class VesyncData:
    """Data for the VeSync Humidifiers integration."""

    client: VesyncApiClient
    coordinator: VesyncDataUpdateCoordinator
    integration: Integration
