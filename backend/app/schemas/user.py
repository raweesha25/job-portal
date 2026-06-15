from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ResumeUploadResponse(BaseModel):
    message: str
    resume_url: str


class UserResumeResponse(BaseModel):
    user_id: int
    resume_url: str | None
