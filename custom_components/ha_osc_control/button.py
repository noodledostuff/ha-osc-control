"""Support for OSC Control buttons."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers import entity_registry as er

from .const import CONF_OSC_ADDRESS, CONF_VALUE_TYPE, DOMAIN, VALUE_TYPE_BOOL, VALUE_TYPE_FLOAT, VALUE_TYPE_INT

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OSC Control button based on a config entry."""
    buttons = hass.data[DOMAIN][config_entry.entry_id].get("buttons", [])
    if buttons:
        async_add_entities(buttons, True)
        # Clear the list after adding
        hass.data[DOMAIN][config_entry.entry_id]["buttons"] = []


class OSCButton(ButtonEntity):
    """Representation of an OSC button."""

    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        name: str,
        osc_address: str,
        value: Any = 1.0,
        value_type: str = VALUE_TYPE_FLOAT,
        unique_id: str | None = None,
    ) -> None:
        """Initialize the OSC button."""
        self.hass = hass
        self._entry_id = entry_id
        self._attr_name = name
        self._osc_address = osc_address
        self._value = value
        self._value_type = value_type
        self._attr_unique_id = unique_id or f"{entry_id}_{osc_address}"

    async def async_press(self) -> None:
        """Handle the button press."""
        client = self.hass.data[DOMAIN][self._entry_id]["client"]
        
        # Convert value based on type
        if self._value_type == VALUE_TYPE_INT:
            send_value = int(self._value)
        elif self._value_type == VALUE_TYPE_BOOL:
            send_value = bool(self._value)
        else:  # VALUE_TYPE_FLOAT
            send_value = float(self._value)
        
        try:
            await self.hass.async_add_executor_job(
                client.send_message, self._osc_address, send_value
            )
            _LOGGER.debug(
                "Sent OSC message to %s with value %s", self._osc_address, send_value
            )
        except Exception as err:
            _LOGGER.error("Failed to send OSC message: %s", err)
