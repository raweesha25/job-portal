from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_roles
from app.models.user import User
from app.schemas.user import ResumeUploadResponse, UserResumeResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

UPLOAD_DIR = Path("uploads") / "resumes"
MAX_RESUME_SIZE = 5 * 1024 * 1024
ALLOWED_RESUME_TYPE = "application/pdf"
ALLOWED_ROLES = ["admin", "recruiter", "job_seeker"]


def ensure_resume_directory():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/me")
def get_me(
    current_user: User = Depends(require_roles(ALLOWED_ROLES))
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "resume_url": current_user.resume_url
    }


@router.post(
    "/upload-resume",
    response_model=ResumeUploadResponse,
    summary="Upload current user's resume"
)
def upload_resume(
    resume: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ALLOWED_ROLES))
):
    if resume.content_type != ALLOWED_RESUME_TYPE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )

    ensure_resume_directory()

    unique_id = uuid4().hex[:8]
    filename = f"{current_user.id}_{unique_id}_resume.pdf"
    file_path = UPLOAD_DIR / filename

    total_size = 0

    try:
        with file_path.open("wb") as buffer:
            while chunk := resume.file.read(1024 * 1024):
                total_size += len(chunk)

                if total_size > MAX_RESUME_SIZE:
                    buffer.close()
                    file_path.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Resume file size must be 5 MB or less"
                    )

                buffer.write(chunk)
    finally:
        resume.file.close()

    resume_url = file_path.as_posix()
    current_user.resume_url = resume_url

    db.commit()
    db.refresh(current_user)

    return {
        "message": "Resume uploaded successfully",
        "resume_url": resume_url
    }


@router.get(
    "/me/resume",
    response_model=UserResumeResponse,
    summary="Get current user's resume path"
)
def get_current_user_resume(
    current_user: User = Depends(require_roles(ALLOWED_ROLES))
):
    return {
        "user_id": current_user.id,
        "resume_url": current_user.resume_url
    }


@router.get(
    "/{user_id}/resume",
    summary="Download a user's resume"
)
def download_resume(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ALLOWED_ROLES))
):
    if current_user.role == "job_seeker" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Job seekers can only download their own resume"
        )

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user.resume_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    resume_path = Path(user.resume_url)

    if not resume_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume file not found"
        )

    return FileResponse(
        path=resume_path,
        media_type=ALLOWED_RESUME_TYPE,
        filename=resume_path.name
    )
