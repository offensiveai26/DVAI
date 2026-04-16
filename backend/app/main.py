from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import challenges, progress, health, openai_compat
from app.labs import airline
from app.db import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="DVAI", description="Damn Vulnerable AI - Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(openai_compat.router, tags=["openai-compat"])
app.include_router(challenges.router, prefix="/api/challenges", tags=["challenges"])
app.include_router(progress.router, prefix="/api/progress", tags=["progress"])
app.include_router(airline.router, prefix="/api/labs/airline", tags=["labs"])
