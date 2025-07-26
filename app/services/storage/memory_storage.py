from typing import Dict, Optional

from .storage_interface import Storage
from app.models.game_models import Room
from app.models.user import UserInDB

class MemoryStorage(Storage):
    def __init__(self):
        self.rooms: Dict[str, Room] = {}

    async def create_room(self, room: Room) -> None:
        self.rooms[room.room_id] = room

    async def get_room(self, room_id: str) -> Optional[Room]:
        return self.rooms.get(room_id)

    async def get_room_by_code(self, room_code: str) -> Optional[Room]:
        for room in self.rooms.values():
            if room.room_code == room_code:
                return room
        return None

    async def update_room(self, room: Room) -> None:
        self.rooms[room.room_id] = room

    async def get_player_room(self, user: UserInDB) -> Optional[Room]:
        for room in self.rooms.values():
            if user.google_id in room.players:
                return room
        return None
