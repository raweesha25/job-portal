from pydantic import BaseModel


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
