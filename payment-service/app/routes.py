from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.db import payments_collection
from app.models import PaymentCreate, PaymentResponse, PaymentStatusUpdate

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(payload: PaymentCreate) -> PaymentResponse:
    document = {
        "payment_id": str(uuid4()),
        "order_id": payload.order_id,
        "method": payload.method,
        "status": "Pending",
        "amount": round(payload.amount, 2),
    }
    await payments_collection.insert_one(document)
    return PaymentResponse(**document)


@router.get("", response_model=list[PaymentResponse])
async def list_payments() -> list[PaymentResponse]:
    payments = await payments_collection.find({}, {"_id": 0}).to_list(length=None)
    return [PaymentResponse(**payment) for payment in payments]


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: str) -> PaymentResponse:
    payment = await payments_collection.find_one({"payment_id": payment_id}, {"_id": 0})
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found.")
    return PaymentResponse(**payment)


@router.get("/order/{order_id}", response_model=list[PaymentResponse])
async def get_payment_by_order(order_id: str) -> list[PaymentResponse]:
    payments = await payments_collection.find({"order_id": order_id}, {"_id": 0}).to_list(length=None)
    return [PaymentResponse(**payment) for payment in payments]


@router.post("/{payment_id}/validate", response_model=PaymentResponse)
async def validate_payment(payment_id: str) -> PaymentResponse:
    result = await payments_collection.update_one({"payment_id": payment_id}, {"$set": {"status": "Validated"}})
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found.")

    payment = await payments_collection.find_one({"payment_id": payment_id}, {"_id": 0})
    return PaymentResponse(**payment)


@router.patch("/{payment_id}/status", response_model=PaymentResponse)
async def update_payment_status(payment_id: str, payload: PaymentStatusUpdate) -> PaymentResponse:
    result = await payments_collection.update_one({"payment_id": payment_id}, {"$set": {"status": payload.status}})
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found.")

    payment = await payments_collection.find_one({"payment_id": payment_id}, {"_id": 0})
    return PaymentResponse(**payment)


@router.delete("/{payment_id}")
async def delete_payment(payment_id: str) -> dict:
    result = await payments_collection.delete_one({"payment_id": payment_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found.")
    return {"message": "Payment deleted successfully."}
