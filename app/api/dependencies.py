from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.services.auth_service import AuthService
from app.services.user_repository import UserRepository
from app.services.auth_service_interface import AuthServiceInterface
from app.models.user import UserInDB
from app.config.settings import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    OAUTH_REDIRECT_URL,
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_EXPIRATION_MINUTES
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/callback")

def get_user_repository() -> UserRepository:
    return UserRepository()

def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository)
) -> AuthServiceInterface:
    return AuthService(
        user_repository=user_repo,
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        redirect_url=OAUTH_REDIRECT_URL,
        jwt_secret=JWT_SECRET_KEY,
        jwt_algo=JWT_ALGORITHM,
        jwt_exp_mins=JWT_EXPIRATION_MINUTES
    )

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthServiceInterface = Depends(get_auth_service)
) -> UserInDB:
    user = await auth_service.get_current_user(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user