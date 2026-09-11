"""Select platform for LED Candle IR integration.

Provides select entities for brightness levels and effect modes.
Adapted from:
https://github.com/home-assistant/core/tree/dev/homeassistant/components/lg_infrared/select.py
"""

from typing import override

from homeassistant.components.infrared import InfraredEmitterConsumerEntity
from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import CandleCommand
from .entity import CandleEntity

PARALLEL_UPDATES = 1


# Effect modes - maps UI options to IR command codes
EFFECT_MODES = {
    "flicker": CandleCommand.FLICKER,
    "flat": CandleCommand.FLAT,
}

# Brightness levels (some remotes use numeric keys)
BRIGHTNESS_LEVELS = ["low", "medium", "high"]
BRIGHTNESS_COMMANDS = {
    "low": CandleCommand.NUM_1,
    "medium": CandleCommand.NUM_2,
    "high": CandleCommand.NUM_3,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Candle IR select entities from config entry."""
    infrared_entity_id = entry.data.get("infrared_entity_id")
    if not infrared_entity_id:
        return

    device_name = entry.options.get("device_name", "LED Candle")
    async_add_entities([
        CandleEffectSelect(entry, infrared_entity_id, device_name),
        CandleBrightnessSelect(entry, infrared_entity_id, device_name),
    ])


class CandleEffectSelect(CandleEntity, InfraredEmitterConsumerEntity, SelectEntity, RestoreEntity):
    """Select entity for candle effect modes."""

    _attr_assumed_state = True
    _attr_entity_category = EntityCategory.CONFIG
    _attr_translation_key = "effect_mode"
    _attr_options = list(EFFECT_MODES.keys())

    def __init__(self, entry: ConfigEntry, emitter_entity_id: str, device_name: str) -> None:
        """Initialize the effect select."""
        super().__init__(entry, unique_id_suffix="effect_mode", device_name=device_name)
        self._infrared_emitter_entity_id = emitter_entity_id
        self._attr_current_option = "flicker"

    @override
    async def async_added_to_hass(self) -> None:
        """Restore the assumed state."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if (
            last_state is not None
            and last_state.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN)
            and last_state.state in EFFECT_MODES
        ):
            self._attr_current_option = last_state.state

    @override
    async def async_select_option(self, option: str) -> None:
        """Send the IR code for the chosen effect."""
        await self._send_command(CandleCommand.to_nec_command(EFFECT_MODES[option]))
        self._attr_current_option = option
        self.async_write_ha_state()


class CandleBrightnessSelect(CandleEntity, InfraredEmitterConsumerEntity, SelectEntity, RestoreEntity):
    """Select entity for candle brightness levels."""

    _attr_assumed_state = True
    _attr_entity_category = EntityCategory.CONFIG
    _attr_translation_key = "brightness"
    _attr_options = BRIGHTNESS_LEVELS

    def __init__(self, entry: ConfigEntry, emitter_entity_id: str, device_name: str) -> None:
        """Initialize the brightness select."""
        super().__init__(entry, unique_id_suffix="brightness", device_name=device_name)
        self._infrared_emitter_entity_id = emitter_entity_id
        self._attr_current_option = "medium"

    @override
    async def async_added_to_hass(self) -> None:
        """Restore the assumed state."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if (
            last_state is not None
            and last_state.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN)
            and last_state.state in BRIGHTNESS_COMMANDS
        ):
            self._attr_current_option = last_state.state

    @override
    async def async_select_option(self, option: str) -> None:
        """Send the IR code for the chosen brightness."""
        await self._send_command(CandleCommand.to_nec_command(BRIGHTNESS_COMMANDS[option]))
        self._attr_current_option = option
        self.async_write_ha_state()
