"""Config flow for GLaDOS TTS integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries, exceptions
from homeassistant.core import HomeAssistant

from .const import DOMAIN, SUPPORTED_LANGUAGES  # pylint:disable=unused-import
from .tts import GladosProvider

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({("host"): str})


async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    # Validate the data can be used to set up a connection.

    if len(data["url"]) < 3:
        raise InvalidUrl

    if data["language"] not in SUPPORTED_LANGUAGES:
        raise InvalidLanguage


    provider = GladosProvider(hass, data["language"], data["url"])
    # The dummy hub provides a `test_connection` method to ensure it's working
    # as expected
    result = await provider.async_test_connection()
    if not result:
        # If there is an error, raise an exception to notify HA that there was a
        # problem. The UI will also show there was a problem
        raise ConnectionTestFailed

    # Return info that you want to store in the config entry.
    # "Title" is what is displayed to the user for this hub device
    # It is stored internally in HA as part of the device config.
    # See `async_step_user` below for how this is used
    return {"title": data["url"]}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hello World."""

    VERSION = 1
    # Pick one of the available connection classes in homeassistant/config_entries.py
    # This tells HA if it should be asking for updates, or it'll be notified of updates
    # automatically. This example uses PUSH, as the dummy hub will notify HA of
    # changes.
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        # This goes through the steps to take the user through the setup process.
        # Using this it is possible to update the UI and prompt for additional
        # information. This example provides a single form (built from `DATA_SCHEMA`),
        # and when that has some validated input, it calls `async_create_entry` to
        # actually create the HA config entry. Note the "title" value is returned by
        # `validate_input` above.
        errors = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)

                return self.async_create_entry(title=info["title"], data=user_input)
            except ConnectionTestFailed:
                errors["url"] = "connection_test_failed"
            except InvalidUrl:
                # The error string is set here, and should be translated.
                # This example does not currently cover translations, see the
                # comments on `DATA_SCHEMA` for further details.
                # Set the error on the `host` field, not the entire form.
                errors["url"] = "cannot_connect"
            except InvalidLanguage:
                errors["language"] = "unsupported_language"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class ConnectionTestFailed(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidUrl(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid server url."""

class InvalidLanguage(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid language."""
