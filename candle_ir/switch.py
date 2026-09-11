"""Switch platform for LED Candle IR integration.

Provides switch entities for features that have distinct on/off states.
Adapted from:
https://github.com/home-assistant/core/tree/dev/homeassistant/components/lg_infrared/switch.py
"""

from dataclasses import dataclass
from typing import Any, override

from homeassistant.components.infrared import InfraredEmitterConsumerEntity
from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    STATE_ON,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    EntityCategory,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import CandleCommand
from .entity import CandleEntity

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class CandleSwitchEntityDescription(SwitchEntityDescription):
    """Describes a Candle IR switch entity."""

    on_code: int
    off_code: int | None = None  # Some candles don't have separate off codes


# Switch definitions - adjust based on your candle remote
CANDLE_SWITCH_DESCRIPTIONS: tuple[CandleSwitchEntityDescription, ...] = (
    CandleSwitchEntityDescription(
        key="color_temperature",
        translation_key="color_temperature",
        on_code=CandleCommand.COLOR_TEMP_COOL,
        off_code=CandleCommand.COLOR_TEMP_WARM,
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Candle IR switches from config entry."""
    emitter_entity_id = entry.data.get("infrared_entity_id")
    if not emitter_entity_id:
        return

    device_name = entry.options.get("device_name", "LED Candle")
    async_add_entities(
        CandleSwitch(entry, emitter_entity_id, description, device_name)
        for description in CANDLE_SWITCH_DESCRIPTIONS
    )


class CandleSwitch(CandleEntity, InfraredEmitterConsumerEntity, SwitchEntity, RestoreEntity):
    """A Candle IR feature toggled by infrared codes."""

    _attr_assumed_state = True
    entity_description: CandleSwitchEntityDescription

    def __init__(
        self,
        entry: ConfigEntry,
        emitter_entity_id: str,
        description: CandleSwitchEntityDescription,
        device_name: str,
    ) -> None:
        """Initialize the switch."""
        super().__init__(entry, unique_id_suffix=description.key, device_name=device_name)
        self._infrared_emitter_entity_id = emitter_entity_id
        self.entity_description = description
        self._attr_is_on = False

    @override
    async def async_added_to_hass(self) -> None:
        """Restore the assumed state."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state is not None and last_state.state not in (
            STATE_UNAVAILABLE,
            STATE_UNKNOWN,
        ):
            self._attr_is_on = last_state.state == STATE_ON

    @override
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the feature on."""
        await self._send_command(CandleCommand.to_nec_command(self.entity_description.on_code))
        self._attr_is_on = True
        self.async_write_ha_state()

    @override
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the feature off."""
        if self.entity_description.off_code is not None:
            await self._send_command(CandleCommand.to_nec_command(self.entity_description.off_code))
        self._attr_is_on = False
        self.async_write_ha_state()
