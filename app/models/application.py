from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import base
from sqlalchemy import func

class Application(base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id",ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id",ondelete="CASCADE"), nullable=False)
    status = Column(String, default="Applied")
    applied_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


    candidate = relationship("Candidate", back_populates="applications")
    job = relationship("Job", back_populates="applications")
