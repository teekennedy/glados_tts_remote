import asyncio
import logging
from urllib.parse import quote

import aiohttp
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.tts import CONF_LANG
from homeassistant.components.tts import PLATFORM_SCHEMA as TTS_PLATFORM_SCHEMA
from homeassistant.components.tts import Provider
from homeassistant.const import CONF_URL
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DEFAULT_LANG, DEFAULT_URL, SUPPORTED_LANGUAGES

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = TTS_PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_LANG, default=DEFAULT_LANG): vol.In(SUPPORTED_LANGUAGES),
        vol.Optional(CONF_URL, default=DEFAULT_URL): cv.string,
    }
)


def get_engine(hass, config, discovery_info=None):
    """Set up Pico speech component."""
    return GladosProvider(hass, config[CONF_LANG], config[CONF_URL])


class GladosProvider(Provider):
    """GLaDOS TTS API provider."""

    def __init__(self, hass, lang, url):
        """Initialize GLaDOS TTS provider."""
        self._hass = hass
        self._lang = lang
        self._url = url
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
            with asyncio.timeout(5):
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

        try:
            with asyncio.timeout(5):
                url = f"{self._url}/say"
                encoded_message = quote(message)
                url_param = {
                    "lang": language,
                    "text": encoded_message,
                }

                request = await websession.get(url, params=url_param)

                if request.status != 200:
                    _LOGGER.error(
                        "Error %d on load url %s", request.status, request.url
                    )
                    return (None, None)
                data = await request.read()

        except (asyncio.TimeoutError, aiohttp.ClientError):
            _LOGGER.error("Timeout for GLaDOS TTS API")
            return (None, None)

        if data:
            return ("wav", data)
        return (None, None)
