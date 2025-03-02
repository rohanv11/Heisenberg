import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from app.services.room_service import RoomServiceWithAuth, RoomService
from app.models.user import UserInDB
from app.models.room import Room, RoomStatus
from app.models.game import GameConfig
from app.models.player import Player
from app.models.exceptions import NotHostError, RoomNotFoundError, UserNotFoundError
from app.config.backend import DatabaseManager


# Mock data
MOCK_GOOGLE_ID = "google123"
MOCK_EMAIL = "test@example.com"
MOCK_NAME = "Test User"
MOCK_USERNAME = "test_user"

# Mock room data
MOCK_ROOM_ID = "room123"
MOCK_ROOM_NAME = "Test Room"
MOCK_PLAYER_ID = "player123"


@pytest.fixture
def mock_user():
    return UserInDB(
        email=MOCK_EMAIL,
        name=MOCK_NAME,
        username=MOCK_USERNAME,
        google_id=MOCK_GOOGLE_ID,
        cash=50000,
        games_played=0,
        achievements={},
        current_game_details={}
    )


@pytest.fixture
def mock_host_user(mock_user):
    # Create a copy with host status
    user = mock_user.copy(deep=True)
    user.current_game_details = {
        "room_id": MOCK_ROOM_ID,
        "player_id": MOCK_PLAYER_ID,
        "is_host": True
    }
    return user


@pytest.fixture
def mock_player():
    return Player(
        player_id=MOCK_PLAYER_ID,
        name=MOCK_USERNAME,
        cash=50000
    )


@pytest.fixture
def mock_room():
    return Room(
        room_id=MOCK_ROOM_ID,
        name=MOCK_ROOM_NAME,
        status=RoomStatus.WAITING,
        config=GameConfig(),
        players=[MOCK_PLAYER_ID],
        host_player_id=MOCK_PLAYER_ID,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat(),
        max_players=4
    )


@pytest.fixture
def setup_mocks(mock_player, mock_room):
    # Mock the in-memory RoomService
    with patch.object(RoomService, "get_instance") as mock_room_service_cls:
        # Create mock instance
        mock_room_service = MagicMock()
        mock_room_service_cls.return_value = mock_room_service
        
        # Mock methods on the RoomService
        mock_room_service.get_room.return_value = mock_room
        mock_room_service.create_room.return_value = {"room": mock_room, "player": mock_player}
        mock_room_service.join_room.return_value = mock_player
        mock_room_service.get_players_in_room.return_value = [mock_player]
        mock_room_service.start_game.return_value = True
        mock_room_service.end_turn.return_value = True
        
        # DatabaseManager mocks
        DatabaseManager.mongo_db = MagicMock()
        DatabaseManager.mongo_client = MagicMock()
        
        # Create mock collections
        rooms_collection = AsyncMock()
        users_collection = AsyncMock()
        
        # Setup collection returns
        DatabaseManager.get_collection = MagicMock(side_effect=lambda name: 
            rooms_collection if name == "rooms" else users_collection)
        
        # Setup MongoDB find_one return
        users_collection.find_one.return_value = {
            "google_id": MOCK_GOOGLE_ID,
            "email": MOCK_EMAIL,
            "name": MOCK_NAME,
            "username": MOCK_USERNAME,
            "cash": 50000,
            "games_played": 0,
            "achievements": {},
            "current_game_details": {
                "room_id": MOCK_ROOM_ID,
                "player_id": MOCK_PLAYER_ID,
                "is_host": True
            }
        }
        
        # Create RoomServiceWithAuth instance to test
        room_service_with_auth = RoomServiceWithAuth()
        room_service_with_auth.in_memory_service = mock_room_service
        
        yield room_service_with_auth, mock_room_service, rooms_collection, users_collection


@pytest.mark.asyncio
async def test_create_room(setup_mocks, mock_user):
    # Setup
    room_service, mock_room_service, rooms_collection, users_collection = setup_mocks
    
    # Test
    result = await room_service.create_room(MOCK_ROOM_NAME, mock_user)
    
    # Assertions
    assert result is not None
    assert "room" in result
    assert "player" in result
    assert result["room"].name == MOCK_ROOM_NAME
    
    # Verify MongoDB interactions
    rooms_collection.insert_one.assert_called_once()
    users_collection.update_one.assert_called_once()
    
    # Verify in-memory service call
    mock_room_service.create_room.assert_called_once_with(
        MOCK_ROOM_NAME, 
        mock_user.username, 
        None  # No config specified
    )


@pytest.mark.asyncio
async def test_join_room(setup_mocks, mock_user):
    # Setup
    room_service, mock_room_service, rooms_collection, users_collection = setup_mocks
    
    # Test
    player = await room_service.join_room(MOCK_ROOM_ID, mock_user)
    
    # Assertions
    assert player is not None
    assert player.player_id == MOCK_PLAYER_ID
    assert player.name == MOCK_USERNAME
    
    # Verify MongoDB interactions
    rooms_collection.update_one.assert_called_once()
    users_collection.update_one.assert_called_once()
    
    # Verify in-memory service call
    mock_room_service.join_room.assert_called_once_with(MOCK_ROOM_ID, mock_user.username)


@pytest.mark.asyncio
async def test_start_game(setup_mocks, mock_host_user):
    # Setup
    room_service, mock_room_service, rooms_collection, users_collection = setup_mocks
    
    # Test
    result = await room_service.start_game(MOCK_ROOM_ID, mock_host_user)
    
    # Assertions
    assert result is True
    
    # Verify MongoDB interactions
    rooms_collection.update_one.assert_called_once()
    users_collection.update_one.assert_called_once()
    
    # Verify in-memory service call
    mock_room_service.start_game.assert_called_once_with(MOCK_ROOM_ID)


@pytest.mark.asyncio
async def test_start_game_not_host(setup_mocks, mock_user):
    # Setup
    room_service, mock_room_service, rooms_collection, users_collection = setup_mocks
    
    # Override the user to not be a host
    users_collection.find_one.return_value = {
        "google_id": MOCK_GOOGLE_ID,
        "current_game_details": {
            "room_id": MOCK_ROOM_ID,
            "player_id": MOCK_PLAYER_ID,
            "is_host": False  # Not the host
        }
    }
    
    # Test & Assertions
    with pytest.raises(NotHostError):
        await room_service.start_game(MOCK_ROOM_ID, mock_user)
    
    # Verify the game was not started
    mock_room_service.start_game.assert_not_called()
    rooms_collection.update_one.assert_not_called()


@pytest.mark.asyncio
async def test_room_not_found(setup_mocks, mock_user):
    # Setup
    room_service, mock_room_service, rooms_collection, users_collection = setup_mocks
    
    # Make get_room return None to simulate room not found
    mock_room_service.get_room.return_value = None
    
    # Test & Assertions
    with pytest.raises(RoomNotFoundError):
        await room_service.join_room(MOCK_ROOM_ID, mock_user)
    
    # Verify services not called
    mock_room_service.join_room.assert_not_called()
    rooms_collection.update_one.assert_not_called()
    users_collection.update_one.assert_not_called()


@pytest.mark.asyncio
async def test_user_not_found(setup_mocks, mock_user):
    # Setup
    room_service, mock_room_service, rooms_collection, users_collection = setup_mocks
    
    # Make find_one return None to simulate user not found
    users_collection.find_one.return_value = None
    
    # Test & Assertions
    with pytest.raises(UserNotFoundError):
        await room_service.start_game(MOCK_ROOM_ID, mock_user)
    
    # Verify services not called
    mock_room_service.start_game.assert_not_called()
    rooms_collection.update_one.assert_not_called()