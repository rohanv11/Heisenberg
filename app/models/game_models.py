from pydantic import BaseModel, Field, RootModel, validator, model_validator
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


# class SpaceType(str, Enum):
#     PROPERTY = "property"
#     CHANCE = "chance"
#     COMMUNITY_CHEST = "community_chest"
#     TAX = "tax"
#     GO = "go"
#     JAIL = "jail"
#     FREE_PARKING = "free_parking"
#     GO_TO_JAIL = "go_to_jail"
#     UTILITY = "utility"
#     RAILROAD = "railroad"


# class BoardSpace(BaseModel):
#     """
#     Model representing a space on the board.
#     """
#     space_id: int
#     name: str
#     type: SpaceType
#     property_id: Optional[str] = None  # Only for property, utility, railroad types


# class Board(BaseModel):
#     """
#     Model representing the game board.
#     """
#     spaces: List[BoardSpace]
#     properties: Dict[str, str]  # Property ID to Property Name mapping


class GameStatus(str, Enum):
    WAITING = "waiting"  # Waiting for players to join
    STARTED = "started"  # Game has started
    FINISHED = "finished"  # Game has finished

class BoardCountry(str, Enum):
    US = "US"
    IN = "IN"

class GameConfig(BaseModel):
    """
    Configuration for a game.
    """
    house_even_build: bool = True  # Even build or random build
    starting_cash: int = 1500
    max_players: int = 4
    board_country: BoardCountry = BoardCountry.IN
    stock_market_enabled: bool = True
    stakes_enabled: bool = True


class RoomStatus(str, Enum):
    WAITING = "waiting"  # Waiting for players to join
    PLAYING = "playing"  # Game is in progress
    FINISHED = "finished"  # Game has finished


class Player(BaseModel):
    """
    Model representing a player in the game.
    """
    player_id: str
    name: str
    cash: int
    properties: List[str] = []  # List of property_ids
    position: int = 0  # Current position on the board
    stocks: Dict[str, int] = {}  # Stock id to quantity
    is_bankrupt: bool = False
    is_in_jail: bool = False
    jail_turns: int = 0
    get_out_of_jail_cards: int = 0


class BoardSpaceData(BaseModel):
    """
    Model representing a space on the board.
    """
    name: str
    type: str
    pos: int
    financials: Optional[Dict[str, Any]] = None
    owned_by: Optional[Dict[str, Any]] = None
    building_rights: Optional[str] = None
    builds: Optional[int] = 0
    income_earned: Optional[int] = 0
    set_complete: Optional[bool] = False

class BoardData(RootModel):
    """
    Model representing the board data for a country.
    """
    root: Dict[int, BoardSpaceData]

class Room(BaseModel):
    """
    Model representing a game room.
    """
    room_id: str
    status: RoomStatus = RoomStatus.WAITING
    config: GameConfig
    players: List[Player] = []  # List of Player objects
    host_player_id: Optional[str] = None  # The player ID who created the room
    created_at: str  # ISO format datetime
    updated_at: str  # ISO format datetime
    # Board is the source of truth for game state
    board_data: Optional[BoardData] = None  # Use BoardData class

    @model_validator(mode='after')
    def load_board_data(cls, values):
        from app.services.board_service import BoardService
        board_country = values.config.board_country
        values.board_data = BoardService.get_board(board_country)
        return values