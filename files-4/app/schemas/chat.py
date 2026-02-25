from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID


class MessageSend(BaseModel):
    task_id: UUID
    ciphertext: str
    nonce: str


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    task_id: UUID
    sender_id: UUID
    ciphertext: str
    nonce: str
    sent_at: datetime