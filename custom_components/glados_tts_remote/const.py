"""Constants for glados_tts_remote"""

from homeassistant.components.tts import DOMAIN as TTS_DOMAIN

DOMAIN = "glados_tts_remote"

PLATFORMS = [TTS_DOMAIN]

SUPPORTED_LANGUAGES = ["en-US"]

DEFAULT_LANG = "en-US"
DEFAULT_URL = "http://localhost:8124"
