from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CandidateCreate(BaseModel):
    phone: str
    skills: str
    experience_years: int
    education: str


class CandidateUpdate(BaseModel):
    phone: str
    skills: str
    experience_years: int
    education: str


class CandidateResponse(BaseModel):
    id: int
    user_id: int
    phone: str
    skills: str
    experience_years: int
    education: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)