"""
API routes for room management.
"""
from fastapi import APIRouter, HTTPException, Body, Depends, status
from typing import List, Optional, Dict
from pydantic import BaseModel
import logging
import uuid
import random

from app.services.room_service import RoomServiceWithAuth
from app.models.game_models import Room, RoomStatus, GameConfig, BoardData
# from app.models.game import GameConfig
from app.models.player import Player
from app.models.user import UserInDB
from app.models.exceptions import GameError
from app.api.dependencies import get_current_user
from app.utils.exception_handlers import handle_exceptions
from app.services.board_service import BoardService
from app.services.centrifugo_service import CentrifugoService


router = APIRouter()
logger = logging.getLogger(__name__)


class CreateRoomRequest(BaseModel):
    room_name: str
    even_build: Optional[bool] = True
    starting_cash: Optional[int] = 1500
    max_players: Optional[int] = 4


@router.post("/rooms", response_model=Room)
async def create_room():
    """
    Create a new room with default settings.
    """
    try:
        # Generate a 6-digit numeric room ID
        room_id = str(random.randint(100000, 999999))
        
        # Create room with default configuration
        room = Room(
            room_id=room_id,
            config=GameConfig()
        )
        
        # Connect the creator to the room using Centrifugo
        CentrifugoService.connect_user_to_room(room_id)
        
        return room
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rooms", response_model=List[Room])
@handle_exceptions
async def list_rooms(
    status: Optional[str] = None,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    List all rooms, optionally filtered by status.
    """
    room_service = RoomServiceWithAuth.get_instance()
    room_status = None
    if status is not None:
        try:
            room_status = RoomStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Invalid status: {status}. Valid statuses are: {[s.value for s in RoomStatus]}"
            )
    
    return room_service.list_rooms(room_status)


@router.get("/rooms/{room_id}", response_model=Room)
@handle_exceptions
async def get_room(
    room_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get a room by ID.
    """
    if not room_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room ID is required"
        )
        
    room_service = RoomServiceWithAuth.get_instance()
    return room_service.get_room(room_id)


@router.post("/rooms/{room_id}/join", response_model=Player)
@handle_exceptions
async def join_room(
    room_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Join a room using the authenticated user.
    """
    if not room_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room ID is required"
        )
        
    room_service = RoomServiceWithAuth.get_instance()
    player = await room_service.join_room(room_id, current_user)
    return player


@router.post("/rooms/{room_id}/start")
@handle_exceptions
async def start_game(
    room_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Start a game in the room. Only the host can start the game.
    """
    if not room_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room ID is required"
        )
        
    room_service = RoomServiceWithAuth.get_instance()
    success = await room_service.start_game(room_id, current_user)
    return {"status": "started"}


@router.post("/rooms/{room_id}/end-turn")
@handle_exceptions
async def end_turn(
    room_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    End the current player's turn. Only the current player can end their turn.
    """
    if not room_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room ID is required"
        )
        
    room_service = RoomServiceWithAuth.get_instance()
    success = await room_service.end_turn(room_id, current_user)
    return {"status": "turn ended"}


@router.get("/rooms/{room_id}/players", response_model=List[Player])
@handle_exceptions
async def get_players(
    room_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get all players in a room.
    """
    if not room_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room ID is required"
        )
        
    room_service = RoomServiceWithAuth.get_instance()
    players = room_service.get_players_in_room(room_id)
    return players