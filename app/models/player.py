from pydantic import BaseModel
from typing import List, Dict, Optional


class Player(BaseModel):
    """
    Model representing a player in the game.
    """
    player_id: str
    name: str
    cash: int
    properties: List[str] = []  # List of property_ids
    position: int = 0  # Current position on the board
    stocks: Dict[str, int] = {}  # Stock symbol to quantity
    is_bankrupt: bool = False
    is_in_jail: bool = False
    jail_turns: int = 0
    get_out_of_jail_cards: int = 0