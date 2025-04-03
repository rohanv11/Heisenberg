"""
Service for managing game rooms.
"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Union

from app.models.game_models import Room, RoomStatus, GameConfig, Player
from app.models.user import UserInDB
from app.config import game_config
from app.config.backend import DatabaseManager, USERS_COLLECTION


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


# Collection names for MongoDB
ROOMS_COLLECTION = "rooms"
# PLAYER_GAME_COLLECTION = "player_games" - Will be implemented later

from app.models.exceptions import (
    GameError,
    NotHostError, 
    NotInRoomError, 
    NotYourTurnError, 
    RoomFullError, 
    RoomNotFoundError, 
    GameAlreadyStartedError, 
    NotEnoughPlayersError,
    UserNotFoundError
)


class RoomServiceWithAuth:
    """
    Service for managing game rooms with authentication and MongoDB persistence.
    """
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """
        Get the singleton instance of RoomServiceWithAuth.
        """
        if cls._instance is None:
            cls._instance = RoomServiceWithAuth()
        return cls._instance
    
    def __init__(self):
        # For backward compatibility, we'll still use the in-memory service
        # but extend it with MongoDB persistence
        self.in_memory_service = RoomService.get_instance()
    
    async def create_room(self, name: str, user: UserInDB, config: Optional[GameConfig] = None) -> Dict:
        """
        Create a new room with an authenticated user as host.
        """
        if config is None:
            config = GameConfig()
        
        # First create the room in memory
        room_data = self.in_memory_service.create_room(name, user.username, config)
        room = room_data["room"]
        player = room_data["player"]
        
        # Prepare the operations
        rooms_collection = DatabaseManager.get_collection(ROOMS_COLLECTION)
        users_collection = DatabaseManager.get_collection(USERS_COLLECTION)
        
        # Perform the database operations
        try:
            # Insert room document
            await rooms_collection.insert_one(room.dict())
            
            # Update user's current game details
            await users_collection.update_one(
                {"google_id": user.google_id},
                {"$set": {
                    "current_game_details": {
                        "room_id": room.room_id,
                        "player_id": player.player_id,
                        "is_host": True
                    }
                }}
            )
            
            return room_data
        except Exception as e:
            # If there's an error, we need to clean up the in-memory state
            # to maintain consistency with the database
            if room.room_id in self.in_memory_service.rooms:
                del self.in_memory_service.rooms[room.room_id]
            if player.player_id in self.in_memory_service.players:
                del self.in_memory_service.players[player.player_id]
            raise e
    
    async def join_room(self, room_id: str, user: UserInDB) -> Optional[Player]:
        """
        Add an authenticated user to a room.
        """
        # Check if room exists
        room = self.in_memory_service.get_room(room_id)
        if room is None:
            raise RoomNotFoundError(room_id)
            
        # Check if room is in WAITING status
        if room.status != RoomStatus.WAITING:
            raise GameAlreadyStartedError(room_id)
            
        # Check if room is full
        if len(room.players) >= room.max_players:
            raise RoomFullError(room_id, room.max_players)
        
        # Join room in memory
        player = self.in_memory_service.join_room(room_id, user.username)
        if player is None:
            # This shouldn't happen if our previous checks are thorough
            raise GameError(detail="Failed to join room")
        
        # Prepare the operations
        rooms_collection = DatabaseManager.get_collection(ROOMS_COLLECTION)
        users_collection = DatabaseManager.get_collection(USERS_COLLECTION)
        
        # Perform the database operations
        try:
            # Update user's current game details
            await users_collection.update_one(
                {"google_id": user.google_id},
                {"$set": {
                    "current_game_details": {
                        "room_id": room_id,
                        "player_id": player.player_id,
                        "is_host": False
                    }
                }}
            )
            
            # Update room in MongoDB
            await rooms_collection.update_one(
                {"room_id": room_id},
                {"$set": room.dict()}
            )
            
            return player
        except Exception as e:
            # If there's an error, we need to clean up the in-memory state
            if player.player_id in self.in_memory_service.players:
                del self.in_memory_service.players[player.player_id]
            if room and player.player_id in room.players:
                room.players.remove(player.player_id)
            raise e
    
    async def start_game(self, room_id: str, user: UserInDB) -> bool:
        """
        Start a game in the room, checking that the user is the host.
        Raises appropriate exceptions for error conditions.
        """
        # Check if room exists
        room = self.in_memory_service.get_room(room_id)
        if room is None:
            raise RoomNotFoundError(room_id)
            
        # Get user details
        users_collection = DatabaseManager.get_collection(USERS_COLLECTION)
        user_doc = await users_collection.find_one({"google_id": user.google_id})
        
        if not user_doc:
            raise UserNotFoundError()
            
        # Check if user is in this room and is host
        current_game = user_doc.get("current_game_details", {})
        is_in_room = current_game.get("room_id") == room_id
        is_host = current_game.get("is_host", False)
        
        if not is_in_room:
            raise NotInRoomError(room_id)
            
        if not is_host:
            raise NotHostError(room_id)
            
        # Check room status
        if room.status != RoomStatus.WAITING:
            raise GameAlreadyStartedError(room_id)
            
        # Check minimum players
        if len(room.players) < 2:  # Minimum 2 players required
            raise NotEnoughPlayersError(room_id, len(room.players), 2)
        
        # Store original state for rollback
        original_status = room.status
        original_game_state = room.game_state
        original_current_player = room.current_turn_player_id
        
        # Start game in memory
        result = self.in_memory_service.start_game(room_id)
        if not result:
            # This shouldn't happen if our previous checks are thorough
            raise GameError(detail="Failed to start game")
        
        # Prepare the operations
        rooms_collection = DatabaseManager.get_collection(ROOMS_COLLECTION)
        
        # Perform the database operations
        try:
            # Update room in MongoDB
            await rooms_collection.update_one(
                {"room_id": room_id},
                {"$set": room.dict()}
            )
            
            # Increment the host's games_played count
            await users_collection.update_one(
                {"google_id": user.google_id},
                {"$inc": {"games_played": 1}}
            )
            
            return True
        except Exception as e:
            # If there's an error, revert the in-memory state
            room.status = original_status
            room.game_state = original_game_state
            room.current_turn_player_id = original_current_player
            raise e
    
    def get_room(self, room_id: str) -> Room:
        """
        Get a room by ID using in-memory service.
        Raises RoomNotFoundError if the room doesn't exist.
        """
        room = self.in_memory_service.get_room(room_id)
        if room is None:
            raise RoomNotFoundError(room_id)
        return room
    
    def list_rooms(self, status: Optional[RoomStatus] = None) -> List[Room]:
        """List all rooms using in-memory service."""
        return self.in_memory_service.list_rooms(status)
    
    def get_player(self, player_id: str) -> Optional[Player]:
        """Get a player by ID using in-memory service."""
        return self.in_memory_service.get_player(player_id)
    
    def get_players_in_room(self, room_id: str) -> List[Player]:
        """
        Get all players in a room using in-memory service.
        Raises RoomNotFoundError if the room doesn't exist.
        """
        room = self.in_memory_service.get_room(room_id)
        if room is None:
            raise RoomNotFoundError(room_id)
        return self.in_memory_service.get_players_in_room(room_id)
    
    async def end_turn(self, room_id: str, user: UserInDB) -> bool:
        """
        End the current player's turn, checking that it's the user's turn.
        Raises appropriate exceptions for error conditions.
        """
        # Check if room exists and game is in progress
        room = self.in_memory_service.get_room(room_id)
        if room is None:
            raise RoomNotFoundError(room_id)
            
        if room.status != RoomStatus.PLAYING:
            raise GameError(detail=f"Game in room {room_id} is not in progress")
        
        # Get user details
        users_collection = DatabaseManager.get_collection(USERS_COLLECTION)
        user_doc = await users_collection.find_one({"google_id": user.google_id})
        
        if not user_doc:
            raise UserNotFoundError()
            
        # Check if user is in this room and it's their turn
        current_game = user_doc.get("current_game_details", {})
        is_in_room = current_game.get("room_id") == room_id
        player_id = current_game.get("player_id")
        
        if not is_in_room:
            raise NotInRoomError(room_id)
            
        if player_id != room.current_turn_player_id:
            raise NotYourTurnError(room_id)
        
        # Store original state for rollback
        original_player_id = room.current_turn_player_id
        original_turn_number = room.turn_number
        
        # End turn in memory
        result = self.in_memory_service.end_turn(room_id)
        if not result:
            # This shouldn't happen if our previous checks are thorough
            raise GameError(detail="Failed to end turn")
        
        # Prepare the operations
        rooms_collection = DatabaseManager.get_collection(ROOMS_COLLECTION)
        
        # Perform the database operations
        try:
            # Update room in MongoDB
            await rooms_collection.update_one(
                {"room_id": room_id},
                {"$set": room.dict()}
            )
            
            return True
        except Exception as e:
            # If there's an error, revert the in-memory state
            room.current_turn_player_id = original_player_id
            room.turn_number = original_turn_number
            raise e