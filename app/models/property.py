from pydantic import BaseModel
from typing import List, Optional


class Property(BaseModel):
    """
    Model representing a property in the game.
    """
    property_id: str
    name: str
    color_set: str
    buy_price: int
    mortgage_price: int
    house_build_price: int
    rent_no_house: int
    rent_one_house: int
    rent_two_houses: int
    rent_three_houses: int
    rent_four_houses: int
    rent_hotel: int
    owner: Optional[str] = None
    houses: int = 0
    is_mortgaged: bool = False


class ColorSet(BaseModel):
    """
    Model representing a color set of properties.
    """
    color: str
    properties: List[str]  # List of property_ids