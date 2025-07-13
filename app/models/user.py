from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Optional
from datetime import datetime
import re


class UserBase(BaseModel):
    """Base User model with common fields."""
    email: EmailStr
    name: str
    username: Optional[str] = None


class UserCreate(UserBase):
    """Model used for creating a new user."""
    google_id: str


class UserInDB(UserBase):
    """Model representing a user as stored in the database."""
    google_id: str
    games_played: int = 0
    achievements: Dict = Field(default_factory=dict)
    current_game_details: Dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @classmethod
    def create_from_google(cls, email: str, name: str, google_id: str) -> "UserInDB":
        """Create a new user from Google OAuth data."""
        # Create username from email by taking everything before @ symbol
        username = re.sub(r'@.*$', '', email)
        # Replace dots with underscores for consistency
        username = username.replace('.', '_')
        
        return cls(
            email=email,
            name=name,
            username=username,
            google_id=google_id
        )


class UserResponse(UserBase):
    """Model used for user data in API responses."""
    cash: int
    games_played: int
    achievements: Dict
    current_game_details: Dict


class Token(BaseModel):
    """JWT token model."""
    access_token: str
    token_type: str = "bearer"
