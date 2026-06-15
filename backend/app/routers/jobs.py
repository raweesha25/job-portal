from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import Integer, cast, or_
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.core.dependencies import get_db, require_roles
from app.models.job import Job
from app.models.user import User
from app.schemas.job import JobCreate, JobUpdate, PaginatedJobsResponse

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

@router.get(
    "/",
    response_model=PaginatedJobsResponse,
    summary="Search, filter, sort, and paginate jobs"
)
def get_jobs(
    keyword: str | None = Query(
        default=None,
        description="Search keyword for job title, company, or description"
    ),
    location: str | None = Query(
        default=None,
        description="Filter jobs by location"
    ),
    salary_min: int | None = Query(
        default=None,
        ge=0,
        description="Minimum salary"
    ),
    salary_max: int | None = Query(
        default=None,
        ge=0,
        description="Maximum salary"
    ),
    sort_by: str = Query(
        default="created_at",
        description="Sort field. Allowed values: created_at, salary"
    ),
    order: str = Query(
        default="desc",
        description="Sort order. Allowed values: asc, desc"
    ),
    page: int = Query(
        default=1,
        ge=1,
        description="Page number"
    ),
    page_size: int = Query(
        default=10,
        ge=1,
        le=50,
        description="Number of jobs per page. Maximum is 50"
    ),
    db: Session = Depends(get_db)
):
    if salary_min is not None and salary_max is not None:
        if salary_min > salary_max:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="salary_min cannot be greater than salary_max"
            )

    if sort_by not in ["created_at", "salary"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sort_by must be either 'created_at' or 'salary'"
        )

    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="order must be either 'asc' or 'desc'"
        )

    query = db.query(Job)
    salary_value = cast(Job.salary, Integer)

    if keyword:
        keyword_filter = f"%{keyword}%"
        query = query.filter(
            or_(
                Job.title.ilike(keyword_filter),
                Job.company.ilike(keyword_filter),
                Job.description.ilike(keyword_filter)
            )
        )

    if location:
        query = query.filter(
            Job.location.ilike(f"%{location}%")
        )

    if salary_min is not None:
        query = query.filter(
            salary_value >= salary_min
        )

    if salary_max is not None:
        query = query.filter(
            salary_value <= salary_max
        )

    total = query.count()

    if sort_by == "salary":
        sort_column = salary_value
    else:
        sort_column = Job.created_at

    if order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    jobs = (
        query
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": jobs
    }

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
