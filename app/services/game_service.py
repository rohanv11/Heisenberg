"""
Service for managing game operations.
"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from app.models.game import Game, GameConfig, GameStatus
from app.models.player import Player
from app.config import game_config


class GameService:
    """
    Service for managing game operations.
    """
    def __init__(self):
        self.games: Dict[str, Game] = {}
        self.players: Dict[str, Player] = {}
    
    def create_game(self, name: str, config: Optional[GameConfig] = None) -> Game:
        """
        Create a new game.
        """
        if config is None:
            config = GameConfig()
        
        game_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        game = Game(
            game_id=game_id,
            name=name,
            config=config,
            created_at=now,
            updated_at=now
        )
        
        self.games[game_id] = game
        return game
    
    def get_game(self, game_id: str) -> Optional[Game]:
        """
        Get a game by ID.
        """
        return self.games.get(game_id)
    
    def list_games(self, status: Optional[GameStatus] = None) -> List[Game]:
        """
        List all games, optionally filtered by status.
        """
        if status is None:
            return list(self.games.values())
        return [game for game in self.games.values() if game.status == status]
    
    def add_player(self, game_id: str, player_name: str) -> Optional[Player]:
        """
        Add a player to a game.
        """
        game = self.get_game(game_id)
        if game is None or game.status != GameStatus.WAITING:
            return None
        
        if len(game.players) >= game.config.max_players:
            return None
        
        player_id = str(uuid.uuid4())
        player = Player(
            player_id=player_id,
            name=player_name,
            cash=game.config.starting_cash
        )
        
        self.players[player_id] = player
        game.players.append(player_id)
        game.updated_at = datetime.now().isoformat()
        
        return player
    
    def start_game(self, game_id: str) -> bool:
        """
        Start a game.
        """
        game = self.get_game(game_id)
        if game is None or game.status != GameStatus.WAITING:
            return False
        
        if len(game.players) < 2:  # At least 2 players required
            return False
        
        game.status = GameStatus.STARTED
        game.current_turn = game.players[0]  # First player's turn
        game.updated_at = datetime.now().isoformat()
        
        return True
    
    def end_turn(self, game_id: str) -> bool:
        """
        End the current player's turn and move to the next player.
        """
        game = self.get_game(game_id)
        if game is None or game.status != GameStatus.STARTED:
            return False
        
        current_index = game.players.index(game.current_turn)
        next_index = (current_index + 1) % len(game.players)
        
        game.current_turn = game.players[next_index]
        game.turn_number += 1
        game.updated_at = datetime.now().isoformat()
        
        return True


# Create a singleton instance of the service
game_service = GameService()