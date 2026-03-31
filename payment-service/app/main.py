import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import ASCENDING

from app.db import payments_collection, ping_database
from app.routes import router

app = FastAPI(
    title="Payment Service",
    version="1.0.0",
    description="Handles and validates payment records for the Smart Food Ordering System.",
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
    await payments_collection.create_index([("payment_id", ASCENDING)], unique=True)
    await payments_collection.create_index([("order_id", ASCENDING)])


@app.get("/", tags=["Health"])
async def root() -> dict:
    return {"service": "payment-service", "status": "running", "port": 8004}


app.include_router(router)
//add routing for payment operations
