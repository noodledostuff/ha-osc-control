"""Support for OSC Control buttons."""
from __future__ import annotations

from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import slugify

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OSC Control button based on a config entry."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    data["add_buttons"] = async_add_entities

    if buttons := data["pending_buttons"]:
        async_add_entities(buttons, True)
        data["pending_buttons"] = []


class OSCButton(ButtonEntity):
    """Representation of an OSC button."""

    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        name: str,
        endpoint: Any,  # OSCEndpoint
        value: Any = 1.0,
        unique_id: str | None = None,
    ) -> None:
        """Initialize the OSC button."""
        self.hass = hass
        self._entry_id = entry_id
        self._attr_name = name
        self._endpoint = endpoint
        self._value = value
        self._attr_unique_id = (
            unique_id or f"{entry_id}_button_{endpoint.unique_id}_{slugify(name)}"
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._endpoint.send_value(self._value)
