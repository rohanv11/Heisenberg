import pytest
from fastapi.testclient import TestClient

from app.main import server_app
from app.services.room_service import RoomService


@pytest.fixture
def client():
    """
    Create a test client.
    """
    return TestClient(server_app)


@pytest.fixture(autouse=True)
def reset_singleton():
    """
    Reset the RoomService singleton instance before each test.
    This avoids test interference.
    """
    # Reset instance
    RoomService._instance = None
    yield
    # Reset again after test
    RoomService._instance = None


def test_create_room(client):
    """
    Test creating a room via API.
    """
    response = client.post(
        "/api/rooms",
        json={
            "room_name": "Test Room",
            "host_player_name": "Host Player",
            "even_build": True,
            "starting_cash": 1500,
            "max_players": 4
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "room" in data
    assert "player" in data
    
    room = data["room"]
    player = data["player"]
    
    assert room["name"] == "Test Room"
    assert room["status"] == "waiting"
    assert len(room["players"]) == 1
    assert room["players"][0] == player["player_id"]
    
    assert player["name"] == "Host Player"
    assert player["cash"] == 1500


def test_list_rooms(client):
    """
    Test listing rooms via API.
    """
    # First, create a room
    client.post(
        "/api/rooms",
        json={
            "room_name": "Test Room",
            "host_player_name": "Host Player"
        }
    )
    
    # Now list the rooms
    response = client.get("/api/rooms")
    
    assert response.status_code == 200
    rooms = response.json()
    
    assert len(rooms) >= 1
    assert any(room["name"] == "Test Room" for room in rooms)


def test_get_room(client):
    """
    Test getting a room by ID via API.
    """
    # First, create a room
    create_response = client.post(
        "/api/rooms",
        json={
            "room_name": "Test Room",
            "host_player_name": "Host Player"
        }
    )
    room_id = create_response.json()["room"]["room_id"]
    
    # Now get the room by ID
    response = client.get(f"/api/rooms/{room_id}")
    
    assert response.status_code == 200
    room = response.json()
    
    assert room["room_id"] == room_id
    assert room["name"] == "Test Room"


def test_join_room(client):
    """
    Test joining a room via API.
    """
    # First, create a room
    create_response = client.post(
        "/api/rooms",
        json={
            "room_name": "Test Room",
            "host_player_name": "Host Player"
        }
    )
    room_id = create_response.json()["room"]["room_id"]
    
    # Now join the room
    response = client.post(
        f"/api/rooms/{room_id}/join",
        json={"player_name": "New Player"}
    )
    
    assert response.status_code == 200
    player = response.json()
    
    assert player["name"] == "New Player"
    
    # Verify the player is in the room
    room_response = client.get(f"/api/rooms/{room_id}")
    room = room_response.json()
    
    assert len(room["players"]) == 2
    assert player["player_id"] in room["players"]


def test_start_game(client):
    """
    Test starting a game via API.
    """
    # First, create a room
    create_response = client.post(
        "/api/rooms",
        json={
            "room_name": "Test Room",
            "host_player_name": "Host Player"
        }
    )
    room_id = create_response.json()["room"]["room_id"]
    
    # Add a second player
    client.post(
        f"/api/rooms/{room_id}/join",
        json={"player_name": "Player 2"}
    )
    
    # Now start the game
    response = client.post(f"/api/rooms/{room_id}/start")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "started"
    
    # Verify the room status
    room_response = client.get(f"/api/rooms/{room_id}")
    room = room_response.json()
    
    assert room["status"] == "playing"
    assert room["current_turn_player_id"] is not None