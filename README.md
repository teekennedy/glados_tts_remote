# GLaDOS Piper Addon

![Supports aarch64 Architecture][aarch64-shield] ![Supports amd64 Architecture][amd64-shield]

This project is a downstream fork of the official [Home Assistant Piper addon][upstream] that uses the GLaDOS voice model from [dnhkng/GlaDOS].

The official addon limits the voices to a predefined set of models.
This fork adds GLaDOS as a voice option, and also provides a url option to allow you to download and use models from any source.

Using a custom model url breaks the model auto-update functionality, so that feature is disabled.
Instead, updates to the GLaDOS voice model will be done by releasing new versions of this forked addon.

## Installation

[![Add Repository to HA][my-ha-badge]][my-ha-url]

You can also install this addon manually by going to Settings -> Add-Ons -> Add-on Store -> Menu (three dots) -> Repositories and adding this repository's url.

## TODO

- [ ] Get fork working.
- [ ] GitHub action to validate addon.
- [ ] Update icon to distinguish this fork from the official one.
- [ ] Setup action to periodically check for and incorporate upstream changes.

## License

This project is licensed based on its [upstream] which is Apache 2.0. The GLaDOS models are MIT licensed.

[upstream]: https://github.com/home-assistant/addons/tree/master/piper
[dnhkng/GlaDOS]: https://github.com/dnhkng/GlaDOS
[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[my-ha-badge]: https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg
[my-ha-url]: https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?
