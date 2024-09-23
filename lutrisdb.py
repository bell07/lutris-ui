import os
import signal
import subprocess

import psutil
from lutris import settings
from lutris.database import games, categories


class LutrisDb:
    def __init__(self):
        self.games_data = []
        self.reload()
        self.running_game_pid = None

    def reload(self) -> None:
        self.games_data.clear()
        for game_data in games.get_games(filters={"installed": "1"}):
            game_categories = categories.get_categories_in_game(game_data["id"])
            if '.hidden' in game_categories:
                continue
            data = game_data.copy()
            data["coverart"] = self.get_cover_art(game_data)
            self.games_data.append(data)

    @staticmethod
    def get_cover_art(game: dict) -> str:
        image_path = os.path.join(settings.COVERART_PATH, f"{game['slug']}.jpg")
        if os.path.exists(image_path):
            return image_path

    def launch(self, game_data: dict) -> None:
        print(f"Launch Lutris session for {game_data['name']}")
        running_game_popen = subprocess.Popen(
            ["env", "LUTRIS_SKIP_INIT=1", "lutris", f"lutris:rungameid/{game_data['id']}"], stdout=subprocess.PIPE)

        while True:
            line = running_game_popen.stdout.readline().strip()
            print(str(line))
            if str(line).find("Started initial process") >= 0:
                self.running_game_pid = int(line.split()[3])
                break

    def check_is_running(self) -> bool:
        if self.running_game_pid is None:
            return False
        if psutil.pid_exists(self.running_game_pid) is False:
            print("Lutris session closed")
            self.running_game_pid = None
            return False
        return True

    def kill_running(self) -> None:
        if self.running_game_pid is not None:
            print("Kill game")
            try:
                os.kill(self.running_game_pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        else:
            print("Try to kill not running game :-(")
