from pydantic import BaseModel
from typing import List, Dict, Optional
from enum import Enum


class StockType(str, Enum):
    COMPANY = "company"  # Regular company stock
    PROPERTY = "property"  # Property listing on the stock market


class Stock(BaseModel):
    """
    Model representing a stock in the stock market.
    """
    symbol: str
    name: str
    type: StockType
    current_price: float
    previous_price: float
    property_id: Optional[str] = None  # Only for property stocks
    owner: Optional[str] = None  # Owner player_id for property stocks


class StockMarket(BaseModel):
    """
    Model representing the stock market.
    """
    stocks: Dict[str, Stock]  # Symbol to Stock mapping
    history: Dict[str, List[float]]  # Symbol to price history