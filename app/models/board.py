from pydantic import BaseModel
from typing import List, Dict, Union, Optional
from enum import Enum


class SpaceType(str, Enum):
    PROPERTY = "property"
    CHANCE = "chance"
    COMMUNITY_CHEST = "community_chest"
    TAX = "tax"
    GO = "go"
    JAIL = "jail"
    FREE_PARKING = "free_parking"
    GO_TO_JAIL = "go_to_jail"
    UTILITY = "utility"
    RAILROAD = "railroad"


class BoardSpace(BaseModel):
    """
    Model representing a space on the board.
    """
    space_id: int
    name: str
    type: SpaceType
    property_id: Optional[str] = None  # Only for property, utility, railroad types


class Board(BaseModel):
    """
    Model representing the game board.
    """
    spaces: List[BoardSpace]
    properties: Dict[str, str]  # Property ID to Property Name mapping