from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JobCreate(BaseModel):
    title: str
    company: str
    location: str
    salary: str
    description: str


class JobUpdate(BaseModel):
    title: str
    company: str
    location: str
    salary: str
    description: str


class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    location: str
    salary: str | None
    description: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedJobsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[JobResponse]
