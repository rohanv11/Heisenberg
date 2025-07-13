from fastapi import APIRouter
import logging


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/game/info")

async def get_game_info():
    """
    Get general information about the game.
    """
    return {
        "name": "HighStakes",
        "version": "0.1.0",
        "description": "A trading board game"
    }