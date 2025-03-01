from fastapi import HTTPException
from typing import Any, Dict, Optional
from http import HTTPStatus


class GameError(HTTPException):
    """Base exception class for game-related errors."""
    
    def __init__(
        self, 
        status_code: int = 400, 
        detail: str = "Game error occurred",
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class RoomError(GameError):
    """Exception for room-related errors."""
    pass


class NotHostError(RoomError):
    """Exception for when a user attempts an action that requires host privileges."""
    
    def __init__(self, room_id: str):
        super().__init__(
            status_code=HTTPStatus.FORBIDDEN,
            detail=f"Only the host can perform this action in room {room_id}"
        )


class NotInRoomError(RoomError):
    """Exception for when a user attempts an action in a room they're not in."""
    
    def __init__(self, room_id: str):
        super().__init__(
            status_code=HTTPStatus.FORBIDDEN,
            detail=f"You are not in room {room_id}"
        )


class NotYourTurnError(RoomError):
    """Exception for when a user attempts an action when it's not their turn."""
    
    def __init__(self, room_id: str):
        super().__init__(
            status_code=HTTPStatus.FORBIDDEN,
            detail=f"It's not your turn in room {room_id}"
        )


class RoomFullError(RoomError):
    """Exception for when a user attempts to join a full room."""
    
    def __init__(self, room_id: str, max_players: int):
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Room {room_id} is full (max {max_players} players)"
        )


class RoomNotFoundError(RoomError):
    """Exception for when a room doesn't exist."""
    
    def __init__(self, room_id: str):
        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Room {room_id} not found"
        )


class GameAlreadyStartedError(RoomError):
    """Exception for when a game has already started."""
    
    def __init__(self, room_id: str):
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Game in room {room_id} has already started"
        )


class NotEnoughPlayersError(RoomError):
    """Exception for when there aren't enough players to start a game."""
    
    def __init__(self, room_id: str, current_players: int, min_players: int):
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Not enough players in room {room_id} ({current_players}/{min_players})"
        )


class UserNotFoundError(GameError):
    """Exception for when a user is not found in the database."""
    
    def __init__(self):
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="User not found. Please log in again."
        )