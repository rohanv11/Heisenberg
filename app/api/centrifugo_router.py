"""
API routes for Centrifugo integration.
"""
from fastapi import APIRouter, HTTPException, Body, Depends, status
from typing import Dict
from pydantic import BaseModel
import logging

from app.services.centrifugo_service import CentrifugoService
from app.utils.exception_handlers import handle_exceptions


router = APIRouter()
logger = logging.getLogger(__name__)


class GenerateTokenRequest(BaseModel):
    user_id: str


@router.post("/centrifugo/token")
@handle_exceptions
async def generate_token(request: GenerateTokenRequest):
    """
    Generate a connection token for Centrifugo.
    """
    if not request.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is required"
        )
        
    centrifugo_service = CentrifugoService.get_instance()
    token = centrifugo_service.generate_connection_token(request.user_id)
    return {"token": token}


@router.post("/centrifugo/publish/{channel}")
@handle_exceptions
async def publish_to_channel(channel: str, data: Dict = Body(...)):
    """
    Publish data to a Centrifugo channel.
    """
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Channel name is required"
        )
        
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data payload is required"
        )
        
    centrifugo_service = CentrifugoService.get_instance()
    try:
        result = await centrifugo_service.publish(channel, data)
        return result
    except Exception as e:
        logger.error(f"Failed to publish to Centrifugo channel {channel}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to publish to channel"
        )