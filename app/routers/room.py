from fastapi import APIRouter, Depends
from pydantic import ValidationError
from fastapi import HTTPException

from app.schemas.room import RoomCreate, RoomFull
from app.room_management.room_manager import RoomManager
from app.utils.exceptions import RoomValidationException


room_router = APIRouter()
 

@room_router.post("/", response_model=RoomFull)
async def create_room(
    room: RoomCreate, 
    player_id: str,  # Assume this is passed in the request (e.g., from auth middleware)
    room_manager: RoomManager = Depends(lambda: RoomManager())
):
    """Create a new room and join the creator."""
    return await room_manager.create_room(room, player_id)
