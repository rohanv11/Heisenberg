import json
import os
from app.models.game_models import BoardData

class BoardService:
    _boards = {}

    @classmethod
    def load_boards(cls):
        """Load board data from JSON file."""
        try:
            with open(os.path.join("app", "models", "boards.json")) as f:
                boards = json.load(f)
                for country_code, board_data in boards.items():
                    cls._boards[country_code.upper()] = BoardData(**board_data)
        except Exception as e:
            raise RuntimeError(f"Failed to load board data: {str(e)}")

    @classmethod
    def get_board(cls, country_code: str) -> BoardData:
        """Get board data for a specific country."""
        board = cls._boards.get(country_code.upper())
        if not board:
            raise ValueError(f"Board not found for country code: {country_code}")
        return board
