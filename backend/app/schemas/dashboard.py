from datetime import datetime

from pydantic import BaseModel


class DashboardUserResponse(BaseModel):
    id: int
    name: str
    email: str


class AppliedJobResponse(BaseModel):
    id: int
    title: str
    company: str
    applied_at: datetime


class JobSeekerDashboardResponse(BaseModel):
    user: DashboardUserResponse
    applications_count: int
    applied_jobs: list[AppliedJobResponse]


class RecruiterDashboardJobResponse(BaseModel):
    id: int
    title: str
    applications_count: int


class RecruiterDashboardResponse(BaseModel):
    total_jobs_posted: int
    total_applications: int
    jobs: list[RecruiterDashboardJobResponse]


class AdminDashboardResponse(BaseModel):
    total_users: int
    total_jobs: int
    total_applications: int
    users_by_role: dict[str, int]
