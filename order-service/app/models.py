from datetime import datetime, timezone
from typing import Optional, Literal

from pydantic import BaseModel, Field, model_validator


class OrderItem(BaseModel):
    item_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=2, max_length=100)
    price: float = Field(..., gt=0)
    quantity: int = Field(..., ge=1)
    subtotal: Optional[float] = None

    @model_validator(mode="after")
    def calculate_subtotal(self):
        self.subtotal = round(self.price * self.quantity, 2)
        return self


class OrderCreate(BaseModel):
    user_id: str = Field(..., min_length=1)
    items: list[OrderItem] = Field(..., min_length=1)


class OrderStatusUpdate(BaseModel):
    status: Literal["Pending", "Processing", "Completed", "Cancelled"]


class OrderResponse(BaseModel):
    order_id: str
    user_id: str
    order_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    items: list[OrderItem]
    total: float
    status: Literal["Pending", "Processing", "Completed", "Cancelled"]
