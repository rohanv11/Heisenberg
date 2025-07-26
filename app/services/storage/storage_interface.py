from abc import ABC, abstractmethod
from typing import Optional

from app.models.game_models import Room
from app.models.user import UserInDB

class Storage(ABC):
    @abstractmethod
    async def create_room(self, room: Room) -> None:
        pass

    @abstractmethod
    async def get_room(self, room_id: str) -> Optional[Room]:
        pass

    @abstractmethod
    async def get_room_by_code(self, room_code: str) -> Optional[Room]:
        pass

    @abstractmethod
    async def update_room(self, room: Room) -> None:
        pass

    @abstractmethod
    async def get_player_room(self, user: UserInDB) -> Optional[Room]:
        pass
