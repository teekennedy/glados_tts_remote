import asyncio
import logging
from urllib.parse import quote

import aiohttp
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.tts import CONF_LANG
from homeassistant.components.tts import DOMAIN as TTS_DOMAIN
from homeassistant.components.tts import PLATFORM_SCHEMA as TTS_PLATFORM_SCHEMA
from homeassistant.components.tts import Provider
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_TIMEOUT, CONF_URL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (DEFAULT_LANG, DEFAULT_TIMEOUT, DEFAULT_URL,
                    SUPPORTED_LANGUAGES)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = TTS_PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_LANG, default=DEFAULT_LANG): vol.In(SUPPORTED_LANGUAGES),
        vol.Optional(CONF_URL, default=DEFAULT_URL): vol.Any(cv.url_no_path, None),
        vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): int,
    }
)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_forward_entry_setups(entry, [TTS_DOMAIN])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload Entry"""
    return await hass.config_entries.async_forward_entry_unload(entry, TTS_DOMAIN)


def get_engine(hass, config, discovery_info=None):
    """Set up Pico speech component."""
    return GladosProvider(hass, config[CONF_LANG], config[CONF_URL], config[CONF_TIMEOUT])


class GladosProvider(Provider):
    """GLaDOS TTS API provider."""

    def __init__(self, hass, lang, url, timeout):
        """Initialize GLaDOS TTS provider."""
        self._hass = hass
        self._lang = lang
        self._url = url
        self._timeout = timeout
        self.name = "GLaDOS TTS (Remote)"
        _LOGGER.info("Initialized ", self.name)


    @property
    def default_language(self):
        """Return the default language."""
        return self._lang

    @property
    def supported_languages(self):
        """Return list of supported languages."""
        return SUPPORTED_LANGUAGES

    async def async_test_connection(self) -> bool:
        """Test TTS url using healthcheck endpoint"""
        _LOGGER.info("Using url", self._url)
        websession = async_get_clientsession(self._hass)

        try:
            async with asyncio.timeout(self._timeout):
                url = f"{self._url}/health"

                request = await websession.get(url)
                if request.status == 200:
                    return True
                return False

        except (asyncio.TimeoutError, aiohttp.ClientError):
            return False

    async def async_get_tts_audio(self, message, language, options=None):
        """Load TTS using a remote server."""
        _LOGGER.info("Using url", self._url)
        websession = async_get_clientsession(self._hass)
        format = "mp3"

        url = f"{self._url}/say"
        try:
            async with asyncio.timeout(self._timeout):
                encoded_message = quote(message)
                url_param = {
                    "lang": language,
                    "text": encoded_message,
                    "format": format,
                }

                request = await websession.get(url, params=url_param)

                if request.status != 200:
                    _LOGGER.error(
                        "Error %d on load url %s", request.status, request.url
                    )
                    return (None, None)
                data = await request.read()

        except (asyncio.TimeoutError, aiohttp.ClientError):
            _LOGGER.error(f"Timeout for GLaDOS TTS API. Url: {url}")
            return (None, None)

        if data:
            return (format, data)
        return (None, None)
