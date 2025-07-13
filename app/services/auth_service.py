from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.oauth2 import OAuth2Token

from app.services.auth_service_interface import AuthServiceInterface
from app.services.user_repository import UserRepository
from app.models.user import UserInDB

class AuthService(AuthServiceInterface):
    """Service for handling user authentication."""
    
    def __init__(self, user_repository: UserRepository, client_id: str, client_secret: str, redirect_url: str, jwt_secret: str, jwt_algo: str, jwt_exp_mins: int):
        self.user_repository = user_repository
        self.oauth_client = GoogleOAuth2(
            client_id=client_id,
            client_secret=client_secret
        )
        self.redirect_url = redirect_url
        self.jwt_secret = jwt_secret
        self.jwt_algo = jwt_algo
        self.jwt_exp_mins = jwt_exp_mins

    async def get_authorization_url(self) -> str:
        """Get the Google OAuth authorization URL."""
        return await self.oauth_client.get_authorization_url(
            redirect_uri=self.redirect_url,
            scope=["email", "profile"]
        )

    async def exchange_code(self, code: str) -> OAuth2Token:
        """Exchange the authorization code for an access token."""
        token = await self.oauth_client.get_access_token(
            code=code,
            redirect_uri=self.redirect_url
        )
        return token

    async def get_user_info(self, token: OAuth2Token) -> Dict[str, Any]:
        """Get user information from Google OAuth."""
        user_info = await self.oauth_client.get_profile_info(token["access_token"])
        return user_info

    async def authenticate_user(self, code: str) -> Optional[UserInDB]:
        """
        Authenticate a user with Google OAuth and create or retrieve their account.
        Returns the user if authentication is successful, None otherwise.
        """
        try:
            token = await self.exchange_code(code)
            user_info = await self.get_user_info(token)
            
            user = await self.user_repository.get_user_by_google_id(user_info["sub"])
            
            if user:
                await self.user_repository.update_user_login(user.google_id, user_info["name"])
                return await self.user_repository.get_user_by_google_id(user.google_id)
            else:
                return await self.user_repository.create_user_from_google(
                    email=user_info["email"],
                    name=user_info["name"],
                    google_id=user_info["sub"]
                )
                
        except Exception as e:
            print(f"Authentication error: {e}")
            return None

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """
        Create a JWT access token for the user.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.jwt_exp_mins)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, self.jwt_secret, algorithm=self.jwt_algo)
        return encoded_jwt

    async def get_current_user(self, token: str) -> Optional[UserInDB]:
        """
        Validate the JWT token and return the current user.
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algo])
            google_id: str = payload.get("sub")
            if google_id is None:
                return None
            
            return await self.user_repository.get_user_by_google_id(google_id)
            
        except JWTError:
            return None