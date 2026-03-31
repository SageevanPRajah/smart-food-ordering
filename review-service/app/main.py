import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import ASCENDING

from app.db import ping_database, reviews_collection
from app.routes import router

app = FastAPI(
    title="Review Service",
    version="1.0.0",
    description="Collects product reviews and ratings for the Smart Food Ordering System.",
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
    await reviews_collection.create_index([("review_id", ASCENDING)], unique=True)
    await reviews_collection.create_index([("item_id", ASCENDING)])
    await reviews_collection.create_index([("user_id", ASCENDING)])


@app.get("/", tags=["Health"])
async def root() -> dict:
    return {"service": "review-service", "status": "running", "port": 8005}


app.include_router(router)
