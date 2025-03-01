from fastapi import APIRouter, Depends
from pydantic import ValidationError
from fastapi import HTTPException

from app.schemas.room import RoomCreate, RoomFull
from app.room_management.room_manager import RoomManager


room_router = APIRouter()
 
@room_router.post("/join", response_model=RoomFull)
async def create_room(
    room: RoomCreate, 
    player_id: str,
    room_manager: RoomManager = Depends(lambda: RoomManager())
):
    """Create a new room and join the creator."""
    return await room_manager.create_room(room, player_id)


@room_router.post("/leave", response_model=RoomFull)
async def leave_room(
    room_id: str, 
    player_id: str,
    room_manager: RoomManager = Depends(lambda: RoomManager())
):
    """Allow a player to leave a room."""
    return await room_manager.leave_room(room_id, player_id)
