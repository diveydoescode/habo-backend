from sqlalchemy.orm import Session
from app.models.chat import ChatMessage
from app.models.task import GigTask
from app.models.user import User
from app.schemas.chat import MessageSend
from fastapi import HTTPException


def _check_chat_access(db: Session, task_id: str, user: User) -> GigTask:
    task = db.query(GigTask).filter(GigTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status not in ("Accepted", "Completed"):
        raise HTTPException(status_code=403, detail="Chat only available after task is accepted")
    if str(user.id) not in {str(task.creator_id), str(task.accepted_by_id)}:
        raise HTTPException(status_code=403, detail="You are not a participant of this task")
    return task


def send_message(db: Session, payload: MessageSend, sender: User) -> ChatMessage:
    _check_chat_access(db, str(payload.task_id), sender)
    msg = ChatMessage(
        task_id=payload.task_id,
        sender_id=sender.id,
        ciphertext=payload.ciphertext,
        nonce=payload.nonce,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_messages(db: Session, task_id: str, user: User) -> list[ChatMessage]:
    _check_chat_access(db, task_id, user)
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.task_id == task_id)
        .order_by(ChatMessage.sent_at.asc())
        .all()
    )