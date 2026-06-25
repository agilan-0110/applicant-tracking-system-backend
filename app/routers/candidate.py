from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.oauth2 import get_current_user
from app.models.user import User
from app.models.candidate import Candidate
from app.schemas.candidate import (
    CandidateCreate,
    CandidateUpdate,
    CandidateResponse
)

router = APIRouter(
    prefix="/candidate",
    tags=["Candidate"]
)


@router.post(
    "/profile",
    response_model=CandidateResponse,
    summary="Create Candidate Profile",
    description="Create a profile for the logged-in candidate."
)
def create_profile(
    candidate: CandidateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only candidates can create a profile
    if current_user.role != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can create profiles."
        )

    # Check if profile already exists
    existing_profile = db.query(Candidate).filter(
        Candidate.user_id == current_user.id
    ).first()

    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Candidate profile already exists."
        )

    # Create candidate profile
    new_candidate = Candidate(
        user_id=current_user.id,
        phone=candidate.phone,
        skills=candidate.skills,
        experience_years=candidate.experience_years,
        education=candidate.education
    )

    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)

    return new_candidate

@router.get(
    "/profile",
    response_model=CandidateResponse,
    summary="View Candidate Profile",
    description="Retrieve the logged-in candidate's profile."
)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only candidates can view their profile
    if current_user.role != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can view profiles."
        )

    profile = db.query(Candidate).filter(
        Candidate.user_id == current_user.id
    ).first()

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found."
        )

    return profile


@router.put(
    "/profile",
    response_model=CandidateResponse,
    summary="Update Candidate Profile",
    description="Update the logged-in candidate's profile."
)
def update_profile(
    candidate: CandidateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can update profiles."
        )

    profile = db.query(Candidate).filter(
        Candidate.user_id == current_user.id
    ).first()

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found."
        )

    profile.phone = candidate.phone
    profile.skills = candidate.skills
    profile.experience_years = candidate.experience_years
    profile.education = candidate.education

    db.commit()
    db.refresh(profile)

    return profile
