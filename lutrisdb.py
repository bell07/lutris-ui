import os
import signal
import subprocess

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
        self.wrapper_pid = None
        self.launch_pid = None
        self.pid_list = []
        self.last_seen = 0
        self.last_pid_count = 0
        self.terminate_in_proces = False

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
        p = subprocess.Popen(["env", "LUTRIS_SKIP_INIT=1", "lutris", f"lutris:rungameid/{game_data['id']}"],
                             start_new_session=True)
        self.launch_pid = p.pid
        self.pid_list = [p.pid]
        self.wrapper_pid = None
        self.last_seen = 0
        self.last_pid_count = 0
        self.terminate_in_proces = False

    def check_is_running(self) -> bool:
        if self.wrapper_pid is None:
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
                    self.wrapper_pid = process.pid
                    if not (process.pid in self.pid_list):
                        self.pid_list.append(process.pid)

        for pid in self.pid_list:
            try:
                p = psutil.Process(pid=pid)

                if p.status() == 'zombie':
                    try:
                        p.wait(timeout=1)
                    except psutil.TimeoutExpired:
                        pass

                if p.is_running():
                    for child in p.children():
                        if not (child.pid in self.pid_list):
                            self.pid_list.append(child.pid)
            except psutil.NoSuchProcess:
                self.pid_list.remove(pid)
                continue

        if len(self.pid_list) == 0:  # All processes killed
            if self.terminate_in_proces is False:
                self.last_seen = self.last_seen + 1
                if self.last_seen <= 6:  # Wait 6 times. Each step is ~ 300 msps
                    return True
            print("Lutris session closed")
            return False
        else:
            self.last_seen = 0
        return True

    def kill_running(self) -> None:
        self.terminate_in_proces = True
        if self.last_pid_count == 0:
            self.last_pid_count = len(self.pid_list)
        completed_count = self.last_pid_count - len(self.pid_list)
        current_count = len(self.pid_list)
        if completed_count > 0 or current_count == 0:
            self.last_pid_count = current_count
            return

        for idx in range(len(self.pid_list) - 1, self.last_pid_count - 2, -1):
            try:
                pid = self.pid_list[idx]
                os.kill(pid, signal.SIGTERM)
            except IndexError:
                break
            except ProcessLookupError:
                continue
            print(f"PID {pid} killed")
        self.last_pid_count = current_count
