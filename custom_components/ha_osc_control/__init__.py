"""The OSC Control integration."""
from __future__ import annotations

import logging
from typing import Any

from pythonosc import udp_client

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
from homeassistant.helpers import config_validation as cv, device_registry as dr
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
SERVICE_ADD_ENDPOINT = "add_endpoint"
SERVICE_ADD_BUTTON = "add_button"
SERVICE_ADD_SLIDER = "add_slider"
SERVICE_LIST_ENDPOINTS = "list_endpoints"
SERVICE_NAMES = (
    SERVICE_ADD_ENDPOINT,
    SERVICE_ADD_BUTTON,
    SERVICE_ADD_SLIDER,
    SERVICE_LIST_ENDPOINTS,
)

# Service schemas
SERVICE_ADD_ENDPOINT_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Optional("entry_id"): cv.string,
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
        vol.Optional("entry_id"): cv.string,
        vol.Optional("value", default=1.0): vol.Any(float, int, bool),
    }
)

SERVICE_ADD_SLIDER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required("endpoint_id"): cv.string,
        vol.Optional("entry_id"): cv.string,
        vol.Optional("min", default=0.0): vol.Coerce(float),
        vol.Optional("max", default=1.0): vol.Coerce(float),
        vol.Optional("step", default=0.01): vol.Coerce(float),
    }
)

SERVICE_LIST_ENDPOINTS_SCHEMA = vol.Schema({vol.Optional("entry_id"): cv.string})


def _entry_data(hass: HomeAssistant) -> dict[str, dict[str, Any]]:
    """Return loaded config-entry data."""
    return {
        entry_id: data
        for entry_id, data in hass.data.get(DOMAIN, {}).items()
        if isinstance(data, dict) and "endpoints" in data
    }


def _get_entry_data(
    hass: HomeAssistant, entry_id: str | None = None
) -> tuple[str, dict[str, Any]]:
    """Find the target integration entry for an action."""
    entries = _entry_data(hass)

    if entry_id is not None:
        if entry_id in entries:
            return entry_id, entries[entry_id]
        raise HomeAssistantError(f"OSC Control entry {entry_id} not found")

    if len(entries) == 1:
        return next(iter(entries.items()))

    if not entries:
        raise HomeAssistantError("No OSC Control entries are loaded")

    raise HomeAssistantError("entry_id is required when multiple OSC Control entries exist")


def _get_endpoint_data(
    hass: HomeAssistant, endpoint_id: str, entry_id: str | None = None
) -> dict[str, Any]:
    """Find the loaded entry data containing an endpoint."""
    if entry_id is not None:
        _, data = _get_entry_data(hass, entry_id)
        if endpoint_id in data["endpoints"]:
            return data
        raise HomeAssistantError(f"OSC endpoint {endpoint_id} not found")

    for data in _entry_data(hass).values():
        if endpoint_id in data["endpoints"]:
            return data

    raise HomeAssistantError(f"OSC endpoint {endpoint_id} not found")


def _register_services(hass: HomeAssistant) -> None:
    """Register integration actions."""

    async def handle_add_endpoint(call: ServiceCall) -> None:
        """Handle add_endpoint action call."""
        from .osc_endpoint import OSCEndpoint

        entry_id, data = _get_entry_data(hass, call.data.get("entry_id"))
        endpoint_host = call.data.get(CONF_HOST, data["host"])
        endpoint_port = call.data.get(CONF_PORT, data["port"])
        endpoint = OSCEndpoint(
            hass=hass,
            entry_id=entry_id,
            name=call.data[CONF_NAME],
            host=endpoint_host,
            port=endpoint_port,
            osc_address=call.data[CONF_OSC_ADDRESS],
            value_type=call.data[CONF_VALUE_TYPE],
        )

        data["endpoints"][endpoint.unique_id] = endpoint
        _LOGGER.info(
            "Added OSC endpoint: %s -> %s:%s%s (ID: %s)",
            endpoint.name,
            endpoint_host,
            endpoint_port,
            endpoint.osc_address,
            endpoint.unique_id,
        )

    async def handle_add_button(call: ServiceCall) -> None:
        """Handle add_button action call."""
        from .button import OSCButton

        data = _get_endpoint_data(
            hass, call.data["endpoint_id"], call.data.get("entry_id")
        )
        endpoint = data["endpoints"][call.data["endpoint_id"]]
        button = OSCButton(
            hass=hass,
            entry_id=endpoint.entry_id,
            name=call.data[CONF_NAME],
            endpoint=endpoint,
            value=call.data["value"],
        )

        if add_entities := data.get("add_buttons"):
            add_entities([button], True)
        else:
            data["pending_buttons"].append(button)
        _LOGGER.info("Added OSC button: %s", call.data[CONF_NAME])

    async def handle_add_slider(call: ServiceCall) -> None:
        """Handle add_slider action call."""
        from .number import OSCNumber

        data = _get_endpoint_data(
            hass, call.data["endpoint_id"], call.data.get("entry_id")
        )
        endpoint = data["endpoints"][call.data["endpoint_id"]]
        slider = OSCNumber(
            hass=hass,
            entry_id=endpoint.entry_id,
            name=call.data[CONF_NAME],
            endpoint=endpoint,
            min_value=call.data["min"],
            max_value=call.data["max"],
            step=call.data["step"],
        )

        if add_entities := data.get("add_sliders"):
            add_entities([slider], True)
        else:
            data["pending_sliders"].append(slider)
        _LOGGER.info("Added OSC slider: %s", call.data[CONF_NAME])

    async def handle_list_endpoints(call: ServiceCall) -> None:
        """Handle list_endpoints action call."""
        entry_id = call.data.get("entry_id")
        if entry_id is None:
            entries = _entry_data(hass)
        else:
            current_entry_id, data = _get_entry_data(hass, entry_id)
            entries = {current_entry_id: data}
        found = False

        for current_entry_id, data in entries.items():
            if not data["endpoints"]:
                continue

            found = True
            _LOGGER.info("Configured OSC Endpoints for entry %s:", current_entry_id)
            for endpoint_id, endpoint in data["endpoints"].items():
                _LOGGER.info(
                    "  - ID: %s | Name: %s | Address: %s:%s%s | Type: %s",
                    endpoint_id,
                    endpoint.name,
                    endpoint.host,
                    endpoint.port,
                    endpoint.osc_address,
                    endpoint.value_type,
                )

        if not found:
            _LOGGER.info("No OSC endpoints configured")

    hass.services.async_register(
        DOMAIN,
        SERVICE_ADD_ENDPOINT,
        handle_add_endpoint,
        schema=SERVICE_ADD_ENDPOINT_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_ADD_BUTTON, handle_add_button, schema=SERVICE_ADD_BUTTON_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_ADD_SLIDER, handle_add_slider, schema=SERVICE_ADD_SLIDER_SCHEMA
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_LIST_ENDPOINTS,
        handle_list_endpoints,
        schema=SERVICE_LIST_ENDPOINTS_SCHEMA,
    )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OSC Control from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]

    try:
        client = udp_client.SimpleUDPClient(host, port)
    except Exception as err:
        _LOGGER.error("Failed to connect to OSC server at %s:%s: %s", host, port, err)
        raise ConfigEntryNotReady from err

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        manufacturer="OSC Control",
        name=entry.data.get(CONF_NAME, "OSC Device"),
        model="OSC Client",
        configuration_url=f"homeassistant://config/integrations/integration/{DOMAIN}",
    )

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        "host": host,
        "port": port,
        "endpoints": {},
        "pending_buttons": [],
        "pending_sliders": [],
    }

    if not hass.data[DOMAIN].get("services_registered"):
        _register_services(hass)
        hass.data[DOMAIN]["services_registered"] = True

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
        if not _entry_data(hass):
            for service in SERVICE_NAMES:
                hass.services.async_remove(DOMAIN, service)
            hass.data.pop(DOMAIN)
    return unload_ok
