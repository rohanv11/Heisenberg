from app.schemas.room import RoomFull
from typing import Dict

game_rooms: Dict[str, RoomFull] = {}
player_to_game_rooms: Dict[str, str] = {}

