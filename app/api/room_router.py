"""
API routes for room management.
"""
from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional, Dict
from pydantic import BaseModel

from app.services.room_service import RoomService
from app.models.room import Room, RoomStatus
from app.models.game import GameConfig
from app.models.player import Player


router = APIRouter()


class CreateRoomRequest(BaseModel):
    room_name: str
    host_player_name: str
    even_build: Optional[bool] = True
    starting_cash: Optional[int] = 1500
    max_players: Optional[int] = 4


class JoinRoomRequest(BaseModel):
    player_name: str


@router.post("/rooms", response_model=Dict)
async def create_room(request: CreateRoomRequest):
    """
    Create a new room with a host player.
    """
    room_service = RoomService.get_instance()
    config = GameConfig(
        even_build=request.even_build,
        starting_cash=request.starting_cash,
        max_players=request.max_players
    )
    result = room_service.create_room(request.room_name, request.host_player_name, config)
    return result


@router.get("/rooms", response_model=List[Room])
async def list_rooms(status: Optional[str] = None):
    """
    List all rooms, optionally filtered by status.
    """
    room_service = RoomService.get_instance()
    room_status = None
    if status is not None:
        try:
            room_status = RoomStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    return room_service.list_rooms(room_status)


@router.get("/rooms/{room_id}", response_model=Room)
async def get_room(room_id: str):
    """
    Get a room by ID.
    """
    room_service = RoomService.get_instance()
    room = room_service.get_room(room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.post("/rooms/{room_id}/join", response_model=Player)
async def join_room(room_id: str, request: JoinRoomRequest):
    """
    Join a room.
    """
    room_service = RoomService.get_instance()
    player = room_service.join_room(room_id, request.player_name)
    if player is None:
        raise HTTPException(status_code=400, detail="Could not join room")
    return player


@router.post("/rooms/{room_id}/start")
async def start_game(room_id: str):
    """
    Start a game in the room.
    """
    room_service = RoomService.get_instance()
    success = room_service.start_game(room_id)
    if not success:
        raise HTTPException(status_code=400, detail="Could not start game")
    return {"status": "started"}


@router.post("/rooms/{room_id}/end-turn")
async def end_turn(room_id: str):
    """
    End the current player's turn.
    """
    room_service = RoomService.get_instance()
    success = room_service.end_turn(room_id)
    if not success:
        raise HTTPException(status_code=400, detail="Could not end turn")
    return {"status": "turn ended"}


@router.get("/rooms/{room_id}/players", response_model=List[Player])
async def get_players(room_id: str):
    """
    Get all players in a room.
    """
    room_service = RoomService.get_instance()
    room = room_service.get_room(room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    
    players = room_service.get_players_in_room(room_id)
    return players