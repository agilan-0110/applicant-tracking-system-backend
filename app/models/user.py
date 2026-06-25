from sqlalchemy import Column,Integer,String,DateTime
from sqlalchemy.orm import relationship
from app.database import base
from sqlalchemy.sql import func

class User(base):
    __tablename__ = 'users'

    id = Column(Integer,primary_key=True,index=True)
    name = Column(String,nullable=False)
    email = Column(String,unique=True,nullable=False)
    password_hashed = Column(String,nullable=False)
    role = Column(String,nullable=False)
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    candidate = relationship("Candidate", back_populates="user", uselist=False)
    jobs = relationship("Job", back_populates="recruiter")
