from fastapi import FastAPI
from app.routers.auth import router as auth_router
from app.models.application import Application
from app.routers.application import router as application_router

from app.database import Base, engine
from app.models.user import User
from app.models.job import Job

from app.routers.users import router as users_router
from app.routers.jobs import router as jobs_router


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Job Portal API",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(jobs_router)
app.include_router(application_router)

@app.get("/")
def root():
    return {
        "message": "Job Portal API Running"
    }