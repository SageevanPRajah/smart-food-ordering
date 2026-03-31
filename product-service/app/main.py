import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import ASCENDING

from app.db import ping_database, products_collection
from app.routes import router

app = FastAPI(
    title="Product Service",
    version="1.0.0",
    description="Manages food items and menu data for the Smart Food Ordering System.",
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
    await products_collection.create_index([("item_id", ASCENDING)], unique=True)
    await products_collection.create_index([("name", ASCENDING)])


@app.get("/", tags=["Health"])
async def root() -> dict:
    return {"service": "product-service", "status": "running", "port": 8002}


app.include_router(router)
