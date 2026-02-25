from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.payment import CreateOrderRequest, CreateOrderResponse
from app.services.payment_service import create_razorpay_order
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/create-order", response_model=CreateOrderResponse)
def create_order(
    payload: CreateOrderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Creates a Razorpay test-mode order.
    iOS app uses the returned order_id to open the Razorpay payment sheet.
    Supports UPI App Intent and QR code flows.
    """
    return create_razorpay_order(payload.amount_paise, str(payload.task_id))
