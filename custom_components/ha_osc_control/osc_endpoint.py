"""OSC Endpoint entity base class."""
from __future__ import annotations

import logging
from typing import Any

from pythonosc import udp_client

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, VALUE_TYPE_BOOL, VALUE_TYPE_FLOAT, VALUE_TYPE_INT

_LOGGER = logging.getLogger(__name__)


class OSCEndpoint:
    """Representation of an OSC endpoint (target destination + address)."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        name: str,
        host: str,
        port: int,
        osc_address: str,
        value_type: str = VALUE_TYPE_FLOAT,
        unique_id: str | None = None,
    ) -> None:
        """Initialize the OSC endpoint."""
        self.hass = hass
        self.entry_id = entry_id
        self.name = name
        self.host = host
        self.port = port
        self.osc_address = osc_address
        self.value_type = value_type
        self.unique_id = unique_id or f"{entry_id}_{osc_address.replace('/', '_')}"
        self._client = udp_client.SimpleUDPClient(host, port)

    async def send_value(self, value: Any) -> None:
        """Send a value to this OSC endpoint."""
        # Convert value based on type
        if self.value_type == VALUE_TYPE_INT:
            send_value = int(value)
        elif self.value_type == VALUE_TYPE_BOOL:
            send_value = bool(value)
        else:  # VALUE_TYPE_FLOAT
            send_value = float(value)

        try:
            await self.hass.async_add_executor_job(
                self._client.send_message, self.osc_address, send_value
            )
            _LOGGER.debug(
                "Sent OSC message to %s:%s%s with value %s",
                self.host,
                self.port,
                self.osc_address,
                send_value,
            )
        except Exception as err:
            _LOGGER.error("Failed to send OSC message: %s", err)

    def to_dict(self) -> dict[str, Any]:
        """Convert endpoint to dictionary."""
        return {
            "name": self.name,
            "host": self.host,
            "port": self.port,
            "osc_address": self.osc_address,
            "value_type": self.value_type,
            "unique_id": self.unique_id,
        }
