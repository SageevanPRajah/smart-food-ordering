import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import ASCENDING

from app.db import ping_database, users_collection
from app.routes import router

app = FastAPI(
    title="User Service",
    version="1.0.0",
    description="Manages user registration, login, and profile operations for the Smart Food Ordering System.",
)

allowed_origins = os.getenv("ALLOWED_ORIGINS").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()] or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    await ping_database()
    await users_collection.create_index([("email", ASCENDING)], unique=True)
    await users_collection.create_index([("user_id", ASCENDING)], unique=True)


@app.get("/", tags=["Health"])
async def root() -> dict:
    return {"service": "user-service", "status": "running", "port": 8001}


app.include_router(router)
