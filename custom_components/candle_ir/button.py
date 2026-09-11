"""Button platform for LED Candle IR integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.components.infrared import InfraredEmitterConsumerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CandleCommand
from .entity import CandleEntity

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class CandleButtonEntityDescription(ButtonEntityDescription):
    """Describes a Candle IR button entity."""

    command_code: int


CANDLE_BUTTON_DESCRIPTIONS: tuple[CandleButtonEntityDescription, ...] = (
    CandleButtonEntityDescription(
        key="power", translation_key="power", command_code=CandleCommand.POWER
    ),
    CandleButtonEntityDescription(
        key="power_on", translation_key="power_on", command_code=CandleCommand.POWER_ON
    ),
    CandleButtonEntityDescription(
        key="power_off", translation_key="power_off", command_code=CandleCommand.POWER_OFF
    ),
    CandleButtonEntityDescription(
        key="flicker", translation_key="flicker", command_code=CandleCommand.FLICKER
    ),
    CandleButtonEntityDescription(
        key="flat", translation_key="flat", command_code=CandleCommand.FLAT
    ),
)

# Timer buttons - disabled by default, user can enable as needed
TIMER_BUTTON_DESCRIPTIONS: tuple[CandleButtonEntityDescription, ...] = (
    CandleButtonEntityDescription(
        key="timer_1h",
        translation_key="timer_1h",
        command_code=CandleCommand.TIMER_1H,
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.CONFIG,
    ),
    CandleButtonEntityDescription(
        key="timer_2h",
        translation_key="timer_2h",
        command_code=CandleCommand.TIMER_2H,
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.CONFIG,
    ),
    CandleButtonEntityDescription(
        key="timer_4h",
        translation_key="timer_4h",
        command_code=CandleCommand.TIMER_4H,
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.CONFIG,
    ),
    CandleButtonEntityDescription(
        key="timer_8h",
        translation_key="timer_8h",
        command_code=CandleCommand.TIMER_8H,
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.CONFIG,
    ),
)

# Brightness buttons
BRIGHTNESS_BUTTON_DESCRIPTIONS: tuple[CandleButtonEntityDescription, ...] = (
    CandleButtonEntityDescription(
        key="brightness_up",
        translation_key="brightness_up",
        command_code=CandleCommand.BRIGHTNESS_UP,
    ),
    CandleButtonEntityDescription(
        key="brightness_down",
        translation_key="brightness_down",
        command_code=CandleCommand.BRIGHTNESS_DOWN,
    ),
)

# Color temperature buttons
COLOR_TEMP_BUTTON_DESCRIPTIONS: tuple[CandleButtonEntityDescription, ...] = (
    CandleButtonEntityDescription(
        key="color_temp_warm",
        translation_key="color_temp_warm",
        command_code=CandleCommand.COLOR_TEMP_WARM,
    ),
    CandleButtonEntityDescription(
        key="color_temp_cool",
        translation_key="color_temp_cool",
        command_code=CandleCommand.COLOR_TEMP_COOL,
    ),
)

ALL_BUTTON_DESCRIPTIONS: tuple[CandleButtonEntityDescription, ...] = (
    CANDLE_BUTTON_DESCRIPTIONS
    + TIMER_BUTTON_DESCRIPTIONS
    + BRIGHTNESS_BUTTON_DESCRIPTIONS
    + COLOR_TEMP_BUTTON_DESCRIPTIONS
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Candle IR buttons from config entry."""
    infrared_entity_id = entry.data.get("infrared_entity_id")
    if not infrared_entity_id:
        return

    device_name = entry.options.get("device_name", "LED Candle")
    async_add_entities(
        CandleButton(entry, infrared_entity_id, description, device_name)
        for description in ALL_BUTTON_DESCRIPTIONS
    )


class CandleButton(CandleEntity, InfraredEmitterConsumerEntity, ButtonEntity):
    """Candle IR button entity."""

    entity_description: CandleButtonEntityDescription

    def __init__(
        self,
        entry: ConfigEntry,
        infrared_entity_id: str,
        description: CandleButtonEntityDescription,
        device_name: str,
    ) -> None:
        """Initialize Candle IR button."""
        super().__init__(
            entry, unique_id_suffix=description.key, device_name=device_name
        )
        self._infrared_emitter_entity_id = infrared_entity_id
        self.entity_description = description

    async def async_press(self) -> None:
        """Press the button."""
        await self._send_command(
            CandleCommand.to_nec_command(self.entity_description.command_code)
        )
