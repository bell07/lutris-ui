from __future__ import annotations

from configparser import ConfigParser
from os import makedirs, path, sep
from typing import TypeVar

from xdg import BaseDirectory

SAVE_DEFAULTS = False

_app_name = "lutris-ui"

_AnySetting = TypeVar("_AnySetting", str, int, float, bool)


class Settings:
    config: ConfigParser | None = None
    config_changed = False

    def __init__(self, module: str):
        self.module = module

    @staticmethod
    def open_config() -> None:
        if Settings.config is not None:
            return

        Settings.config = ConfigParser()
        for config_path in reversed(list(BaseDirectory.load_config_paths(_app_name))):
            config_file = path.join(config_path, "config.ini")
            if path.isfile(config_file):
                Settings.config.read(config_file)

    def set_default_value(self, key: str, value) -> None:
        if SAVE_DEFAULTS is False:
            return
        self.set(key, value)

    def get(self, key: str, default_value: _AnySetting) -> _AnySetting:
        self.open_config()
        assert Settings.config

        if Settings.config.has_section(self.module) is False:
            self.set_default_value(key, default_value)
            return default_value

        if Settings.config.has_option(self.module, key) is False:
            self.set_default_value(key, default_value)
            return default_value

        if type(default_value) is bool:
            value = Settings.config.getboolean(self.module, key)
        else:
            value = Settings.config.get(self.module, key)
        if value is None:
            self.set_default_value(key, default_value)
            return default_value

        return_type = type(default_value)
        return return_type(value)

    def get_str(self, key: str) -> str | None:
        assert Settings.config
        value = Settings.config.get(self.module, key)
        assert isinstance(value, str)
        return value

    def get_int(self, key: str) -> int | None:
        assert Settings.config
        return Settings.config.getint(self.module, key)

    def get_bool(self, key: str) -> bool | None:
        assert Settings.config
        return Settings.config.getboolean(self.module, key)

    def get_float(self, key: str) -> float | None:
        assert Settings.config
        return Settings.config.getfloat(self.module, key)

    def set(self, key: str, value) -> None:
        self.open_config()
        assert Settings.config

        if Settings.config.has_section(self.module) is False:
            Settings.config.add_section(self.module)
        Settings.config.set(self.module, key, str(value))
        Settings.config_changed = True

    @staticmethod
    def save() -> None:
        if Settings.config_changed is False:
            return
        assert Settings.config
        config_path = BaseDirectory.save_config_path(_app_name)
        if config_path is None:
            config_path = path.join(BaseDirectory.xdg_config_home, _app_name)
            makedirs(config_path, exist_ok=True)

        with open(path.join(config_path, "config.ini"), "w") as f:
            Settings.config.write(f)
            f.close()

    @staticmethod
    def get_ressource_path(file_name: str) -> str:
        # File in Development repository
        my_path = path.realpath(__file__).split(sep)
        if len(my_path) > 3 and my_path[-3] == "src" and my_path[-2] == _app_name:
            return path.join(sep.join(my_path[:-3]), "resources", file_name)

        # Check xdg paths
        for xdg_path in BaseDirectory.xdg_data_dirs:
            resource = path.join(xdg_path, _app_name, "resources", file_name)
            if path.isfile(resource):
                return resource

        return "/usr/share/lutris-ui/resources"
