from pydantic import BaseModel, Field, RootModel, validator, root_validator
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime
from app.services.board_service import BoardService


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
    US = "us"
    IN = "in"

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


class BoardSpaceData(BaseModel):
    """
    Model representing a space on the board.
    """
    name: str
    type: str
    players_here: List[str]
    pos: int
    financials: Optional[Dict] = None
    owned_by: Optional[Dict] = None
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
    players: List[str] = []  # List of player_ids
    host_player_id: Optional[str] = None  # The player who created the room
    # current_turn_player_id: Optional[str] = None  # player_id of current turn 
    # this is a Board property not a rtoom property, (current_turn_player_id)
    # turn_number: int = 0
    created_at: str  # ISO format datetime
    updated_at: str  # ISO format datetime
    # Game state will be stored here when the game starts

    # this is post load
    board_data: Optional[BoardData] = None  # Use BoardData class

    @root_validator()
    def load_board_data(cls, values):
        board_country = values.get('config', {}).get('board_country', 'IN')
        values['board_data'] = BoardService.get_board(board_country)
        return values