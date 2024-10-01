import os
import signal
import subprocess
from pygame import time

import psutil
from lutris import settings
from lutris.database import games, categories

from settings import Settings


class LutrisDb:
    def __init__(self):
        list_settings = Settings("gamelist")
        self._sort_key = list_settings.get("sort_attribute", "lastplayed")  # sortname, lastplayed, installed_at
        self._sort_reverse = list_settings.get("reverse_sort", True)
        self.data_changed = True
        self.games_data = []
        self.running_game_popen = None

    def get_games(self) -> tuple[list, bool]:
        if self.data_changed is False:
            return self.games_data, False
        self.games_data.clear()
        for game_data in games.get_games(filters={"installed": "1"}):
            game_categories = categories.get_categories_in_game(game_data["id"])
            if '.hidden' in game_categories:
                continue
            data = game_data.copy()
            data["coverart"] = self.get_cover_art(game_data)
            self.games_data.append(data)

        # Note:  fallback "0" is for non existing lastplayed value. This should not affect sorting by name
        self.games_data.sort(key=lambda game: game.get(self._sort_key) or 0, reverse=self._sort_reverse)
        self.data_changed = False
        return self.games_data, True

    @staticmethod
    def get_cover_art(game: dict) -> str:
        image_path = os.path.join(settings.COVERART_PATH, f"{game['slug']}.jpg")
        if os.path.exists(image_path):
            return image_path
        image_path = os.path.join(settings.COVERART_PATH, f"{game['slug']}.png")
        if os.path.exists(image_path):
            return image_path

    def launch(self, game_data: dict) -> None:
        print(f"Launch Lutris session for {game_data['name']}")
        self.running_game_popen = subprocess.Popen(
            ["env", "LUTRIS_SKIP_INIT=1", "lutris", f"lutris:rungameid/{game_data['id']}"], start_new_session=True)
        time.wait(1000)

    def get_lutris_pid(self) -> int | None:
        if self.running_game_popen is None:
            return

        for process in psutil.process_iter():
            try:
                if process.uids().real != os.getuid():
                    continue
                cmdline = process.cmdline()
            except psutil.ZombieProcess:
                continue
            except psutil.NoSuchProcess:
                continue

            if len(cmdline) > 0 and cmdline[0].startswith("lutris-wrapper:"):
                return process.pid

        if self.running_game_popen.poll() is None:
            return self.running_game_popen.pid

        print("Lutris session closed")
        self.data_changed = True  # Force reload

    def kill_running(self) -> None:
        pid = self.get_lutris_pid()
        if pid is not None:
            print(f"Kill game PID {pid}")
            os.kill(pid, signal.SIGTERM)
