from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ApplicationUserResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class ApplicationJobResponse(BaseModel):
    id: int
    title: str

    model_config = ConfigDict(from_attributes=True)


class ApplicationResponse(BaseModel):
    id: int
    user: ApplicationUserResponse
    job: ApplicationJobResponse
    applied_at: datetime

    model_config = ConfigDict(from_attributes=True)
