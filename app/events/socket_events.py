import logging
import random
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Callable, Awaitable, Optional, Tuple, Union
from functools import wraps

from app.main import sio  # Import the sio instance from main.py
from app.models.game_models import Room, RoomStatus, GameConfig, BoardCountry, Player

logger = logging.getLogger(__name__)

# In-memory storage for rooms
rooms: Dict[str, Room] = {}

# ----------------------------------------------------------------------
# Event Emission Manager - For atomic multi-emit operations
# ----------------------------------------------------------------------

class EventEmissionManager:
    """
    Manages atomic emission of multiple socket.io events.
    All emissions are collected and only sent if no errors occur.
    """
    def __init__(self):
        self.emissions: List[Tuple[str, Any, Optional[str]]] = []
        self.error_occurred = False
        
    def add_emission(self, event: str, data: Any, room: Optional[str] = None):
        """Add an emission to the transaction."""
        self.emissions.append((event, data, room))
        
    async def emit_all(self):
        """Emit all collected events."""
        try:
            for event, data, room in self.emissions:
                await sio.emit(event, data, room=room)
            return True
        except Exception as e:
            logger.error(f"Error during atomic emit: {str(e)}")
            self.error_occurred = True
            return False
            
    def __bool__(self):
        """Returns False if an error occurred during emission."""
        return not self.error_occurred


# ----------------------------------------------------------------------
# Decorator for atomic event handling and roomwide operations
# ----------------------------------------------------------------------

def atomic_event_handler(func: Callable) -> Callable:
    """
    Decorator to ensure atomic event handling for socket.io events.
    If an exception occurs, proper error handling is done and client is notified.
    """
    @wraps(func)
    async def wrapper(sid: str, data: Any = None):
        emissions = EventEmissionManager()
        
        try:
            # Run the event handler with the emission manager
            result = await func(sid, data, emissions)
            
            # Emit all collected events
            await emissions.emit_all()
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            # Emit error to client
            await sio.emit('error', {'message': f'Operation failed: {str(e)}'}, room=sid)
            return None
            
    return wrapper


# ----------------------------------------------------------------------
# Socket.IO Event Handlers
# ----------------------------------------------------------------------

@sio.on('connect')
async def connect(sid, environ):
    """Handle client connection."""
    logger.info(f"Client connected: {sid}")
    await sio.emit('connection_success', {'message': 'Successfully connected to game server'}, room=sid)

@sio.on('disconnect')
@atomic_event_handler
async def disconnect(sid, _=None, emissions=None):
    """Handle client disconnection with atomic operations."""
    logger.info(f"Client disconnected: {sid}")
    
    # Find rooms where this player is and handle their departure
    for room_id, room in list(rooms.items()):
        for player in list(room.players):
            if player.player_id == sid:
                # Remove player from room
                room.players = [p for p in room.players if p.player_id != sid]
                
                # No need to update board spaces anymore
                # Player position is tracked in the Player object itself
                
                # Prepare emissions (will be sent atomically)
                emissions.add_emission('player_left', {'player_id': sid}, room=room_id)
                
                # If room is empty, remove it
                if not room.players:
                    del rooms[room_id]
                    logger.info(f"Room {room_id} removed (empty)")
                # If host left, assign a new host
                elif room.host_player_id == sid and room.players:
                    room.host_player_id = room.players[0].player_id
                    emissions.add_emission('host_changed', {
                        'new_host_id': room.host_player_id
                    }, room=room_id)
                
                # Update timestamp
                room.updated_at = datetime.now().isoformat()
                break

@sio.on('create_room')
@atomic_event_handler
async def create_room(sid, data=None, emissions=None):
    """
    Handle room creation with default settings.
    - Default IN board
    - Max players: 4
    - Default game configuration
    """
    if not data:
        data = {}
        
    # Use player name from data if provided, otherwise use generic name
    player_name = data.get('player_name', f"Player_{sid[:6]}")
    
    # Generate a 6-digit numeric room ID
    room_id = str(random.randint(100000, 999999))
    
    # Create default game config
    config = GameConfig(
        board_country=BoardCountry.IN,
        max_players=4
    )
    
    # Create a player with cash from config
    player = Player(
        player_id=sid,
        name=player_name,
        cash=config.starting_cash
    )
    
    # Create room with current timestamp
    now = datetime.now().isoformat()
    room = Room(
        room_id=room_id,
        status=RoomStatus.WAITING,
        config=config,
        players=[player],
        host_player_id=sid,
        created_at=now,
        updated_at=now
    )
    
    # Player's initial position is already set to 0 in the Player model
    
    # Store the room in memory
    rooms[room_id] = room
    
    # Join socket room
    sio.enter_room(sid, room_id)
    
    # Prepare room data emission (will be sent atomically)
    room_data = room.model_dump()
    emissions.add_emission('room_created', {
        'room': room_data,
        'message': f'Room created with ID: {room_id}'
    }, room=sid)
    
    logger.info(f"Room created: {room_id} by player {sid}")
    return {'room_id': room_id}

@sio.on('join_room')
@atomic_event_handler
async def join_room(sid, data, emissions=None):
    """
    Handle a player joining a room with atomic operations.
    """
    room_id = data.get('room_id')
    player_name = data.get('player_name', f"Player_{sid[:6]}")
    
    if not room_id:
        raise ValueError('Room ID is required')
    
    if room_id not in rooms:
        raise ValueError('Room not found')
    
    room = rooms[room_id]
    
    # Check if the room is waiting for players
    if room.status != RoomStatus.WAITING:
        raise ValueError('Game has already started')
    
    # Check if the room is full
    if len(room.players) >= room.config.max_players:
        raise ValueError('Room is full')
    
    # Check if player is already in the room
    if any(player.player_id == sid for player in room.players):
        raise ValueError('You are already in this room')
    
    # Create a new player with cash from room config
    player = Player(
        player_id=sid,
        name=player_name,
        cash=room.config.starting_cash
    )
    
    # Add player to the room
    room.players.append(player)
    
    # Player's initial position is already set to 0 in the Player model
    
    # Update timestamp
    room.updated_at = datetime.now().isoformat()
    
    # Join socket room
    sio.enter_room(sid, room_id)
    
    # Prepare emissions (will be sent atomically)
    emissions.add_emission('player_joined', {
        'player': player.model_dump(),
        'message': f'{player_name} joined the room'
    }, room=room_id)
    
    emissions.add_emission('room_joined', {
        'room': room.model_dump(),
        'message': f'You joined room {room_id}'
    }, room=sid)
    
    logger.info(f"Player {sid} joined room {room_id}")

@sio.on('leave_room')
@atomic_event_handler
async def leave_room(sid, data, emissions=None):
    """
    Handle a player leaving a room with atomic operations.
    """
    room_id = data.get('room_id')
    
    if not room_id or room_id not in rooms:
        raise ValueError('Room not found')
    
    room = rooms[room_id]
    
    # Check if player is in the room
    player_index = None
    player_name = "Unknown player"
    
    for i, player in enumerate(room.players):
        if player.player_id == sid:
            player_index = i
            player_name = player.name
            break
            
    if player_index is None:
        raise ValueError('You are not in this room')
    
    # Remove player from the room
    room.players.pop(player_index)
    
    # No need to update board spaces anymore
    # Player position is tracked in the Player object itself
    
    # Leave socket room
    sio.leave_room(sid, room_id)
    
    # If room is empty, remove it
    if not room.players:
        del rooms[room_id]
        logger.info(f"Room {room_id} removed (empty)")
        emissions.add_emission('room_left', {'message': f'You left room {room_id}'}, room=sid)
        return
    
    # If this was the host, assign a new host
    if room.host_player_id == sid:
        room.host_player_id = room.players[0].player_id
        emissions.add_emission('host_changed', {
            'new_host_id': room.host_player_id,
            'new_host_name': room.players[0].name
        }, room=room_id)
    
    # Update room timestamp
    room.updated_at = datetime.now().isoformat()
    
    # Prepare emissions (will be sent atomically)
    emissions.add_emission('player_left', {
        'player_id': sid,
        'player_name': player_name,
        'message': f'{player_name} left the room'
    }, room=room_id)
    
    emissions.add_emission('room_left', {'message': f'You left room {room_id}'}, room=sid)
    
    logger.info(f"Player {sid} left room {room_id}")

@sio.on('start_game')
@atomic_event_handler
async def start_game(sid, data, emissions=None):
    """
    Start the game in a room with atomic operations.
    Only the host can start the game.
    """
    room_id = data.get('room_id')
    
    if not room_id or room_id not in rooms:
        raise ValueError('Room not found')
    
    room = rooms[room_id]
    
    # Check if player is the host
    if room.host_player_id != sid:
        raise ValueError('Only the host can start the game')
    
    # Check if enough players
    if len(room.players) < 2:
        raise ValueError('Need at least 2 players to start')
    
    # Check if game already started
    if room.status != RoomStatus.WAITING:
        raise ValueError('Game has already started')
    
    # Update room status
    room.status = RoomStatus.PLAYING
    room.updated_at = datetime.now().isoformat()
    
    # Prepare emission (will be sent atomically)
    emissions.add_emission('game_started', {
        'room': room.model_dump(),
        'message': 'Game has started!'
    }, room=room_id)
    
    logger.info(f"Game started in room {room_id}")

@sio.on('move_player')
@atomic_event_handler
async def move_player(sid, data, emissions=None):
    """
    Move a player based on dice roll from client.
    """
    room_id = data.get('room_id')
    dice_total = data.get('dice_total')
    
    if not room_id or room_id not in rooms:
        raise ValueError('Room not found')
    
    if not isinstance(dice_total, int) or dice_total < 2 or dice_total > 12:
        raise ValueError('Invalid dice total')
    
    room = rooms[room_id]
    
    # Check if game is in progress
    if room.status != RoomStatus.PLAYING:
        raise ValueError('Game has not started yet')
    
    # Find the player
    player = None
    for p in room.players:
        if p.player_id == sid:
            player = p
            break
    
    if not player:
        raise ValueError('You are not in this room')
    
    # Move player
    old_position = player.position
    # Calculate new position using board length
    board_length = len(room.board_data.root) if room.board_data else 40
    player.position = (player.position + dice_total) % board_length
    
    # Update room timestamp
    room.updated_at = datetime.now().isoformat()
    
    # Prepare emissions
    emissions.add_emission('player_moved', {
        'player_id': sid,
        'player_name': player.name,
        'dice_total': dice_total,
        'old_position': old_position,
        'new_position': player.position
    }, room=room_id)
    
    # Also send the updated room state
    emissions.add_emission('room_updated', {
        'room': room.model_dump()
    }, room=room_id)
    
    logger.info(f"Player {sid} moved {dice_total} spaces in room {room_id}")

