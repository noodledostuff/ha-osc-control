"""The OSC Control integration."""
from __future__ import annotations

import logging
from typing import Any

from pythonosc import udp_client

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.BUTTON, Platform.NUMBER]


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
        }
        
        # Forward entry setup to platforms
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        
        return True
    except Exception as err:
        _LOGGER.error("Failed to connect to OSC server at %s:%s: %s", host, port, err)
        raise ConfigEntryNotReady from err


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
