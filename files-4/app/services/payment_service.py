import razorpay
from app.config import get_settings
from fastapi import HTTPException

settings = get_settings()

_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def create_razorpay_order(amount_paise: int, task_id: str) -> dict:
    if amount_paise < 100:
        raise HTTPException(status_code=400, detail="Minimum payment is ₹1")
    try:
        order = _client.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "receipt": f"habo_{str(task_id)[:8]}",
            "payment_capture": 1,
        })
        return {
            "razorpay_order_id": order["id"],
            "amount_paise": order["amount"],
            "currency": order["currency"],
            "key_id": settings.RAZORPAY_KEY_ID,
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Razorpay error: {str(e)}")
