import json5 as json
import os

from xdg import BaseDirectory

SAVE_DEFAULTS = False


class Settings:
    all_settings = None
    config_file = os.path.join(BaseDirectory.xdg_config_home, 'lutris-ui', 'config.json5')

    def __init__(self, module):
        self.module = module

    def get(self, key: str, default_value=None) -> any:
        if Settings.all_settings is None:
            if os.path.exists(Settings.config_file):
                with open(Settings.config_file, 'r') as f:
                    Settings.all_settings = json.load(f)
                    f.close()
        if Settings.all_settings is None:
            Settings.all_settings = {}

        module_settings = Settings.all_settings.get(self.module) or {}
        value = module_settings.get(key)
        if value is None:
            if SAVE_DEFAULTS is True:
                self.set(key, default_value)
            return default_value
        return value

    def set(self, key: str, value: any) -> None:
        module_settings = Settings.all_settings.get(self.module) or {}
        module_settings[key] = value
        Settings.all_settings[self.module] = module_settings

    @staticmethod
    def save() -> None:
        os.makedirs(os.path.dirname(Settings.config_file), exist_ok=True)
        with open(Settings.config_file, 'w') as f:
            json.dump(Settings.all_settings, f)
            f.close()
