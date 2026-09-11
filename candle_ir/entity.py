"""Common entity for LED Candle IR integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN


class CandleEntity(Entity):
    """LED Candle base entity providing common device info."""

    _attr_has_entity_name = True

    def __init__(
        self,
        entry: ConfigEntry,
        unique_id_suffix: str,
        device_name: str = "LED Candle",
        model: str = "LED Flame Candle",
    ) -> None:
        """Initialize LED Candle entity."""
        self._attr_unique_id = f"{entry.entry_id}_{unique_id_suffix}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=device_name,
            manufacturer="Generic",
            model=model,
            sw_version="IR Controlled",
        )
