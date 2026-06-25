from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import base
from sqlalchemy import func

class Job(base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String)
    min_salary = Column(Integer, nullable=True)
    max_salary = Column(Integer, nullable=True)
    status = Column(String, default="open")
    recruiter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    recruiter = relationship("User", back_populates="jobs")
    applications = relationship(
    "Application",
    back_populates="job",
    cascade="all, delete-orphan"
)