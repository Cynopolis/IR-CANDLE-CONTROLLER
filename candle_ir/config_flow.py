"""Config flow for LED Candle IR integration.

Adapted from:
https://github.com/home-assistant/core/tree/dev/homeassistant/components/lg_infrared/config_flow.py
"""

from typing import TYPE_CHECKING, Any, override

import voluptuous as vol

from homeassistant.components.infrared import (
    DOMAIN as INFRARED_DOMAIN,
    async_get_emitters,
    async_get_receivers,
)
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
)

from .const import CONF_INFRARED_ENTITY_ID, CONF_INFRARED_RECEIVER_ENTITY_ID, DOMAIN

DEVICE_TYPE_NAMES = {
    "candle": "Single Candle",
    "candle_string": "Candle String/Light Set",
}


@callback
def _infrared_entity_schema(
    hass: HomeAssistant, *, emitter_required: bool
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
    """Handle config flow for LED Candle IR."""

    VERSION = 2

    def _entity_name(self, entity_id: str) -> str:
        ent_reg = er.async_get(self.hass)
        entry = ent_reg.async_get(entity_id)
        return entry.name or entry.original_name or entity_id if entry else entity_id

    @override
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle device type selection."""
        emitter_entity_ids = async_get_emitters(self.hass)
        if not emitter_entity_ids and not async_get_receivers(self.hass):
            return self.async_abort(reason="no_infrared_entities")

        menu_options = ["candle"]
        # Offer candle_string as an option
        menu_options.append("candle_string")

        return self.async_show_menu(step_id="user", menu_options=menu_options)

    async def async_step_candle(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle single candle setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            if user_input.get(CONF_INFRARED_ENTITY_ID) or user_input.get(
                CONF_INFRARED_RECEIVER_ENTITY_ID
            ):
                return await self._async_create_device_entry("candle", user_input)
            errors["base"] = "missing_infrared_entity"

        return self.async_show_form(
            step_id="candle",
            data_schema=_infrared_entity_schema(self.hass, emitter_required=False),
            errors=errors,
        )

    async def async_step_candle_string(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle candle string setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            if user_input.get(CONF_INFRARED_ENTITY_ID) or user_input.get(
                CONF_INFRARED_RECEIVER_ENTITY_ID
            ):
                return await self._async_create_device_entry("candle_string", user_input)
            errors["base"] = "missing_infrared_entity"

        return self.async_show_form(
            step_id="candle_string",
            data_schema=_infrared_entity_schema(self.hass, emitter_required=False),
            errors=errors,
        )

    async def _async_create_device_entry(
        self, device_type: str, user_input: dict[str, Any]
    ) -> ConfigFlowResult:
        """Create the entry for the candle device."""
        emitter_id = user_input.get(CONF_INFRARED_ENTITY_ID)
        receiver_id = user_input.get(CONF_INFRARED_RECEIVER_ENTITY_ID)

        title_entity_id = emitter_id or receiver_id
        if TYPE_CHECKING:
            assert title_entity_id is not None

        return self.async_create_entry(
            title=f"Candle via {self._entity_name(title_entity_id)}",
            data={
                "device_type": device_type,
                CONF_INFRARED_ENTITY_ID: emitter_id,
                CONF_INFRARED_RECEIVER_ENTITY_ID: receiver_id,
            },
        )
