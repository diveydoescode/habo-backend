from pydantic import BaseModel
from uuid import UUID


class CreateOrderRequest(BaseModel):
    task_id: UUID
    amount_paise: int


class CreateOrderResponse(BaseModel):
    razorpay_order_id: str
    amount_paise: int
    currency: str = "INR"
    key_id: str