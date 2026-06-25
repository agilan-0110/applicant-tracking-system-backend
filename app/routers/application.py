from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.oauth2 import get_current_user

from app.models.user import User
from app.models.job import Job
from app.models.candidate import Candidate
from app.models.application import Application

from app.schemas.application import (
    ApplicationResponse,
    ApplicantResponse,
    StatusUpdate
)

router = APIRouter(
    prefix="/applications",
    tags=["Applications"]
)


# ======================================================
# Apply for a Job
# ======================================================
@router.post(
    "/{job_id}",
    response_model=ApplicationResponse,
    summary="Apply for Job"
)
def apply_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "candidate":
        raise HTTPException(
            status_code=403,
            detail="Only candidates can apply."
        )

    candidate = db.query(Candidate).filter(
        Candidate.user_id == current_user.id
    ).first()

    if candidate is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile not found."
        )

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found."
        )

    existing = db.query(Application).filter(
        Application.candidate_id == candidate.id,
        Application.job_id == job_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Already applied for this job."
        )

    application = Application(
        candidate_id=candidate.id,
        job_id=job.id,
        status="Applied"
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return application


# ======================================================
# Candidate - View My Applications
# ======================================================
@router.get(
    "/my",
    response_model=list[ApplicationResponse]
)
def my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "candidate":
        raise HTTPException(
            status_code=403,
            detail="Only candidates can view applications."
        )

    candidate = db.query(Candidate).filter(
        Candidate.user_id == current_user.id
    ).first()

    if candidate is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile not found."
        )

    return db.query(Application).filter(
        Application.candidate_id == candidate.id
    ).all()


# ======================================================
# Recruiter - View Applicants for One Job
# ======================================================
@router.get(
    "/job/{job_id}/applicants",
    response_model=list[ApplicantResponse]
)
def get_job_applicants(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "recruiter":
        raise HTTPException(
            status_code=403,
            detail="Only recruiters can view applicants."
        )

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found."
        )

    if job.recruiter_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only view applicants for your own jobs."
        )

    applications = db.query(Application).filter(
        Application.job_id == job_id
    ).all()

    result = []

    for application in applications:

        candidate = db.query(Candidate).filter(
            Candidate.id == application.candidate_id
        ).first()

        user = db.query(User).filter(
            User.id == candidate.user_id
        ).first()

        result.append(
            ApplicantResponse(
                application_id=application.id,
                candidate_id=candidate.id,
                name=user.name,
                email=user.email,
                phone=candidate.phone,
                skills=candidate.skills,
                experience_years=candidate.experience_years,
                education=candidate.education,
                status=application.status,
                applied_at=application.applied_at
            )
        )

    return result


# ======================================================
# Recruiter - Update Application Status
# ======================================================
@router.put(
    "/{application_id}/status",
    response_model=ApplicationResponse
)
def update_status(
    application_id: int,
    status_data: StatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "recruiter":
        raise HTTPException(
            status_code=403,
            detail="Only recruiters can update application status."
        )

    application = db.query(Application).filter(
        Application.id == application_id
    ).first()

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found."
        )

    job = db.query(Job).filter(
        Job.id == application.job_id
    ).first()

    if job.recruiter_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only update applicants for your own jobs."
        )

    application.status = status_data.status

    db.commit()
    db.refresh(application)

    return application