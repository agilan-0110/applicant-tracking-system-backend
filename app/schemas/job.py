from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JobCreate(BaseModel):
    title: str
    description: str
    location: str
    min_salary: int
    max_salary: int
    

class JobUpdate(BaseModel):
    title: str
    description: str
    location: str
    min_salary: int
    max_salary: int


class JobResponse(BaseModel):
    id: int
    title: str
    description: str
    location: str
    min_salary: int
    max_salary: int
    recruiter_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)



class RecruiterJobResponse(BaseModel):
    id: int
    title: str
    location: str
    min_salary: int
    max_salary: int
    status: str
    applicant_count: int

    model_config = ConfigDict(from_attributes=True)