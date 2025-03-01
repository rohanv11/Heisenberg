import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

from app.services.auth_service import AuthService
from app.models.user import UserInDB
from app.config.backend import MongoDB
from jose import jwt

# Mock data
MOCK_GOOGLE_ID = "google123"
MOCK_EMAIL = "test@example.com"
MOCK_NAME = "Test User"
MOCK_USERNAME = "test_user"


@pytest.fixture
def auth_service():
    return AuthService()


@pytest.fixture
async def setup_mongodb():
    # Mock the MongoDB connection and client
    MongoDB.db = MagicMock()
    MongoDB.client = MagicMock()
    
    # Create a mock users collection
    users_collection = AsyncMock()
    MongoDB.db = {"users": users_collection}
    MongoDB.get_collection = MagicMock(return_value=users_collection)
    
    return users_collection


@pytest.mark.asyncio
async def test_authenticate_user_new_user(auth_service, setup_mongodb):
    # Setup
    users_collection = setup_mongodb
    users_collection.find_one.return_value = None  # User doesn't exist yet
    
    # Mock the OAuth token exchange and profile info
    auth_service.exchange_code = AsyncMock(return_value={"access_token": "token123"})
    auth_service.get_user_info = AsyncMock(return_value={
        "sub": MOCK_GOOGLE_ID,
        "email": MOCK_EMAIL,
        "name": MOCK_NAME
    })
    
    # Test
    result = await auth_service.authenticate_user("auth_code_123")
    
    # Assertions
    assert result is not None
    assert result.google_id == MOCK_GOOGLE_ID
    assert result.email == MOCK_EMAIL
    assert result.name == MOCK_NAME
    assert result.cash == 50000  # Default starting cash
    assert result.games_played == 0
    
    # Verify MongoDB interaction
    users_collection.find_one.assert_called_once_with({"google_id": MOCK_GOOGLE_ID})
    users_collection.insert_one.assert_called_once()


@pytest.mark.asyncio
async def test_authenticate_user_existing_user(auth_service, setup_mongodb):
    # Setup
    users_collection = setup_mongodb
    
    # Create mock user that already exists in DB
    existing_user = {
        "google_id": MOCK_GOOGLE_ID,
        "email": MOCK_EMAIL,
        "name": MOCK_NAME,
        "username": MOCK_USERNAME,
        "cash": 75000,  # User has more cash from previous games
        "games_played": 5,
        "achievements": {"first_win": True},
        "current_game_details": {},
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow() - timedelta(days=1)  # Last update was yesterday
    }
    
    users_collection.find_one.return_value = existing_user
    
    # Mock the OAuth token exchange and profile info
    auth_service.exchange_code = AsyncMock(return_value={"access_token": "token123"})
    auth_service.get_user_info = AsyncMock(return_value={
        "sub": MOCK_GOOGLE_ID,
        "email": MOCK_EMAIL,
        "name": MOCK_NAME
    })
    
    # Test
    result = await auth_service.authenticate_user("auth_code_123")
    
    # Assertions
    assert result is not None
    assert result.google_id == MOCK_GOOGLE_ID
    assert result.email == MOCK_EMAIL
    assert result.name == MOCK_NAME
    assert result.cash == 75000  # Preserved from DB
    assert result.games_played == 5
    assert result.achievements == {"first_win": True}
    
    # Verify MongoDB interaction
    users_collection.find_one.assert_called_once_with({"google_id": MOCK_GOOGLE_ID})
    users_collection.update_one.assert_called_once()  # Should update the last login time


@pytest.mark.asyncio
async def test_get_current_user(auth_service, setup_mongodb):
    # Setup
    users_collection = setup_mongodb
    
    # Create mock user
    existing_user = {
        "google_id": MOCK_GOOGLE_ID,
        "email": MOCK_EMAIL,
        "name": MOCK_NAME,
        "username": MOCK_USERNAME,
        "cash": 50000,
        "games_played": 0,
        "achievements": {},
        "current_game_details": {},
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    users_collection.find_one.return_value = existing_user
    
    # Create a valid token
    token = auth_service.create_access_token({"sub": MOCK_GOOGLE_ID})
    
    # Test
    result = await auth_service.get_current_user(token)
    
    # Assertions
    assert result is not None
    assert result.google_id == MOCK_GOOGLE_ID
    assert result.email == MOCK_EMAIL
    assert result.name == MOCK_NAME
    
    # Verify MongoDB interaction
    users_collection.find_one.assert_called_once_with({"google_id": MOCK_GOOGLE_ID})


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(auth_service, setup_mongodb):
    # Setup - Invalid token
    invalid_token = "invalid.token.string"
    
    # Test
    result = await auth_service.get_current_user(invalid_token)
    
    # Assertions
    assert result is None