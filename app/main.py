from fastapi import FastAPI
from app.database import base, engine
from app.routers import auth
from app.routers import job
from app.routers import candidate
from app.routers import application

from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

origins = [
    "https://www.google.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(job.router)
app.include_router(candidate.router)
app.include_router(application.router)



@app.get("/")
def home():
    return {"message": "ATS API Running"}