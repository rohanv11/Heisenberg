"""
Service for interacting with Centrifugo server.
"""
import json
import hmac
import hashlib
import time
from typing import Dict, Any, Optional, List

import httpx

from app.config.settings import CENTRIFUGO_HOST, CENTRIFUGO_PORT, CENTRIFUGO_API_KEY


class CentrifugoService:
    """
    Service for interacting with Centrifugo server.
    Implemented as a singleton.
    """
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """
        Get the singleton instance of CentrifugoService.
        """
        if cls._instance is None:
            cls._instance = CentrifugoService()
        return cls._instance
    
    def __init__(self):
        self.api_url = f"http://{CENTRIFUGO_HOST}:{CENTRIFUGO_PORT}/api"
        self.api_key = CENTRIFUGO_API_KEY
    
    async def publish(self, channel: str, data: Dict[str, Any]) -> Dict:
        """
        Publish data to a channel.
        """
        async with httpx.AsyncClient() as client:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"apikey {self.api_key}"
            }
            
            payload = {
                "method": "publish",
                "params": {
                    "channel": channel,
                    "data": data
                }
            }
            
            response = await client.post(
                self.api_url,
                headers=headers,
                json=payload
            )
            
            return response.json()
    
    async def broadcast(self, channels: List[str], data: Dict[str, Any]) -> Dict:
        """
        Broadcast data to multiple channels.
        """
        async with httpx.AsyncClient() as client:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"apikey {self.api_key}"
            }
            
            payload = {
                "method": "broadcast",
                "params": {
                    "channels": channels,
                    "data": data
                }
            }
            
            response = await client.post(
                self.api_url,
                headers=headers,
                json=payload
            )
            
            return response.json()
    
    async def presence(self, channel: str) -> Dict:
        """
        Get presence information for a channel.
        """
        async with httpx.AsyncClient() as client:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"apikey {self.api_key}"
            }
            
            payload = {
                "method": "presence",
                "params": {
                    "channel": channel
                }
            }
            
            response = await client.post(
                self.api_url,
                headers=headers,
                json=payload
            )
            
            return response.json()
    
    def generate_connection_token(self, user_id: str, expires_at: int = None) -> str:
        """
        Generate a connection token for a user.
        """
        if expires_at is None:
            expires_at = int(time.time()) + 3600  # 1 hour from now
        
        claims = {
            "sub": user_id,
            "exp": expires_at
        }
        
        claims_json = json.dumps(claims)
        
        # Create HMAC SHA-256 signature
        signature = hmac.new(
            self.api_key.encode(),
            claims_json.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{signature}.{claims_json}"