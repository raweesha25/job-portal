from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.dependencies import get_db, require_roles
from app.models.application import Application
from app.models.job import Job
from app.models.user import User
from app.schemas.application import ApplicationResponse

router = APIRouter(
    prefix="/applications",
    tags=["Applications"]
)


@router.post("/{user_id}/{job_id}")
def apply_job(
    user_id: int,
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["job_seeker"]))
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot apply for another user"
        )

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    existing_application = (
        db.query(Application)
        .filter(
            Application.user_id == user_id,
            Application.job_id == job_id
        )
        .first()
    )

    if existing_application:
        raise HTTPException(
            status_code=400,
            detail="Already applied to this job"
        )

    application = Application(
        user_id=user_id,
        job_id=job_id
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return {
        "message": "Applied successfully",
        "application_id": application.id
    }


@router.get("/", response_model=list[ApplicationResponse])
def get_all_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "recruiter"]))
):
    applications = (
        db.query(Application)
        .options(
            joinedload(Application.user),
            joinedload(Application.job)
        )
        .all()
    )

    return applications


@router.get("/user/{user_id}", response_model=list[ApplicationResponse])
def get_user_applications(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(["admin", "recruiter", "job_seeker"])
    )
):
    if current_user.role == "job_seeker" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Job seekers can only view their own applications"
        )

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    applications = (
        db.query(Application)
        .options(
            joinedload(Application.user),
            joinedload(Application.job)
        )
        .filter(
            Application.user_id == user_id
        )
        .all()
    )

    return applications
