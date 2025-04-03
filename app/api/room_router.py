"""
API routes for room management.
"""
from fastapi import APIRouter, HTTPException, Body, Depends, status
from typing import List, Optional, Dict
from pydantic import BaseModel
import logging
import uuid
import random
from datetime import datetime
from app.events import socket_manager

from app.services.room_service import RoomServiceWithAuth
from app.models.game_models import Room, RoomStatus, GameConfig, Player, BoardCountry
from app.models.user import UserInDB
from app.models.exceptions import GameError
from app.api.dependencies import get_current_user
from app.utils.exception_handlers import handle_exceptions


router = APIRouter()
logger = logging.getLogger(__name__)


class CreateRoomRequest(BaseModel):
    """Request model for room creation via API."""
    player_name: str
    board_country: str = "IN"
    max_players: int = 4
    starting_cash: int = 1500
    house_even_build: bool = True
    stock_market_enabled: bool = True
    stakes_enabled: bool = True


@router.post("/rooms", response_model=Dict)
@handle_exceptions
async def create_room(
    request: CreateRoomRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Create a new room via API with specified settings.
    """
    try:
        # Generate a 6-digit numeric room ID
        room_id = str(random.randint(100000, 999999))
        
        # Create game config from request
        try:
            board_country = BoardCountry(request.board_country)
        except ValueError:
            board_country = BoardCountry.IN
            
        config = GameConfig(
            board_country=board_country,
            max_players=request.max_players,
            starting_cash=request.starting_cash,
            house_even_build=request.house_even_build,
            stock_market_enabled=request.stock_market_enabled,
            stakes_enabled=request.stakes_enabled
        )
        
        # Create a player with the user's ID
        player = Player(
            player_id=current_user.google_id,
            name=request.player_name or current_user.username,
            cash=config.starting_cash
        )
        
        # Create room with current timestamp
        now = datetime.now().isoformat()
        room = Room(
            room_id=room_id,
            status=RoomStatus.WAITING,
            config=config,
            players=[player],
            host_player_id=current_user.google_id,
            created_at=now,
            updated_at=now
        )
        
        # Store the room in memory (shared with socketio)
        # Import here to avoid circular imports
        from app.events.socket_events import rooms as socketio_rooms
        socketio_rooms[room_id] = room
        
        logger.info(f"Room created via API: {room_id} by user {current_user.google_id}")
        return {
            "room": room.model_dump(),
            "message": f"Room created with ID: {room_id}"
        }
    except Exception as e:
        logger.error(f"Error creating room: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rooms", response_model=List[Room])
@handle_exceptions
async def list_rooms(
    status: Optional[str] = None,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    List all rooms, optionally filtered by status.
    Uses both in-memory rooms and rooms from room service.
    """
    try:
        room_status = None
        if status is not None:
            try:
                room_status = RoomStatus(status)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=f"Invalid status: {status}. Valid statuses are: {[s.value for s in RoomStatus]}"
                )
        
        # Get rooms from socket.io in-memory storage
        # Import here to avoid circular imports
        from app.events.socket_events import rooms as socketio_rooms
        socketio_room_list = list(socketio_rooms.values())
        if room_status:
            socketio_room_list = [room for room in socketio_room_list if room.status == room_status]
        
        # Get rooms from room service (database)
        try:
            room_service = RoomServiceWithAuth.get_instance()
            db_rooms = room_service.list_rooms(room_status)
            
            # Combine and deduplicate rooms by room_id
            all_rooms = {room.room_id: room for room in (socketio_room_list + db_rooms)}
            return list(all_rooms.values())
        except Exception:
            # If database access fails, just return in-memory rooms
            logger.warning("Failed to get rooms from database, returning in-memory rooms only")
            return socketio_room_list
            
    except Exception as e:
        logger.error(f"Error listing rooms: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rooms/{room_id}", response_model=Room)
@handle_exceptions
async def get_room(
    room_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get a room by ID. Checks both in-memory and database.
    """
    if not room_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room ID is required"
        )
    
    # First check in-memory rooms
    # Import here to avoid circular imports
    from app.events.socket_events import rooms as socketio_rooms
    if room_id in socketio_rooms:
        return socketio_rooms[room_id]
    
    # If not found, check in database
    try:
        room_service = RoomServiceWithAuth.get_instance()
        return room_service.get_room(room_id)
    except Exception as e:
        logger.error(f"Error getting room: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Room {room_id} not found")


@router.post("/rooms/{room_id}/join")
@handle_exceptions
async def join_room_api(
    room_id: str,
    player_name: str = Body(..., embed=True),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Join a room via API.
    """
    if not room_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room ID is required"
        )
    
    # First check in-memory rooms
    # Import here to avoid circular imports
    from app.events.socket_events import rooms as socketio_rooms
    if room_id in socketio_rooms:
        room = socketio_rooms[room_id]
        
        # Check if the room is waiting for players
        if room.status != RoomStatus.WAITING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Game has already started"
            )
        
        # Check if the room is full
        if len(room.players) >= room.config.max_players:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Room is full"
            )
        
        # Check if player is already in the room
        if any(player.player_id == current_user.google_id for player in room.players):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already in this room"
            )
        
        # Create a new player with cash from room config
        player = Player(
            player_id=current_user.google_id,
            name=player_name or current_user.username,
            cash=room.config.starting_cash
        )
        
        # Add player to the room
        room.players.append(player)
        
        # Update timestamp
        room.updated_at = datetime.now().isoformat()
        
        # Notify all clients in the room about the new player
        await socket_manager.sio.emit('player_joined', {
            'player': player.model_dump(),
            'message': f'{player.name} joined the room'
        }, room=room_id)
        
        logger.info(f"Player {current_user.google_id} joined room {room_id} via API")
        return {
            "room": room.model_dump(),
            "message": f"You joined room {room_id}"
        }
    
    # If not in memory, try to join via room service
    try:
        room_service = RoomServiceWithAuth.get_instance()
        player = await room_service.join_room(room_id, current_user)
        
        return {
            "room": room_service.get_room(room_id).model_dump(),
            "message": f"You joined room {room_id}"
        }
    except Exception as e:
        logger.error(f"Error joining room: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Room {room_id} not found or could not be joined")


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
    
    # First check in-memory rooms
    # Import here to avoid circular imports
    from app.events.socket_events import rooms as socketio_rooms
    if room_id in socketio_rooms:
        room = socketio_rooms[room_id]
        
        # Check if player is the host
        if room.host_player_id != current_user.google_id:
            raise HTTPException(
                status_code=status.HTTP_FORBIDDEN,
                detail="Only the host can start the game"
            )
        
        # Check if enough players
        if len(room.players) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Need at least 2 players to start"
            )
        
        # Check if game already started
        if room.status != RoomStatus.WAITING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Game has already started"
            )
        
        # Update room status
        room.status = RoomStatus.PLAYING
        room.updated_at = datetime.now().isoformat()
        
        # Notify everyone in the room via socket.io
        await socket_manager.sio.emit('game_started', {
            'room': room.model_dump(),
            'message': 'Game has started!'
        }, room=room_id)
        
        logger.info(f"Game started in room {room_id} via API")
        return {"status": "started"}
    
    # If not in memory, start via room service
    try:
        room_service = RoomServiceWithAuth.get_instance()
        success = await room_service.start_game(room_id, current_user)
        return {"status": "started"}
    except Exception as e:
        logger.error(f"Error starting game: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Room {room_id} not found or could not be started")


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
    
    # First check in-memory rooms
    # Import here to avoid circular imports
    from app.events.socket_events import rooms as socketio_rooms
    if room_id in socketio_rooms:
        room = socketio_rooms[room_id]
        return room.players
    
    # If not in memory, get from room service
    try:
        room_service = RoomServiceWithAuth.get_instance()
        return room_service.get_players_in_room(room_id)
    except Exception as e:
        logger.error(f"Error getting players: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Room {room_id} not found")