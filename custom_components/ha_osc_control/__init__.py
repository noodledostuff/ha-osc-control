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
SERVICE_ADD_ENDPOINT_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Optional(CONF_HOST): cv.string,
        vol.Optional(CONF_PORT): cv.port,
        vol.Required(CONF_OSC_ADDRESS): cv.string,
        vol.Optional(CONF_VALUE_TYPE, default=VALUE_TYPE_FLOAT): vol.In(
            [VALUE_TYPE_FLOAT, VALUE_TYPE_INT, VALUE_TYPE_BOOL]
        ),
    }
)

SERVICE_ADD_BUTTON_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required("endpoint_id"): cv.string,
        vol.Optional("value", default=1.0): vol.Any(float, int, bool),
    }
)

SERVICE_ADD_SLIDER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required("endpoint_id"): cv.string,
        vol.Optional("min", default=0.0): vol.Coerce(float),
        vol.Optional("max", default=1.0): vol.Coerce(float),
        vol.Optional("step", default=0.01): vol.Coerce(float),
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
            "endpoints": {},  # Dictionary of endpoint_id -> OSCEndpoint
            "buttons": [],
            "sliders": [],
        }
        
        # Forward entry setup to platforms
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        
        # Register services
        async def handle_add_endpoint(call: ServiceCall) -> None:
            """Handle add_endpoint service call."""
            from .osc_endpoint import OSCEndpoint
            
            name = call.data[CONF_NAME]
            endpoint_host = call.data.get(CONF_HOST, host)
            endpoint_port = call.data.get(CONF_PORT, port)
            osc_address = call.data[CONF_OSC_ADDRESS]
            value_type = call.data[CONF_VALUE_TYPE]
            
            # Create endpoint
            endpoint = OSCEndpoint(
                hass=hass,
                entry_id=entry.entry_id,
                name=name,
                host=endpoint_host,
                port=endpoint_port,
                osc_address=osc_address,
                value_type=value_type,
            )
            
            # Store endpoint
            hass.data[DOMAIN][entry.entry_id]["endpoints"][endpoint.unique_id] = endpoint
            _LOGGER.info(
                "Added OSC endpoint: %s -> %s:%s%s",
                name,
                endpoint_host,
                endpoint_port,
                osc_address,
            )
        
        async def handle_add_button(call: ServiceCall) -> None:
            """Handle add_button service call."""
            from .button import OSCButton
            
            name = call.data[CONF_NAME]
            endpoint_id = call.data["endpoint_id"]
            value = call.data["value"]
            
            # Get endpoint
            endpoint = hass.data[DOMAIN][entry.entry_id]["endpoints"].get(endpoint_id)
            if not endpoint:
                _LOGGER.error("Endpoint %s not found", endpoint_id)
                return
            
            # Create button entity
            button = OSCButton(
                hass=hass,
                entry_id=entry.entry_id,
                name=name,
                endpoint=endpoint,
                value=value,
            )
            
            # Add entity
            hass.data[DOMAIN][entry.entry_id]["buttons"].append(button)
            await hass.config_entries.async_forward_entry_setup(entry, Platform.BUTTON)
            _LOGGER.info("Added OSC button: %s", name)
        
        async def handle_add_slider(call: ServiceCall) -> None:
            """Handle add_slider service call."""
            from .number import OSCNumber
            
            name = call.data[CONF_NAME]
            endpoint_id = call.data["endpoint_id"]
            min_value = call.data["min"]
            max_value = call.data["max"]
            step = call.data["step"]
            
            # Get endpoint
            endpoint = hass.data[DOMAIN][entry.entry_id]["endpoints"].get(endpoint_id)
            if not endpoint:
                _LOGGER.error("Endpoint %s not found", endpoint_id)
                return
            
            # Create number entity
            slider = OSCNumber(
                hass=hass,
                entry_id=entry.entry_id,
                name=name,
                endpoint=endpoint,
                min_value=min_value,
                max_value=max_value,
                step=step,
            )
            
            # Add entity
            hass.data[DOMAIN][entry.entry_id]["sliders"].append(slider)
            await hass.config_entries.async_forward_entry_setup(entry, Platform.NUMBER)
            _LOGGER.info("Added OSC slider: %s", name)
        
        hass.services.async_register(
            DOMAIN, "add_endpoint", handle_add_endpoint, schema=SERVICE_ADD_ENDPOINT_SCHEMA
        )
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
