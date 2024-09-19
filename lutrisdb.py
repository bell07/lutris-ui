import os
import subprocess

from lutris import settings
from lutris.database import games, categories


class LutrisDb:
    def __init__(self, ui_screen):
        self.games_data = []
        self.reload()
        self.running_game_popen = None
        self.ui_screen = ui_screen
        # os.setpgrp()  # Process group to kill

    def reload(self):
        self.games_data.clear()
        for game_data in games.get_games(filters={"installed": "1"}):
            game_categories = categories.get_categories_in_game(game_data["id"])
            if '.hidden' in game_categories:
                continue

            self.games_data.append(
                {"name": game_data["name"], "game_data": game_data, "coverart": self.get_cover_art(game_data)})

    @staticmethod
    def get_cover_art(game):
        image_path = os.path.join(settings.COVERART_PATH, f"{game['slug']}.jpg")
        if os.path.exists(image_path):
            return image_path

    def launch(self, game):
        self.running_game_popen = subprocess.Popen(
            ["env", "LUTRIS_SKIP_INIT=1", "lutris", f"lutris:rungameid/{game.data['id']}"])
        self.ui_screen.games_viewport.is_interactive = False
        self.ui_screen.game_is_running.game = game
        self.ui_screen.game_is_running.is_visible = True
        self.ui_screen.game_is_running.set_focus()

    def check_is_running(self):
        if self.running_game_popen is False:
            return False
        if self.running_game_popen.poll() is not None:
            return False
        return True

    def kill_running(self):
        self.running_game_popen.terminate()
