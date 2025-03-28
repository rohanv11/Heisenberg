from fastapi import APIRouter
import logging
from app.utils.exception_handlers import handle_exceptions

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/game/info")
@handle_exceptions
async def get_game_info():
    """
    Get general information about the game.
    """
    return {
        "name": "Rockefeller",
        "version": "0.1.0",
        "description": "A Monopoly-like board game"
    }