from typing import Literal

from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    order_id: str = Field(..., min_length=1)
    method: Literal["Cash on Delivery"] = "Cash on Delivery"
    amount: float = Field(..., gt=0)


class PaymentStatusUpdate(BaseModel):
    status: Literal["Pending", "Validated", "Failed", "Paid"]


class PaymentResponse(BaseModel):
    payment_id: str
    order_id: str
    method: Literal["Cash on Delivery"]
    status: Literal["Pending", "Validated", "Failed", "Paid"]
    amount: float
