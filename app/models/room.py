from pydantic import BaseModel
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime

from app.models.game import GameConfig


class RoomStatus(str, Enum):
    WAITING = "waiting"  # Waiting for players to join
    PLAYING = "playing"  # Game is in progress
    FINISHED = "finished"  # Game has finished


class Room(BaseModel):
    """
    Model representing a game room.
    """
    room_id: str
    name: str
    status: RoomStatus = RoomStatus.WAITING
    config: GameConfig
    players: List[str] = []  # List of player_ids
    host_player_id: Optional[str] = None  # The player who created the room
    current_turn_player_id: Optional[str] = None  # player_id of current turn
    turn_number: int = 0
    created_at: str  # ISO format datetime
    updated_at: str  # ISO format datetime
    max_players: int = 4
    
    # Game state will be stored here when the game starts
    game_state: Optional[Dict] = None