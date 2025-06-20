from __future__ import annotations

import os
import subprocess

from lutris import settings
from lutris.database import categories, games
from settings import Settings
from shutdown_handler import ShutdownManager


class LutrisDb:
    def __init__(self):
        list_settings = Settings("gamelist")
        self._sort_key: str = str(
            list_settings.get("sort_attribute", "lastplayed")
        )  # sortname, lastplayed, installed_at
        self._sort_reverse: bool = bool(list_settings.get("reverse_sort", True))
        self.data_changed = True
        self.games_data = [str, any]
        self.shutdown_manager: ShutdownManager | None
        self.terminate_in_proces = False

    def get_games(self) -> tuple[list, bool]:
        if self.data_changed is False:
            return self.games_data, False
        self.games_data.clear()
        for game_data in games.get_games(filters={"installed": "1"}):
            game_categories = categories.get_categories_in_game(game_data["id"])
            if ".hidden" in game_categories:
                continue
            data = game_data.copy()
            data["coverart"] = self.get_cover_art(game_data)
            self.games_data.append(data)

        # Note:  fallback "0" is for non-existing lastplayed value. This should not affect sorting by name
        self.games_data.sort(
            key=lambda game: game.get(self._sort_key) or 0, reverse=self._sort_reverse
        )
        self.data_changed = False
        return self.games_data, True

    @staticmethod
    def get_cover_art(game: dict) -> str | None:
        image_path = os.path.join(settings.COVERART_PATH, f"{game['slug']}.jpg")
        if os.path.exists(image_path):
            return image_path
        image_path = os.path.join(settings.COVERART_PATH, f"{game['slug']}.png")
        if os.path.exists(image_path):
            return image_path

    def launch(self, game_data: dict) -> None:
        print(f"Launch Lutris session for {game_data['name']}")
        p = subprocess.Popen(
            [
                "env",
                "LUTRIS_SKIP_INIT=1",
                "lutris",
                f"lutris:rungameid/{game_data['id']}",
            ],
            start_new_session=True,
        )
        self.shutdown_manager = ShutdownManager(p.pid)
        self.terminate_in_proces = False

    def check_is_running(self, kill_in_progress: bool = False) -> bool:
        if self.shutdown_manager is None:
            return False

        is_running = self.shutdown_manager.check_is_running(check_all=kill_in_progress)
        if is_running is False:
            self.shutdown_manager = None
        return is_running

    def kill_running(self) -> None:
        if self.shutdown_manager:
            self.shutdown_manager.shutdown_game()
