from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker


DATABASE_URL = "postgresql://postgres:password@localhost:5432/ats_db"


engine = create_engine(DATABASE_URL)

SessionLocal=sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine
)

base=declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
