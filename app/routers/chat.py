# MARK: - routers/chat.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.chat import MessageSend, MessageResponse
from app.services.chat_service import send_message, get_messages
from app.services.auth_service import get_current_user
from app.models.user import User
from uuid import UUID

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/messages", response_model=MessageResponse, status_code=201)
def send(
    payload: MessageSend,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return send_message(db, payload, current_user)

@router.get("/messages/{task_id}", response_model=list[MessageResponse])
def history(
    task_id: UUID,  # ✅ Forces FastAPI to handle iOS Uppercase -> Lowercase conversion
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Pass the normalized UUID string to your service layer
    return get_messages(db, str(task_id), current_user)