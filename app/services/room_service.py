"""
Service for managing game rooms.
"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from app.models.room import Room, RoomStatus
from app.models.game import GameConfig
from app.models.player import Player
from app.config import game_config


class RoomService:
    """
    Service for managing game rooms.
    Implemented as a singleton.
    """
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """
        Get the singleton instance of RoomService.
        """
        if cls._instance is None:
            cls._instance = RoomService()
        return cls._instance
    
    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.players: Dict[str, Player] = {}
    
    def create_room(self, name: str, host_player_name: str, config: Optional[GameConfig] = None) -> Dict:
        """
        Create a new room with a host player.
        """
        if config is None:
            config = GameConfig()
        
        room_id = str(uuid.uuid4())
        host_player_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        # Create host player
        host_player = Player(
            player_id=host_player_id,
            name=host_player_name,
            cash=config.starting_cash
        )
        
        # Create room
        room = Room(
            room_id=room_id,
            name=name,
            config=config,
            host_player_id=host_player_id,
            players=[host_player_id],
            created_at=now,
            updated_at=now,
            max_players=config.max_players
        )
        
        # Store in memory
        self.players[host_player_id] = host_player
        self.rooms[room_id] = room
        
        return {
            "room": room,
            "player": host_player
        }
    
    def get_room(self, room_id: str) -> Optional[Room]:
        """
        Get a room by ID.
        """
        return self.rooms.get(room_id)
    
    def list_rooms(self, status: Optional[RoomStatus] = None) -> List[Room]:
        """
        List all rooms, optionally filtered by status.
        """
        if status is None:
            return list(self.rooms.values())
        return [room for room in self.rooms.values() if room.status == status]
    
    def join_room(self, room_id: str, player_name: str) -> Optional[Player]:
        """
        Add a player to a room.
        """
        room = self.get_room(room_id)
        if room is None or room.status != RoomStatus.WAITING:
            return None
        
        if len(room.players) >= room.max_players:
            return None
        
        player_id = str(uuid.uuid4())
        player = Player(
            player_id=player_id,
            name=player_name,
            cash=room.config.starting_cash
        )
        
        self.players[player_id] = player
        room.players.append(player_id)
        room.updated_at = datetime.now().isoformat()
        
        return player
    
    def start_game(self, room_id: str) -> bool:
        """
        Start a game in the room.
        """
        room = self.get_room(room_id)
        if room is None or room.status != RoomStatus.WAITING:
            return False
        
        if len(room.players) < 2:  # At least 2 players required
            return False
        
        # Initialize game state
        room.status = RoomStatus.PLAYING
        room.current_turn_player_id = room.players[0]  # First player's turn
        room.updated_at = datetime.now().isoformat()
        
        # Create initial game state
        board = game_config.create_board()
        properties = game_config.create_properties()
        stocks = game_config.create_stocks()
        
        room.game_state = {
            "board": board.dict(),
            "properties": {k: v.dict() for k, v in properties.items()},
            "stocks": {k: v.dict() for k, v in stocks.items()},
            "dice_history": []
        }
        
        return True
    
    def end_turn(self, room_id: str) -> bool:
        """
        End the current player's turn and move to the next player.
        """
        room = self.get_room(room_id)
        if room is None or room.status != RoomStatus.PLAYING:
            return False
        
        current_index = room.players.index(room.current_turn_player_id)
        next_index = (current_index + 1) % len(room.players)
        
        room.current_turn_player_id = room.players[next_index]
        room.turn_number += 1
        room.updated_at = datetime.now().isoformat()
        
        return True
    
    def get_player(self, player_id: str) -> Optional[Player]:
        """
        Get a player by ID.
        """
        return self.players.get(player_id)
    
    def get_players_in_room(self, room_id: str) -> List[Player]:
        """
        Get all players in a room.
        """
        room = self.get_room(room_id)
        if room is None:
            return []
        
        return [self.players.get(player_id) for player_id in room.players]