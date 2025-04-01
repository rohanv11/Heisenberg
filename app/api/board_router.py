from fastapi import APIRouter, HTTPException
from app.services.board_service import BoardService

router = APIRouter()

@router.get("/board/{country_code}")
async def get_board(country_code: str):
    """
    Get board data for a specific country.
    """
    try:
        board_data = BoardService.get_board(country_code)
        return board_data.dict()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

