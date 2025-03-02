from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.oauth2 import OAuth2Token

from app.config.settings import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    OAUTH_REDIRECT_URL,
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_EXPIRATION_MINUTES
)
from app.config.backend import DatabaseManager, USERS_COLLECTION
from app.models.user import UserInDB, UserResponse


class AuthService:
    """Service for handling user authentication."""
    
    def __init__(self):
        self.oauth_client = GoogleOAuth2(
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET
        )
    
    def get_authorization_url(self) -> str:
        """Get the Google OAuth authorization URL."""
        return self.oauth_client.get_authorization_url(
            redirect_uri=OAUTH_REDIRECT_URL,
            scope=["email", "profile"]
        )
    
    async def exchange_code(self, code: str) -> OAuth2Token:
        """Exchange the authorization code for an access token."""
        token = await self.oauth_client.get_access_token(
            code=code,
            redirect_uri=OAUTH_REDIRECT_URL
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
            # Exchange the authorization code for an access token
            token = await self.exchange_code(code)
            
            # Get user information from Google
            user_info = await self.get_user_info(token)
            
            # Check if user exists in the database
            users_collection = DatabaseManager.get_collection(USERS_COLLECTION)
            user_doc = await users_collection.find_one({"google_id": user_info["sub"]})
            
            if user_doc:
                # Update last login time
                await users_collection.update_one(
                    {"google_id": user_info["sub"]},
                    {"$set": {"updated_at": datetime.utcnow()}}
                )
                # Convert document to UserInDB model
                return UserInDB(**user_doc)
            else:
                # Create a new user
                new_user = UserInDB.create_from_google(
                    email=user_info["email"],
                    name=user_info["name"],
                    google_id=user_info["sub"]
                )
                
                # Insert the new user into the database
                await users_collection.insert_one(new_user.dict())
                
                return new_user
                
        except Exception as e:
            # Log the exception
            print(f"Authentication error: {e}")
            return None
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """
        Create a JWT access token for the user.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded_jwt
    
    async def get_current_user(self, token: str) -> Optional[UserInDB]:
        """
        Validate the JWT token and return the current user.
        """
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            google_id: str = payload.get("sub")
            if google_id is None:
                return None
            
            # Get user from database
            users_collection = DatabaseManager.get_collection(USERS_COLLECTION)
            user_doc = await users_collection.find_one({"google_id": google_id})
            
            if user_doc is None:
                return None
                
            return UserInDB(**user_doc)
            
        except JWTError:
            return None