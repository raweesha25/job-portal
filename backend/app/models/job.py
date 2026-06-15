from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)

    company = Column(String, nullable=False)

    location = Column(String, nullable=False)

    salary = Column(String)

    description = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    applications = relationship(
        "Application",
        back_populates="job"
    )
