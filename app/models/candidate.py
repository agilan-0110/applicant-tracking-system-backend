from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import base
from sqlalchemy import func

class Candidate(base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    phone = Column(String)
    skills = Column(Text)
    experience_years = Column(Integer)
    education = Column(String)
    

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    user = relationship("User", back_populates="candidate")
    applications = relationship(
    "Application",
    back_populates="candidate",
    cascade="all, delete-orphan"
)
