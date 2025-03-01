"""
Configuration for game elements like properties, board layout, etc.
"""
from app.models.property import Property, ColorSet
from app.models.board import BoardSpace, SpaceType, Board
from app.models.stock import Stock, StockType
from typing import Dict, List

# Define property sets by color
COLOR_SETS = {
    "brown": ["old_kent_road", "whitechapel_road"],
    "blue": ["mumbai", "delhi"],
    "green": ["agra", "lucknow", "kanpur"],
    "red": ["jaipur", "pune", "goa"],
    "yellow": ["chennai", "bangalore", "hyderabad"],
    "orange": ["kolkata", "ahmedabad", "surat"],
    "purple": ["chandigarh", "indore", "nagpur"],
    "pink": ["kochi", "varanasi", "madurai"],
}

# Define properties
PROPERTIES = {
    # Brown set
    "old_kent_road": {
        "name": "Old Kent Road",
        "color_set": "brown",
        "buy_price": 60,
        "mortgage_price": 30,
        "house_build_price": 50,
        "rent_no_house": 2,
        "rent_one_house": 10,
        "rent_two_houses": 30,
        "rent_three_houses": 90,
        "rent_four_houses": 160,
        "rent_hotel": 250,
    },
    "whitechapel_road": {
        "name": "Whitechapel Road",
        "color_set": "brown",
        "buy_price": 60,
        "mortgage_price": 30,
        "house_build_price": 50,
        "rent_no_house": 4,
        "rent_one_house": 20,
        "rent_two_houses": 60,
        "rent_three_houses": 180,
        "rent_four_houses": 320,
        "rent_hotel": 450,
    },
    
    # Blue set (Indian cities)
    "mumbai": {
        "name": "Mumbai",
        "color_set": "blue",
        "buy_price": 400,
        "mortgage_price": 200,
        "house_build_price": 200,
        "rent_no_house": 50,
        "rent_one_house": 200,
        "rent_two_houses": 600,
        "rent_three_houses": 1400,
        "rent_four_houses": 1700,
        "rent_hotel": 2000,
    },
    "delhi": {
        "name": "Delhi",
        "color_set": "blue",
        "buy_price": 350,
        "mortgage_price": 175,
        "house_build_price": 200,
        "rent_no_house": 35,
        "rent_one_house": 175,
        "rent_two_houses": 500,
        "rent_three_houses": 1100,
        "rent_four_houses": 1300,
        "rent_hotel": 1500,
    },
    
    # Add more properties for other sets...
}

# Define initial stocks
INITIAL_STOCKS = {
    "AAPL": {
        "name": "Apple Inc.",
        "type": StockType.COMPANY,
        "current_price": 150.0,
        "previous_price": 148.0,
    },
    "GOOG": {
        "name": "Alphabet Inc.",
        "type": StockType.COMPANY,
        "current_price": 2800.0,
        "previous_price": 2750.0,
    },
    "MSFT": {
        "name": "Microsoft Corporation",
        "type": StockType.COMPANY,
        "current_price": 340.0,
        "previous_price": 335.0,
    },
    "AMZN": {
        "name": "Amazon.com Inc.",
        "type": StockType.COMPANY,
        "current_price": 3300.0,
        "previous_price": 3250.0,
    },
}

# Define board layout
BOARD_LAYOUT = [
    {"space_id": 0, "name": "GO", "type": SpaceType.GO},
    {"space_id": 1, "name": "Old Kent Road", "type": SpaceType.PROPERTY, "property_id": "old_kent_road"},
    {"space_id": 2, "name": "Community Chest", "type": SpaceType.COMMUNITY_CHEST},
    {"space_id": 3, "name": "Whitechapel Road", "type": SpaceType.PROPERTY, "property_id": "whitechapel_road"},
    {"space_id": 4, "name": "Income Tax", "type": SpaceType.TAX},
    {"space_id": 5, "name": "Kings Cross Station", "type": SpaceType.RAILROAD},
    {"space_id": 6, "name": "Mumbai", "type": SpaceType.PROPERTY, "property_id": "mumbai"},
    {"space_id": 7, "name": "Chance", "type": SpaceType.CHANCE},
    {"space_id": 8, "name": "Delhi", "type": SpaceType.PROPERTY, "property_id": "delhi"},
    {"space_id": 9, "name": "Jail", "type": SpaceType.JAIL},
    # Add more spaces to complete the board...
]


def create_properties() -> Dict[str, Property]:
    """
    Create Property objects from the configuration.
    """
    properties = {}
    for property_id, property_data in PROPERTIES.items():
        properties[property_id] = Property(
            property_id=property_id,
            **property_data
        )
    return properties


def create_color_sets() -> Dict[str, ColorSet]:
    """
    Create ColorSet objects from the configuration.
    """
    color_sets = {}
    for color, property_ids in COLOR_SETS.items():
        color_sets[color] = ColorSet(
            color=color,
            properties=property_ids
        )
    return color_sets


def create_board() -> Board:
    """
    Create a Board object from the configuration.
    """
    spaces = [BoardSpace(**space) for space in BOARD_LAYOUT]
    properties = {prop_id: PROPERTIES[prop_id]["name"] for prop_id in PROPERTIES}
    
    return Board(
        spaces=spaces,
        properties=properties
    )


def create_stocks() -> Dict[str, Stock]:
    """
    Create Stock objects from the configuration.
    """
    stocks = {}
    for symbol, stock_data in INITIAL_STOCKS.items():
        stocks[symbol] = Stock(
            symbol=symbol,
            **stock_data
        )
    return stocks