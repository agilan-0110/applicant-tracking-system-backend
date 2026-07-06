from pydantic import BaseModel,EmailStr,ConfigDict
from datetime import datetime
from typing import Literal



class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Literal["candidate", "recruiter"]


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: Literal["candidate", "recruiter"]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
