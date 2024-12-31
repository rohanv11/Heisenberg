from fastapi import APIRouter
from app.socket_manager import rooms

router = APIRouter()

@router.get("/rooms")
def get_rooms():
    public_rooms = {code: details for code, details in rooms.items() if details['public']}
    return {"rooms": list(public_rooms.keys())}
