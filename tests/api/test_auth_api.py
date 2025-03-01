import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.main import server_app
from app.services.auth_service import AuthService
from app.models.user import UserInDB


@pytest.fixture
def client():
    return TestClient(server_app)


@pytest.fixture
def mock_auth_service():
    with patch("app.api.auth_router.auth_service") as mock_service:
        yield mock_service


def test_login_endpoint(client, mock_auth_service):
    # Setup
    mock_auth_service.get_authorization_url.return_value = "https://google.com/oauth/auth?..."
    
    # Test
    response = client.get("/api/auth/login")
    
    # Assertions
    assert response.status_code == 200
    assert "login_url" in response.json()
    assert response.json()["login_url"] == "https://google.com/oauth/auth?..."
    mock_auth_service.get_authorization_url.assert_called_once()


@pytest.mark.asyncio
async def test_auth_callback_successful(client, mock_auth_service):
    # Setup
    mock_user = UserInDB(
        email="test@example.com",
        name="Test User",
        username="test_user",
        google_id="google123",
        cash=50000,
        games_played=0,
        achievements={},
        current_game_details={}
    )
    
    mock_auth_service.authenticate_user = AsyncMock(return_value=mock_user)
    mock_auth_service.create_access_token.return_value = "jwt_token_123"
    
    # Test
    with patch("app.api.auth_router.auth_service", mock_auth_service):
        response = client.get("/api/auth/callback?code=auth_code_123")
    
    # Assertions
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["access_token"] == "jwt_token_123"
    assert response.json()["token_type"] == "bearer"
    
    # Verify method calls
    mock_auth_service.authenticate_user.assert_called_once_with("auth_code_123")
    mock_auth_service.create_access_token.assert_called_once()


@pytest.mark.asyncio
async def test_auth_callback_failed(client, mock_auth_service):
    # Setup - Authentication fails
    mock_auth_service.authenticate_user = AsyncMock(return_value=None)
    
    # Test
    with patch("app.api.auth_router.auth_service", mock_auth_service):
        response = client.get("/api/auth/callback?code=invalid_code")
    
    # Assertions
    assert response.status_code == 401
    assert "detail" in response.json()
    
    # Verify method calls
    mock_auth_service.authenticate_user.assert_called_once_with("invalid_code")
    mock_auth_service.create_access_token.assert_not_called()


@pytest.mark.asyncio
async def test_get_current_user_info(client, mock_auth_service):
    # Setup
    mock_user = UserInDB(
        email="test@example.com",
        name="Test User",
        username="test_user",
        google_id="google123",
        cash=50000,
        games_played=0,
        achievements={},
        current_game_details={}
    )
    
    # Mock the dependency
    with patch("app.api.auth_router.get_current_user", return_value=mock_user):
        # Test
        response = client.get("/api/auth/me", headers={"Authorization": "Bearer test_token"})
    
    # Assertions
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
    assert response.json()["name"] == "Test User"
    assert response.json()["username"] == "test_user"
    assert response.json()["cash"] == 50000
    assert response.json()["games_played"] == 0
    assert response.json()["achievements"] == {}
    assert response.json()["current_game_details"] == {}