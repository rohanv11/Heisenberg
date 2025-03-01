"""
API routes for Centrifugo integration.
"""
from fastapi import APIRouter, HTTPException, Body, Depends
from typing import Dict
from pydantic import BaseModel

from app.services.centrifugo_service import CentrifugoService


router = APIRouter()


class GenerateTokenRequest(BaseModel):
    user_id: str


@router.post("/centrifugo/token")
async def generate_token(request: GenerateTokenRequest):
    """
    Generate a connection token for Centrifugo.
    """
    centrifugo_service = CentrifugoService.get_instance()
    token = centrifugo_service.generate_connection_token(request.user_id)
    return {"token": token}


@router.post("/centrifugo/publish/{channel}")
async def publish_to_channel(channel: str, data: Dict = Body(...)):
    """
    Publish data to a Centrifugo channel.
    """
    centrifugo_service = CentrifugoService.get_instance()
    result = await centrifugo_service.publish(channel, data)
    return result