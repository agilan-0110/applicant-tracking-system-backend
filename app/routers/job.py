from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.application import Application
from app.database import get_db
from app.models.job import Job
from app.models.user import User
from app.schemas.job import JobCreate, JobResponse,JobUpdate,RecruiterJobResponse
from app.auth.oauth2 import get_current_user
from sqlalchemy import func


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)

@router.post(
    "/",
    response_model=JobResponse,
    summary="Create Job",
    description="Allows recruiters to create a new job posting."
)
def create_job(
    job: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only recruiters can create jobs
    if current_user.role != "recruiter":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can create jobs."
        )

    new_job = Job(
        title=job.title,
        description=job.description,
        location=job.location,
        min_salary=job.min_salary,
        max_salary=job.max_salary,
        recruiter_id=current_user.id
)

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job



@router.get(
    "/my",
    response_model=list[RecruiterJobResponse],
    summary="My Jobs",
    description="Returns all jobs posted by the logged-in recruiter with applicant counts."
)
def my_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "recruiter":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can access this endpoint."
        )

    jobs = (
        db.query(
            Job.id,
            Job.title,
            Job.location,
            Job.min_salary,
            Job.max_salary,
            Job.status,
            func.count(Application.id).label("applicant_count")
        )
        .outerjoin(Application, Job.id == Application.job_id)
        .filter(Job.recruiter_id == current_user.id)
        .group_by(
            Job.id,
            Job.title,
            Job.location,
            Job.min_salary,
            Job.max_salary,
            Job.status
        )
        .all()
    )

    return jobs

@router.get(
    "/{job_id}",
    response_model=JobResponse,
    summary="Get Job",
    description="Retrieve a specific job using its ID."
)
def get_job(job_id : int,db:Session = Depends(get_db),current_user: User = Depends(get_current_user)):

    job = db.query(Job).filter(Job.id == job_id).first()

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    return job
@router.put(
    "/{job_id}",
    response_model=JobResponse,
    summary="Update Job",
    description="Update an existing job. Only the recruiter who created the job can update it."
)
def update_job(
    job_id: int,
    job_data: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Find the job
    job = db.query(Job).filter(Job.id == job_id).first()

    # Check if job exists
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Only recruiters can update jobs
    if current_user.role != "recruiter":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can update jobs."
        )

    # Recruiter can update only their own jobs
    if job.recruiter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own jobs."
        )

    # Update fields
    job.title = job_data.title
    job.description = job_data.description
    job.location = job_data.location
    job.min_salary = job_data.min_salary
    job.max_salary = job_data.max_salary


    db.commit()
    db.refresh(job)

    return job


@router.delete(
    "/{job_id}",
    summary="Delete Job",
    description="Delete a job posting. Only the recruiter who created the job can delete it."
)
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Find the job
    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    # Check if job exists
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Only recruiters can delete jobs
    if current_user.role != "recruiter":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can delete jobs."
        )

    # Recruiter can only delete their own jobs
    if job.recruiter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own jobs."
        )

    db.delete(job)
    db.commit()

    return {
        "message": "Job deleted successfully"
    }


