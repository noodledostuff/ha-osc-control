"""Support for OSC Control number entities (sliders/faders)."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_OSC_ADDRESS, CONF_VALUE_TYPE, DOMAIN, VALUE_TYPE_FLOAT, VALUE_TYPE_INT

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OSC Control number based on a config entry."""
    sliders = hass.data[DOMAIN][config_entry.entry_id].get("sliders", [])
    if sliders:
        async_add_entities(sliders, True)
        # Clear the list after adding
        hass.data[DOMAIN][config_entry.entry_id]["sliders"] = []


class OSCNumber(NumberEntity):
    """Representation of an OSC number entity (slider/fader)."""

    _attr_has_entity_name = True
    _attr_mode = NumberMode.SLIDER

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        name: str,
        endpoint: Any,  # OSCEndpoint
        min_value: float = 0.0,
        max_value: float = 1.0,
        step: float = 0.01,
        unique_id: str | None = None,
    ) -> None:
        """Initialize the OSC number entity."""
        self.hass = hass
        self._entry_id = entry_id
        self._attr_name = name
        self._endpoint = endpoint
        self._attr_unique_id = unique_id or f"{entry_id}_slider_{endpoint.unique_id}"
        
        # Set number entity attributes
        self._attr_native_min_value = min_value
        self._attr_native_max_value = max_value
        self._attr_native_step = step
        self._attr_native_value = min_value

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value and send OSC message."""
        await self._endpoint.send_value(value)
        self._attr_native_value = value
        self.async_write_ha_state()
