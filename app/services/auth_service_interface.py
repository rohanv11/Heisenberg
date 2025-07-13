from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from app.models.user import UserInDB

class AuthServiceInterface(ABC):
    @abstractmethod
    async def get_authorization_url(self) -> str:
        pass

    @abstractmethod
    async def authenticate_user(self, code: str) -> Optional[UserInDB]:
        pass

    @abstractmethod
    def create_access_token(self, data: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def get_current_user(self, token: str) -> Optional[UserInDB]:
        pass