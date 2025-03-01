from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

from app.models.user import UserInDB
from app.services.auth_service import AuthService

# OAuth2 scheme for JWT token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

# Initialize auth service
auth_service = AuthService()


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """
    Dependency to get the current authenticated user.
    Raises a 401 exception if authentication fails.
    """
    user = await auth_service.get_current_user(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_optional_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[UserInDB]:
    """
    Dependency to get the current user if authenticated, or None if not.
    Does not raise an exception if authentication fails.
    """
    if token is None:
        return None
    try:
        return await auth_service.get_current_user(token)
    except HTTPException:
        return None