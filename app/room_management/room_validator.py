from app.core.game_config import player_to_game_rooms
from app.utils.exceptions import RoomValidationException

class RoomValidator:
    def __init__(self):
        pass

    @staticmethod
    def validate_room_creation(player_id: str):
        if player_id in player_to_game_rooms:
            raise RoomValidationException(error_message="Player is already in a room.", status_code=400,
                                          data={"player_id": player_id, "room_code": player_to_game_rooms[player_id]})