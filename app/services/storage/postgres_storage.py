import asyncpg
from typing import Optional

from .storage_interface import Storage
from app.models.game_models import Room
from app.models.user import UserInDB
from app.config.settings import DATABASE_URL

class PostgresStorage(Storage):
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(DATABASE_URL)

    async def close(self):
        await self.pool.close()

    async def create_room(self, room: Room) -> None:
        async with self.pool.acquire() as connection:
            await connection.execute(
                "INSERT INTO rooms (room_id, room_code, data) VALUES ($1, $2, $3)",
                room.room_id,
                room.room_code,
                room.model_dump_json()
            )

    async def get_room(self, room_id: str) -> Optional[Room]:
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("SELECT data FROM rooms WHERE room_id = $1", room_id)
            return Room.model_validate_json(row['data']) if row else None

    async def get_room_by_code(self, room_code: str) -> Optional[Room]:
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow("SELECT data FROM rooms WHERE room_code = $1", room_code)
            return Room.model_validate_json(row['data']) if row else None

    async def update_room(self, room: Room) -> None:
        async with self.pool.acquire() as connection:
            await connection.execute(
                "UPDATE rooms SET data = $1 WHERE room_id = $2",
                room.model_dump_json(),
                room.room_id
            )

    async def get_player_room(self, user: UserInDB) -> Optional[Room]:
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow(
                "SELECT data FROM rooms WHERE data->'players'->>$1 IS NOT NULL",
                user.google_id
            )
            return Room.model_validate_json(row['data']) if row else None
