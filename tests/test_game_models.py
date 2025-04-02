from app.models.game_models import Room, RoomStatus, GameConfig, Player, BoardCountry, BoardData
from app.services.board_service import BoardService
from datetime import datetime
import pytest


# Mock the BoardService for testing
@pytest.fixture(autouse=True)
def mock_board_service(monkeypatch):
    """Mock the board service to return test board data"""
    def mock_get_board(country_code):
        # Create a simple test board
        from app.models.game_models import BoardSpaceData
        return BoardData.model_validate({
            0: BoardSpaceData(name="GO", type="go", pos=0),
            1: BoardSpaceData(name="Test Property", type="property", pos=1),
            2: BoardSpaceData(name="Test Chance", type="chance", pos=2),
            3: BoardSpaceData(name="Test Jail", type="jail", pos=3)
        })
    
    monkeypatch.setattr(BoardService, "get_board", mock_get_board)
    monkeypatch.setattr(BoardService, "load_boards", lambda: None)


def test_create_room():
    """Test room creation with default settings"""
    # Create a room with default settings
    now = datetime.now().isoformat()
    player = Player(player_id="test_player", name="Test Player", cash=1500)
    
    room = Room(
        room_id="123456",
        status=RoomStatus.WAITING,
        config=GameConfig(),
        players=[player],
        host_player_id="test_player",
        created_at=now,
        updated_at=now
    )
    
    # Test room properties
    assert room.room_id == "123456"
    assert room.status == RoomStatus.WAITING
    assert room.config.board_country == BoardCountry.IN
    assert room.config.max_players == 4
    assert len(room.players) == 1
    assert room.host_player_id == "test_player"
    
    # Test player properties
    assert room.players[0].player_id == "test_player"
    assert room.players[0].name == "Test Player"
    assert room.players[0].cash == 1500
    assert room.players[0].position == 0  # Player starts at position 0
    
    # Test board data was loaded
    assert room.board_data is not None
    assert len(room.board_data.root) == 4  # Our mock board has 4 spaces


def test_player_movement():
    """Test player movement on the board"""
    # Create a room with a player
    now = datetime.now().isoformat()
    player = Player(player_id="test_player", name="Test Player", cash=1500)
    
    room = Room(
        room_id="123456",
        status=RoomStatus.PLAYING,
        config=GameConfig(),
        players=[player],
        host_player_id="test_player",
        created_at=now,
        updated_at=now
    )
    
    # Initially at position 0
    assert room.players[0].position == 0
    
    # Move player forward by 2
    room.players[0].position = (room.players[0].position + 2) % len(room.board_data.root)
    assert room.players[0].position == 2
    
    # Move player forward by 3 (should wrap around)
    room.players[0].position = (room.players[0].position + 3) % len(room.board_data.root)
    assert room.players[0].position == 1  # 2 + 3 = 5, 5 % 4 = 1


def test_multiple_players():
    """Test room with multiple players"""
    now = datetime.now().isoformat()
    player1 = Player(player_id="player1", name="Player 1", cash=1500)
    player2 = Player(player_id="player2", name="Player 2", cash=1500)
    player3 = Player(player_id="player3", name="Player 3", cash=1500)
    
    room = Room(
        room_id="123456",
        status=RoomStatus.WAITING,
        config=GameConfig(),
        players=[player1, player2, player3],
        host_player_id="player1",
        created_at=now,
        updated_at=now
    )
    
    # Test room has all players
    assert len(room.players) == 3
    
    # Test positions are tracked independently
    room.players[0].position = 1
    room.players[1].position = 2
    room.players[2].position = 3
    
    assert room.players[0].position == 1
    assert room.players[1].position == 2
    assert room.players[2].position == 3