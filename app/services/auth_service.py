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
        self.client_id = client_id
        self.redirect_url = redirect_url
        self.jwt_secret = jwt_secret
        self.jwt_algo = jwt_algo
        self.jwt_exp_mins = jwt_exp_mins

    async def get_authorization_url(self) -> str:
        """Get the Google OAuth authorization URL."""
        return await self.oauth_client.get_authorization_url(
            redirect_uri=self.redirect_url,
            scope=["https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"]
        )

    async def exchange_code(self, code: str) -> OAuth2Token:
        """Exchange the authorization code for an access token."""
        token = await self.oauth_client.get_access_token(
            code=code,
            redirect_uri=self.redirect_url
        )
        return token

    async def get_user_info(self, token: OAuth2Token) -> Dict[str, Any]:
        """Get user information from Google OAuth using the id_token."""
        print("token", token)
        # --- Start of new id_token decoding logic ---
        id_token = token.get("id_token")
        if not id_token:
            raise ValueError("id_token not found in OAuth2Token response.")

        # Decode the ID token to get the payload.
        # Google's ID tokens are signed with RS256.
        # For this specific use case (getting user info from a token just received from Google),
        # we can decode the payload directly without verifying the signature against Google's keys,
        # as the token was just received from a trusted Google endpoint.
        payload = jwt.decode(id_token, key=None, 
                             options={"verify_signature": False, "verify_at_hash": False}, 
                             audience=self.client_id)

        return {
            "sub": payload.get("sub"),
            "email": payload.get("email"),
            "name": payload.get("name", payload.get("given_name", payload.get("email"))), # Fallback for name
        }
        # --- End of new id_token decoding logic ---

        # --- Original code (commented out) ---
        # user_info = await self.oauth_client.get_profile(token["access_token"])
        # return user_info
        # --- End of original code ---

    async def authenticate_user(self, code: str) -> Optional[UserInDB]:
        """
        Authenticate a user with Google OAuth and create or retrieve their account.
        Returns the user if authentication is successful, None otherwise.
        """
        try:
            token = await self.exchange_code(code)
            user_info = await self.get_user_info(token)
            print("user info fetch from google", user_info)

            # Create a UserInDB instance directly, bypassing the database for testing
            user = UserInDB.create_from_google(
                email=user_info.get("email", ""),
                name=user_info.get("name", "Unknown User"),
                google_id=user_info["sub"]
            )
            return user

            # The original DB code below is not reached, but is kept as requested.
            # To implement DB part
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
