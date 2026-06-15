from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.dependencies import get_db, require_roles
from app.models.application import Application
from app.models.job import Job
from app.models.user import User
from app.schemas.dashboard import (
    AdminDashboardResponse,
    JobSeekerDashboardResponse,
    RecruiterDashboardResponse,
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get(
    "/job-seeker",
    response_model=JobSeekerDashboardResponse,
    summary="Get job seeker dashboard"
)
def get_job_seeker_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["job_seeker"]))
):
    applications = (
        db.query(Application)
        .options(joinedload(Application.job))
        .filter(Application.user_id == current_user.id)
        .all()
    )

    applied_jobs = [
        {
            "id": application.job.id,
            "title": application.job.title,
            "company": application.job.company,
            "applied_at": application.applied_at
        }
        for application in applications
    ]

    return {
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email
        },
        "applications_count": len(applications),
        "applied_jobs": applied_jobs
    }


@router.get(
    "/recruiter",
    response_model=RecruiterDashboardResponse,
    summary="Get recruiter dashboard"
)
def get_recruiter_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["recruiter", "admin"]))
):
    total_jobs_posted = db.query(Job).count()
    total_applications = db.query(Application).count()

    jobs = (
        db.query(
            Job.id,
            Job.title,
            func.count(Application.id).label("applications_count")
        )
        .outerjoin(Application, Application.job_id == Job.id)
        .group_by(Job.id, Job.title)
        .all()
    )

    return {
        "total_jobs_posted": total_jobs_posted,
        "total_applications": total_applications,
        "jobs": [
            {
                "id": job.id,
                "title": job.title,
                "applications_count": job.applications_count
            }
            for job in jobs
        ]
    }


@router.get(
    "/admin",
    response_model=AdminDashboardResponse,
    summary="Get admin dashboard"
)
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    total_users = db.query(User).count()
    total_jobs = db.query(Job).count()
    total_applications = db.query(Application).count()

    role_counts = (
        db.query(
            User.role,
            func.count(User.id).label("count")
        )
        .group_by(User.role)
        .all()
    )

    users_by_role = {
        "job_seeker": 0,
        "recruiter": 0,
        "admin": 0
    }

    for role_count in role_counts:
        users_by_role[role_count.role] = role_count.count

    return {
        "total_users": total_users,
        "total_jobs": total_jobs,
        "total_applications": total_applications,
        "users_by_role": users_by_role
    }
