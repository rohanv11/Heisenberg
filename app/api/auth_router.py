from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from app.models.user import Token, UserResponse, UserInDB
from app.services.auth_service import AuthService
from app.api.dependencies import get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

auth_service = AuthService()


@router.get("/login")
async def login():
    """
    Get Google OAuth login URL.
    The frontend should redirect the user to this URL to start the OAuth flow.
    """
    return {"login_url": auth_service.get_authorization_url()}


@router.get("/callback")
async def auth_callback(code: str):
    """
    Handle the Google OAuth callback.
    This endpoint receives the authorization code and exchanges it for a JWT token.
    """
    user = await auth_service.authenticate_user(code)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
        )
    
    # Create JWT token
    access_token = auth_service.create_access_token(
        data={"sub": user.google_id}
    )
    
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserInDB = Depends(get_current_user)):
    """
    Get information about the currently authenticated user.
    """
    return UserResponse(
        email=current_user.email,
        name=current_user.name,
        username=current_user.username,
        cash=current_user.cash,
        games_played=current_user.games_played,
        achievements=current_user.achievements,
        current_game_details=current_user.current_game_details
    )