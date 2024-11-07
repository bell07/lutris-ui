import configparser
import os

from xdg import BaseDirectory

SAVE_DEFAULTS = False

_app_name = "lutris-ui"


class Settings:
    config = None
    config_changed = False

    def __init__(self, module: str):
        self.module = module

    @staticmethod
    def open_config() -> None:
        if Settings.config is not None:
            return

        Settings.config = configparser.ConfigParser()
        for path in reversed(list(BaseDirectory.load_config_paths(_app_name))):
            file = os.path.join(path, 'config.ini')
            if os.path.isfile(file):
                Settings.config.read(file)

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
        config_path = BaseDirectory.save_config_path(_app_name)
        if config_path is None:
            config_path = os.path.join(BaseDirectory.xdg_config_home, _app_name)
            os.makedirs(config_path, exist_ok=True)

        with open(os.path.join(config_path, 'config.ini'), 'w') as f:
            Settings.config.write(f)
            f.close()

    @staticmethod
    def get_ressource_path(file_name: str) -> str:
        # File in Development repository
        my_path = os.path.realpath(__file__).split(os.sep)
        if len(my_path) > 3 and my_path[-3] == "src" and my_path[-2] == _app_name:
            if my_path[0] == '':
                my_path[0] = os.sep
            resource = os.path.join(*my_path[:-3], "resources", file_name)
            if os.path.isfile(resource):
                return resource

        # Check xdg paths
        for path in BaseDirectory.xdg_data_dirs:
            resource = os.path.join(path, _app_name, file_name)
            if os.path.isfile(resource):
                return resource
