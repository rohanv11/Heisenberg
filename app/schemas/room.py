from pydantic import BaseModel
from typing import Optional
from enum import Enum


class RoomTemplate(str, Enum):
    DEFAULT = "default"
    CLASSIC = "classic"

class RoomType(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"

class Board(str, Enum):
    IN = "in"
    US = "us"
    UK = "uk"

class StartingCash(int, Enum):
    DEFAULT = 2000
    _1500 = 1500
    _2500 = 2500
    _3000 = 3000


class HouseBuild(str, Enum):
    EVEN = "even"
    RANDOM = "random"

class InJail(str, Enum):
    RENT = "rent"
    NO_RENT = "no_rent"

class RoomCreate(BaseModel):
    """
    Schema for creating a new room.
    """
    room_type: RoomType
    board: Board
    room_template: RoomTemplate
    starting_cash: Optional[StartingCash] = StartingCash.DEFAULT
    house_build: Optional[HouseBuild] = HouseBuild.EVEN
    in_jail: Optional[InJail] = InJail.NO_RENT
    community_cards: Optional[bool] = True


    class Config:
        json_schema_extra = {
            "example": {
                "room_type": "public",
                "board": "in",
                "room_template": "default",
                "starting_cash": 2000,
                "house_build": "even",
                "in_jail": "rent",
                "community_cards": True
            }
        }


class RoomFull(RoomCreate):
    room_code: str
    players: set[str] = set() #update this with class Player

