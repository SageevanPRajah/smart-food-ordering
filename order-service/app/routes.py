from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.db import orders_collection
from app.models import OrderCreate, OrderResponse, OrderStatusUpdate

router = APIRouter(prefix="/orders", tags=["Orders"])


def serialize_order(document: dict) -> dict:
    return {
        "order_id": document["order_id"],
        "user_id": document["user_id"],
        "order_date": document["order_date"],
        "items": document["items"],
        "total": document["total"],
        "status": document["status"],
    }


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(payload: OrderCreate) -> OrderResponse:
    if not payload.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order must contain at least one item.")

    items = [item.model_dump() for item in payload.items]
    total = round(sum(item["subtotal"] for item in items), 2)

    document = {
        "order_id": str(uuid4()),
        "user_id": payload.user_id,
        "order_date": datetime.now(timezone.utc),
        "items": items,
        "total": total,
        "status": "Pending",
    }

    await orders_collection.insert_one(document)
    return OrderResponse(**serialize_order(document))


@router.get("", response_model=list[OrderResponse])
async def list_orders() -> list[OrderResponse]:
    orders = await orders_collection.find({}, {"_id": 0}).sort("order_date", -1).to_list(length=None)
    return [OrderResponse(**order) for order in orders]


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str) -> OrderResponse:
    order = await orders_collection.find_one({"order_id": order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")
    return OrderResponse(**order)


@router.get("/user/{user_id}", response_model=list[OrderResponse])
async def get_orders_by_user(user_id: str) -> list[OrderResponse]:
    orders = await orders_collection.find({"user_id": user_id}, {"_id": 0}).sort("order_date", -1).to_list(length=None)
    return [OrderResponse(**order) for order in orders]


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(order_id: str, payload: OrderStatusUpdate) -> OrderResponse:
    result = await orders_collection.update_one({"order_id": order_id}, {"$set": {"status": payload.status}})
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")

    updated_order = await orders_collection.find_one({"order_id": order_id}, {"_id": 0})
    return OrderResponse(**updated_order)


@router.delete("/{order_id}")
async def delete_order(order_id: str) -> dict:
    result = await orders_collection.delete_one({"order_id": order_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")
    return {"message": "Order deleted successfully."}
