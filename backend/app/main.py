from fastapi import FastAPI
from sqlalchemy import text

from app.routers.auth import router as auth_router
from app.models.application import Application
from app.routers.application import router as application_router

from app.database import Base, engine
from app.models.user import User
from app.models.job import Job

from app.routers.users import router as users_router
from app.routers.jobs import router as jobs_router
from app.routers.dashboard import router as dashboard_router


Base.metadata.create_all(bind=engine)

with engine.begin() as connection:
    connection.execute(
        text(
            "ALTER TABLE users "
            "ADD COLUMN IF NOT EXISTS resume_url VARCHAR"
        )
    )

app = FastAPI(
    title="Job Portal API",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(jobs_router)
app.include_router(application_router)
app.include_router(dashboard_router)

@app.get("/")
def root():
    return {
        "message": "Job Portal API Running"
    }
