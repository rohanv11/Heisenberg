from pydantic import BaseModel
from typing import List, Dict, Optional
from enum import Enum


class GameStatus(str, Enum):
    WAITING = "waiting"  # Waiting for players to join
    STARTED = "started"  # Game has started
    FINISHED = "finished"  # Game has finished


class GameConfig(BaseModel):
    """
    Configuration for a game.
    """
    even_build: bool = True  # Even build or random build
    starting_cash: int = 1500
    max_players: int = 4


class Game(BaseModel):
    """
    Model representing a game.
    """
    game_id: str
    name: str
    status: GameStatus = GameStatus.WAITING
    config: GameConfig
    players: List[str] = []  # List of player_ids
    current_turn: Optional[str] = None  # player_id of current turn
    turn_number: int = 0
    created_at: str  # ISO format datetime
    updated_at: str  # ISO format datetime