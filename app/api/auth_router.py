from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
import logging
from typing import Dict, Any

from app.models.user import Token, UserResponse, UserInDB
from app.services.auth_service import AuthService
from app.api.dependencies import get_current_user
from app.utils.exception_handlers import handle_exceptions

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    },
)

auth_service = AuthService()
logger = logging.getLogger(__name__)


@router.get("/login")
@handle_exceptions
async def login():
    """
    Get Google OAuth login URL.
    The frontend should redirect the user to this URL to start the OAuth flow.
    """
    try:
        print("helllo!!!")
        if not auth_service.oauth_client.client_id or not auth_service.oauth_client.client_secret:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OAuth credentials not configured"
            )
        
        return {"login_url": await auth_service.get_authorization_url()}
    except Exception as e:
        logger.exception(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate login URL"
        )


@router.get("/callback")
@handle_exceptions
async def auth_callback(code: str):
    """
    Handle the Google OAuth callback.
    This endpoint receives the authorization code and exchanges it for a JWT token.
    """
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code is required"
        )
        
    user = await auth_service.authenticate_user(code)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )
    
    # Create JWT token
    access_token = auth_service.create_access_token(
        data={"sub": user.google_id}
    )
    
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
@handle_exceptions
async def get_current_user_info(current_user: UserInDB = Depends(get_current_user)):
    """
    Get information about the currently authenticated user.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
        
    return UserResponse(
        email=current_user.email,
        name=current_user.name,
        username=current_user.username,
        cash=current_user.cash,
        games_played=current_user.games_played,
        achievements=current_user.achievements,
        current_game_details=current_user.current_game_details
    )