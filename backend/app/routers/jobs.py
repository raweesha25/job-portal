from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.core.dependencies import get_db, require_roles
from app.models.job import Job
from app.models.user import User
from app.schemas.job import JobCreate, JobUpdate

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


@router.post("/")
def create_job(
    job: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["recruiter", "admin"]))
):
    new_job = Job(
        title=job.title,
        company=job.company,
        location=job.location,
        salary=job.salary,
        description=job.description
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return {
        "message": "Job created successfully",
        "job_id": new_job.id
    }

@router.get("/")
def get_jobs(
    db: Session = Depends(get_db)
):
    jobs = db.query(Job).all()

    return jobs

@router.get("/{job_id}")
def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job


@router.put("/{job_id}")
def update_job(
    job_id: int,
    job_data: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["recruiter", "admin"]))
):
    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    job.title = job_data.title
    job.company = job_data.company
    job.location = job_data.location
    job.salary = job_data.salary
    job.description = job_data.description

    db.commit()
    db.refresh(job)

    return {
        "message": "Job updated successfully",
        "job": job
    }


@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["recruiter", "admin"]))
):
    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    db.delete(job)
    db.commit()

    return {
        "message": "Job deleted successfully"
    }
