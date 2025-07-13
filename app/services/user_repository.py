from datetime import datetime
from typing import Optional
from app.config.backend import PostgresManager
from app.models.user import UserInDB

class UserRepository:
    async def get_user_by_google_id(self, google_id: str) -> Optional[UserInDB]:
        pool = await PostgresManager.get_pool()
        async with pool.acquire() as connection:
            user_record = await connection.fetchrow(
                "SELECT * FROM users WHERE google_id = $1", google_id
            )
            return UserInDB(**user_record) if user_record else None

    async def create_user_from_google(self, email: str, name: str, google_id: str) -> UserInDB:
        new_user = UserInDB.create_from_google(
            email=email,
            name=name,
            google_id=google_id
        )
        pool = await PostgresManager.get_pool()
        async with pool.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO users (email, name, username, google_id, games_played, achievements, current_game_details, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                new_user.email, new_user.name, new_user.username, new_user.google_id,
                new_user.games_played, new_user.achievements, new_user.current_game_details,
                new_user.created_at, new_user.updated_at
            )
        return new_user

    async def update_user_login(self, google_id: str, name: str) -> None:
        pool = await PostgresManager.get_pool()
        async with pool.acquire() as connection:
            await connection.execute(
                "UPDATE users SET name = $1, updated_at = $2 WHERE google_id = $3",
                name, datetime.utcnow(), google_id
            )