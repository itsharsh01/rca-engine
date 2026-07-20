from pydantic import BaseModel, Field
from typing import Dict, Any

class UserSignupRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")

class UserLoginRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")

class PlatformConfigureRequest(BaseModel):
    platform_name: str
    credentials: Dict[str, Any]

class TestConnectionRequest(BaseModel):
    platform_name: str
    credentials: Dict[str, Any]
