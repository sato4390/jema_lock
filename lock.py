"""Jema lock"""
from __future__ import annotations

from urllib.parse import urljoin
import logging
import asyncio
from typing import Any
import voluptuous as vol
import requests
from requests.auth import HTTPDigestAuth

import homeassistant.helpers.config_validation as cv
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, CONF_URL, CONF_NAME
from homeassistant.components.lock import PLATFORM_SCHEMA
from homeassistant.const import (
    STATE_LOCKED,
    STATE_LOCKING,
    STATE_UNLOCKED,
    STATE_UNLOCKING,
)
from homeassistant.components.lock import (
    LockEntity,
)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_URL): cv.string,
        vol.Required(CONF_USERNAME, default="admin"): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    name = config[CONF_NAME]
    url = config[CONF_URL]
    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]

    add_entities([JemaLock(hass, name, url, username, password)])


class JemaLock(LockEntity):
    """Jema Lock"""

    def __init__(
        self, hass: HomeAssistant, name: str, url: str, username: str, password: str
    ) -> None:
        super().__init__()
        self._hass = hass
        self._attr_name = name
        self._url = url
        self._username = username
        self._password = password

        self._state = STATE_LOCKED

    @property
    def is_locking(self) -> bool | None:
        return self._state == STATE_LOCKING

    @property
    def is_locked(self) -> bool | None:
        return self._state == STATE_LOCKED

    @property
    def is_unlocking(self) -> bool | None:
        return self._state == STATE_UNLOCKING

    async def async_lock(self, **kwargs: Any) -> None:
        _LOGGER.debug("lock")
        self._state = STATE_LOCKING
        self.async_write_ha_state()
        await self._hass.async_add_executor_job(
            self.request, "/cgi-bin/jemaStat?Jema=ON"
        )
        self._state = STATE_LOCKED
        self.async_write_ha_state()

        await asyncio.sleep(3)

    async def async_unlock(self, **kwargs: Any) -> None:
        _LOGGER.debug("unlock")
        self._state = STATE_UNLOCKING
        self.async_write_ha_state()
        await self._hass.async_add_executor_job(
            self.request, "/cgi-bin/jemaStat?Jema=OFF"
        )
        self._state = STATE_UNLOCKED
        self.async_write_ha_state()

        await asyncio.sleep(3)

    async def async_update(self) -> None:
        _LOGGER.debug(f"update: {self._url}")

        r = await self._hass.async_add_executor_job(self.request, "/cgi-bin/jemaStat")

        if "<body bgcolor=#ffffff>ON</body>" in r.text:
            self._state = STATE_LOCKED
        else:
            self._state = STATE_UNLOCKED

    def request(self, path):
        return requests.get(
            urljoin(self._url, path),
            auth=HTTPDigestAuth(self._username, self._password),
            timeout=10,
        )
