import pytest
from app.services.room_service import RoomService
from app.models.game import GameConfig
from app.models.room import RoomStatus


@pytest.fixture
def room_service():
    """
    Create a fresh RoomService instance for testing.
    """
    # Create a new instance for testing instead of using the singleton
    # to avoid test interference
    return RoomService()


def test_create_room(room_service):
    """
    Test creating a room.
    """
    room_name = "Test Room"
    host_name = "Host Player"
    config = GameConfig(even_build=True, starting_cash=1500, max_players=4)
    
    result = room_service.create_room(room_name, host_name, config)
    
    assert "room" in result
    assert "player" in result
    
    room = result["room"]
    player = result["player"]
    
    assert room.name == room_name
    assert room.status == RoomStatus.WAITING
    assert len(room.players) == 1
    assert room.players[0] == player.player_id
    assert room.host_player_id == player.player_id
    
    assert player.name == host_name
    assert player.cash == config.starting_cash


def test_join_room(room_service):
    """
    Test joining a room.
    """
    # First create a room
    room_data = room_service.create_room("Test Room", "Host Player")
    room = room_data["room"]
    
    # Now join the room
    player_name = "New Player"
    player = room_service.join_room(room.room_id, player_name)
    
    assert player is not None
    assert player.name == player_name
    assert player.cash == room.config.starting_cash
    
    # Verify the room has been updated
    updated_room = room_service.get_room(room.room_id)
    assert len(updated_room.players) == 2
    assert player.player_id in updated_room.players


def test_start_game(room_service):
    """
    Test starting a game.
    """
    # Create a room with a host
    room_data = room_service.create_room("Test Room", "Host Player")
    room = room_data["room"]
    
    # Add a second player (need at least 2 players to start)
    room_service.join_room(room.room_id, "Player 2")
    
    # Start the game
    success = room_service.start_game(room.room_id)
    assert success is True
    
    # Check room status
    updated_room = room_service.get_room(room.room_id)
    assert updated_room.status == RoomStatus.PLAYING
    assert updated_room.current_turn_player_id == updated_room.players[0]
    assert "game_state" in updated_room.dict() and updated_room.game_state is not None