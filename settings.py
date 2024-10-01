import configparser
import os

from xdg import BaseDirectory

SAVE_DEFAULTS = False


class Settings:
    config_file = os.path.join(BaseDirectory.xdg_config_home, 'lutris-ui', 'config.ini')
    config = None
    config_changed = False

    def __init__(self, module: str):
        self.module = module

    @staticmethod
    def open_config() -> None:
        if Settings.config is None:
            Settings.config = configparser.ConfigParser()
            Settings.config.read(Settings.config_file)

    def set_default_value(self, key: str, value: any) -> None:
        if SAVE_DEFAULTS is False:
            return
        self.set(key, value)

    def get(self, key: str, default_value=None) -> any:
        self.open_config()

        if Settings.config.has_section(self.module) is False:
            self.set_default_value(key, default_value)
            return default_value

        if Settings.config.has_option(self.module, key) is False:
            self.set_default_value(key, default_value)
            return default_value

        if default_value is not None and type(default_value) is bool:
            value = Settings.config.getboolean(self.module, key)
        else:
            value = Settings.config.get(self.module, key)
        if value is None:
            self.set_default_value(key, default_value)
            return default_value

        if default_value is not None:
            return_type = type(default_value)
            return return_type(value)

        return value

    def set(self, key: str, value: any) -> None:
        self.open_config()

        if Settings.config.has_section(self.module) is False:
            Settings.config.add_section(self.module)
        Settings.config.set(self.module, key, str(value))
        Settings.config_changed = True

    @staticmethod
    def save() -> None:
        if Settings.config_changed is False:
            return
        os.makedirs(os.path.dirname(Settings.config_file), exist_ok=True)
        with open(Settings.config_file, 'w') as f:
            Settings.config.write(f)
            f.close()
