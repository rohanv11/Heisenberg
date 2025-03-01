"""
API routes for room management.
"""
from fastapi import APIRouter, HTTPException, Body, Depends, status
from typing import List, Optional, Dict
from pydantic import BaseModel

from app.services.room_service import RoomServiceWithAuth
from app.models.room import Room, RoomStatus
from app.models.game import GameConfig
from app.models.player import Player
from app.models.user import UserInDB
from app.models.exceptions import GameError
from app.api.dependencies import get_current_user


router = APIRouter()


class CreateRoomRequest(BaseModel):
    room_name: str
    even_build: Optional[bool] = True
    starting_cash: Optional[int] = 1500
    max_players: Optional[int] = 4


@router.post("/rooms", response_model=Dict)
async def create_room(
    request: CreateRoomRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Create a new room with the authenticated user as host.
    """
    try:
        room_service = RoomServiceWithAuth.get_instance()
        config = GameConfig(
            even_build=request.even_build,
            starting_cash=request.starting_cash,
            max_players=request.max_players
        )
        result = await room_service.create_room(request.room_name, current_user, config)
        return result
    except GameError as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/rooms", response_model=List[Room])
async def list_rooms(
    status: Optional[str] = None,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    List all rooms, optionally filtered by status.
    """
    try:
        room_service = RoomServiceWithAuth.get_instance()
        room_status = None
        if status is not None:
            try:
                room_status = RoomStatus(status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
        
        return room_service.list_rooms(room_status)
    except GameError as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/rooms/{room_id}", response_model=Room)
async def get_room(
    room_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get a room by ID.
    """
    try:
        room_service = RoomServiceWithAuth.get_instance()
        return room_service.get_room(room_id)
    except GameError as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/rooms/{room_id}/join", response_model=Player)
async def join_room(
    room_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Join a room using the authenticated user.
    """
    try:
        room_service = RoomServiceWithAuth.get_instance()
        player = await room_service.join_room(room_id, current_user)
        return player
    except GameError as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/rooms/{room_id}/start")
async def start_game(
    room_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Start a game in the room. Only the host can start the game.
    """
    try:
        room_service = RoomServiceWithAuth.get_instance()
        success = await room_service.start_game(room_id, current_user)
        return {"status": "started"}
    except GameError as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/rooms/{room_id}/end-turn")
async def end_turn(
    room_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    End the current player's turn. Only the current player can end their turn.
    """
    try:
        room_service = RoomServiceWithAuth.get_instance()
        success = await room_service.end_turn(room_id, current_user)
        return {"status": "turn ended"}
    except GameError as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/rooms/{room_id}/players", response_model=List[Player])
async def get_players(
    room_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get all players in a room.
    """
    try:
        room_service = RoomServiceWithAuth.get_instance()
        players = room_service.get_players_in_room(room_id)
        return players
    except GameError as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )