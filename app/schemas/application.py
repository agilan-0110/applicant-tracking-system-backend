from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Literal

class ApplicationResponse(BaseModel):
    id: int
    candidate_id: int
    job_id: int
    status: str
    applied_at: datetime

    model_config = ConfigDict(from_attributes=True)




class ApplicantResponse(BaseModel):
    application_id: int
    candidate_id: int
    name: str
    email: str
    phone: str
    skills: str
    experience_years: int
    education: str
    status: Literal[
    "Applied",
    "Shortlisted",
    "Interview",
    "Rejected",
    "Hired"
]
    applied_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StatusUpdate(BaseModel):
    status: Literal[
        "Applied",
        "Shortlisted",
        "Interview",
        "Rejected",
        "Hired"
    ]