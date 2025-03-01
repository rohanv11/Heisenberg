from fastapi import APIRouter

router = APIRouter()

@router.get("/game/info")
async def get_game_info():
    """
    Get general information about the game.
    """
    return {
        "name": "Rockefeller",
        "version": "0.1.0",
        "description": "A Monopoly-like board game"
    }