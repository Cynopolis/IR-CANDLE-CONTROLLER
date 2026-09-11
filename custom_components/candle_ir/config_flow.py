"""Config flow for LED Candle IR integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.components.infrared import (
    DOMAIN as INFRARED_DOMAIN,
)
from homeassistant.components.infrared import (
    async_get_emitters,
    async_get_receivers,
)
from homeassistant.config_entries import ConfigFlow
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
)

from .const import CONF_INFRARED_ENTITY_ID, CONF_INFRARED_RECEIVER_ENTITY_ID, DOMAIN

_LOGGER = logging.getLogger(__name__)


DEVICE_TYPE_NAMES: dict[str, str] = {
    "candle": "Single Candle",
    "candle_string": "Candle String/Light Set",
}


@callback
def _infrared_entity_schema(
    hass: HomeAssistant, *, emitter_required: bool = False
) -> vol.Schema:
    """Return the emitter/receiver selection schema."""
    emitter_marker = vol.Required if emitter_required else vol.Optional
    return vol.Schema(
        {
            emitter_marker(CONF_INFRARED_ENTITY_ID): EntitySelector(
                EntitySelectorConfig(
                    domain=INFRARED_DOMAIN,
                    include_entities=async_get_emitters(hass),
                )
            ),
            vol.Optional(CONF_INFRARED_RECEIVER_ENTITY_ID): EntitySelector(
                EntitySelectorConfig(
                    domain=INFRARED_DOMAIN,
                    include_entities=async_get_receivers(hass),
                )
            ),
        }
    )


class CandleIrConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for LED Candle IR."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._device_type: str | None = None

    @callback
    def _entity_name(self, entity_id: str) -> str:
        """Get the name of an entity."""
        ent_reg = er.async_get(self.hass)
        entry = ent_reg.async_get(entity_id)
        return entry.name or entry.original_name or entity_id if entry else entity_id

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        emitter_entity_ids = async_get_emitters(self.hass)
        if not emitter_entity_ids and not async_get_receivers(self.hass):
            return self.async_abort(reason="no_infrared_entities")

        return self.async_show_menu(
            step_id="user",
            menu_options=["candle", "candle_string"],
        )

    async def async_step_candle(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle single candle setup."""
        return await self._async_setup_device("candle", user_input)

    async def async_step_candle_string(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle candle string setup."""
        return await self._async_setup_device("candle_string", user_input)

    async def _async_setup_device(
        self, device_type: str, user_input: dict[str, Any] | None
    ) -> FlowResult:
        """Handle device setup steps."""
        errors: dict[str, str] = {}

        if user_input is not None and (
            user_input.get(CONF_INFRARED_ENTITY_ID)
            or user_input.get(CONF_INFRARED_RECEIVER_ENTITY_ID)
        ):
            emitter_id = user_input.get(CONF_INFRARED_ENTITY_ID)
            receiver_id = user_input.get(CONF_INFRARED_RECEIVER_ENTITY_ID)
            title_entity_id = emitter_id or receiver_id

            if title_entity_id:
                self._async_abort_entries_match(
                    {
                        CONF_INFRARED_ENTITY_ID: emitter_id,
                    }
                )
                return self.async_create_entry(
                    title=f"Candle via {self._entity_name(title_entity_id)}",
                    data={
                        "device_type": device_type,
                        CONF_INFRARED_ENTITY_ID: emitter_id,
                        CONF_INFRARED_RECEIVER_ENTITY_ID: receiver_id,
                    },
                )
            errors["base"] = "missing_infrared_entity"

        return self.async_show_form(
            step_id=device_type,
            data_schema=_infrared_entity_schema(self.hass, emitter_required=False),
            errors=errors,
        )
