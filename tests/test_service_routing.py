"""Plain-Python checks for OSC Control action routing."""
from __future__ import annotations

import sys
import types
from pathlib import Path


def _module(name: str) -> types.ModuleType:
    module = types.ModuleType(name)
    sys.modules[name] = module
    return module


def _install_stubs() -> None:
    """Stub Home Assistant imports used by the integration module."""
    vol = _module("voluptuous")
    vol.Schema = lambda value: value
    vol.Required = lambda key, **kwargs: key
    vol.Optional = lambda key, **kwargs: key
    vol.In = lambda value: value
    vol.Any = lambda *value: value
    vol.Coerce = lambda value: value

    pythonosc = _module("pythonosc")
    udp_client = _module("pythonosc.udp_client")
    udp_client.SimpleUDPClient = object
    pythonosc.udp_client = udp_client

    _module("homeassistant")
    config_entries = _module("homeassistant.config_entries")
    config_entries.ConfigEntry = object

    const = _module("homeassistant.const")
    const.CONF_HOST = "host"
    const.CONF_NAME = "name"
    const.CONF_PORT = "port"

    class Platform:
        BUTTON = "button"
        NUMBER = "number"

    const.Platform = Platform

    core = _module("homeassistant.core")
    core.HomeAssistant = object
    core.ServiceCall = object

    exceptions = _module("homeassistant.exceptions")
    exceptions.ConfigEntryNotReady = RuntimeError
    exceptions.HomeAssistantError = RuntimeError

    helpers = _module("homeassistant.helpers")
    cv = _module("homeassistant.helpers.config_validation")
    cv.string = str
    cv.port = int
    device_registry = _module("homeassistant.helpers.device_registry")
    helpers.config_validation = cv
    helpers.device_registry = device_registry


def _load_integration():
    _install_stubs()
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    import custom_components.ha_osc_control as integration

    return integration


class Hass:
    def __init__(self, data):
        self.data = data


def test_single_entry_is_default() -> None:
    integration = _load_integration()
    data = {"endpoints": {"entry1__mix": object()}}
    hass = Hass({integration.DOMAIN: {"services_registered": True, "entry1": data}})

    assert integration._get_entry_data(hass) == ("entry1", data)
    assert integration._get_endpoint_data(hass, "entry1__mix") is data


def test_multiple_entries_need_entry_id() -> None:
    integration = _load_integration()
    hass = Hass(
        {
            integration.DOMAIN: {
                "entry1": {"endpoints": {"entry1__mix": object()}},
                "entry2": {"endpoints": {"entry2__mix": object()}},
            }
        }
    )

    try:
        integration._get_entry_data(hass)
    except RuntimeError as err:
        assert "entry_id is required" in str(err)
    else:
        raise AssertionError("multiple entries should require entry_id")

    assert integration._get_entry_data(hass, "entry2")[0] == "entry2"
    assert integration._get_endpoint_data(hass, "entry2__mix") is hass.data[
        integration.DOMAIN
    ]["entry2"]


if __name__ == "__main__":
    test_single_entry_is_default()
    test_multiple_entries_need_entry_id()
    print("ok")
