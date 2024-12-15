from fastapi import APIRouter

router = APIRouter()

@router.get("/rooms")
def get_rooms():
    """Get all available rooms."""
    from ..socket_manager import rooms
    return {"rooms": list(rooms.keys())}
