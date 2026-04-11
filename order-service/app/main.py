import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import ASCENDING

from app.db import orders_collection, ping_database
from app.routes import router

app = FastAPI(
    title="Order Service",
    version="1.0.0",
    description="Creates and tracks food orders for the Smart Food Ordering System.",
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
    await orders_collection.create_index([("order_id", ASCENDING)], unique=True)
    await orders_collection.create_index([("user_id", ASCENDING)])
    await orders_collection.create_index([("order_date", ASCENDING)])


@app.get("/", tags=["Health"])
async def root() -> dict:
    return {"service": "order-service", "status": "running", "port": 8003}


app.include_router(router)
