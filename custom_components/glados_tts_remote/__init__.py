"""Adds GLaDOS TTS Engine"""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload Entry"""
    all_ok = True
    for platform in PLATFORMS:
        if not await hass.config_entries.async_forward_entry_unload(entry, platform):
            all_ok = False

    return all_ok
