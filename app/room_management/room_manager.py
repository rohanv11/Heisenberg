import threading

from app.core.socket_manager import sio
from app.utils.common import generate_code
from app.schemas.room import RoomCreate, RoomFull
from app.core.game_config import game_rooms, player_to_game_rooms
from app.room_management.room_validator import RoomValidator


# Singleton
class RoomManager:
    __instance = None
    __lock = threading.Lock()


    def __new__(cls):
        if cls.__instance is None:
            with cls.__lock:
                if cls.__instance is None:
                    cls.__instance = super(RoomManager, cls).__new__(cls)
        
        
        return cls.__instance

    def __init__(self):
        pass

    async def get_all_rooms(self) -> list[dict]:
        """
        Get a list of all rooms, including their details.

        Returns:
            list[dict]: A list of room details.
        """
        return [
            {"room_code": code, "members": details["members"], "public": details["public"]}
            for code, details in game_rooms.items()
        ]

    async def get_room_by_id(self, room_code: str) -> dict:
        room = game_rooms.get(room_code)
        if not room:
            raise ValueError(f"Room with code '{room_code}' not found.")
        return {"room_code": room_code, **room}

    async def create_room(self, room_data: RoomCreate, player_id: str) -> RoomFull:
        RoomValidator.validate_room_creation(player_id=player_id)
        room_code = self._generate_unique_code()
        room_full = RoomFull(**room_data.dict(), 
                             room_code=room_code, 
                             players=[player_id])
        game_rooms[room_code] = room_full
        player_to_game_rooms[player_id] = room_code
        return room_full


    async def delete_room(self, room_code: str) -> dict:
        if room_code not in game_rooms:
            raise ValueError(f"Room with code '{room_code}' not found.")
        room_details = game_rooms.pop(room_code)
        return {"room_code": room_code, **room_details}

    async def remove_player_from_all_rooms(self, sid: str):
        """
        Remove a player from all rooms they are part of.

        Args:
            sid (str): Socket ID of the player.

        Emits:
            room_update: Updates all connected clients about the room's new state.
        """
        for code, details in list(game_rooms.items()):
            if sid in details["members"]:
                details["members"].remove(sid)
                if not details["members"]:
                    del game_rooms[code]  # Delete the room if empty
                else:
                    await sio.emit(
                        "room_update",
                        {"room": code, "members": details["members"]},
                        room=code,
                    )

    def _generate_unique_code(self) -> str:
        """
        Generate a unique room code.

        Returns:
            str: A unique room code.
        """
        room_code = generate_code()
        while room_code in game_rooms:
            room_code = generate_code()
        return room_code
