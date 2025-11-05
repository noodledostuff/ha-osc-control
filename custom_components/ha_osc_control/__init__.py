"""The OSC Control integration."""
from __future__ import annotations

import logging
from typing import Any

from pythonosc import udp_client

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import (
    DOMAIN,
    CONF_OSC_ADDRESS,
    CONF_VALUE_TYPE,
    VALUE_TYPE_FLOAT,
    VALUE_TYPE_INT,
    VALUE_TYPE_BOOL,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.BUTTON, Platform.NUMBER]

# Service schemas
SERVICE_ADD_BUTTON_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_OSC_ADDRESS): cv.string,
        vol.Optional("value", default=1.0): vol.Any(float, int, bool),
        vol.Optional(CONF_VALUE_TYPE, default=VALUE_TYPE_FLOAT): vol.In(
            [VALUE_TYPE_FLOAT, VALUE_TYPE_INT, VALUE_TYPE_BOOL]
        ),
    }
)

SERVICE_ADD_SLIDER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_OSC_ADDRESS): cv.string,
        vol.Optional("min", default=0.0): vol.Coerce(float),
        vol.Optional("max", default=1.0): vol.Coerce(float),
        vol.Optional("step", default=0.01): vol.Coerce(float),
        vol.Optional(CONF_VALUE_TYPE, default=VALUE_TYPE_FLOAT): vol.In(
            [VALUE_TYPE_FLOAT, VALUE_TYPE_INT]
        ),
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OSC Control from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]

    try:
        # Create OSC client
        client = udp_client.SimpleUDPClient(host, port)
        
        # Store client in hass.data
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id] = {
            "client": client,
            "host": host,
            "port": port,
            "buttons": [],
            "sliders": [],
        }
        
        # Forward entry setup to platforms
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        
        # Register services
        async def handle_add_button(call: ServiceCall) -> None:
            """Handle add_button service call."""
            from .button import OSCButton
            
            name = call.data[CONF_NAME]
            osc_address = call.data[CONF_OSC_ADDRESS]
            value = call.data["value"]
            value_type = call.data[CONF_VALUE_TYPE]
            
            # Create button entity
            button = OSCButton(
                hass=hass,
                entry_id=entry.entry_id,
                name=name,
                osc_address=osc_address,
                value=value,
                value_type=value_type,
            )
            
            # Add entity
            hass.data[DOMAIN][entry.entry_id]["buttons"].append(button)
            await hass.config_entries.async_forward_entry_setup(entry, Platform.BUTTON)
            _LOGGER.info("Added OSC button: %s -> %s", name, osc_address)
        
        async def handle_add_slider(call: ServiceCall) -> None:
            """Handle add_slider service call."""
            from .number import OSCNumber
            
            name = call.data[CONF_NAME]
            osc_address = call.data[CONF_OSC_ADDRESS]
            min_value = call.data["min"]
            max_value = call.data["max"]
            step = call.data["step"]
            value_type = call.data[CONF_VALUE_TYPE]
            
            # Create number entity
            slider = OSCNumber(
                hass=hass,
                entry_id=entry.entry_id,
                name=name,
                osc_address=osc_address,
                min_value=min_value,
                max_value=max_value,
                step=step,
                value_type=value_type,
            )
            
            # Add entity
            hass.data[DOMAIN][entry.entry_id]["sliders"].append(slider)
            await hass.config_entries.async_forward_entry_setup(entry, Platform.NUMBER)
            _LOGGER.info("Added OSC slider: %s -> %s", name, osc_address)
        
        hass.services.async_register(
            DOMAIN, "add_button", handle_add_button, schema=SERVICE_ADD_BUTTON_SCHEMA
        )
        hass.services.async_register(
            DOMAIN, "add_slider", handle_add_slider, schema=SERVICE_ADD_SLIDER_SCHEMA
        )
        
        return True
    except Exception as err:
        _LOGGER.error("Failed to connect to OSC server at %s:%s: %s", host, port, err)
        raise ConfigEntryNotReady from err


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
