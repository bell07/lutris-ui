import os

from lutris import settings
from lutris.database import games, categories


class LutrisDb:
    def __init__(self):
        self.games_data = []
        self.reload()

    def reload(self):
        self.games_data.clear()
        for game in games.get_games(filters={"installed": "1"}):
            game_categories = categories.get_categories_in_game(game["id"])
            if '.hidden' in game_categories:
                continue

            self.games_data.append({
                "name": game["name"],
                "platform": game["platform"],
                "coverart": self.get_cover_art(game)
            })

    @staticmethod
    def get_cover_art(game):
        image_path = os.path.join(settings.COVERART_PATH, f"{game['slug']}.jpg")
        if os.path.exists(image_path):
            return image_path
