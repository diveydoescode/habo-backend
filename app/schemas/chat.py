# MARK: - schemas/chat.py
from pydantic import BaseModel, ConfigDict, field_serializer
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

    # ✅ Forces exact ISO8601 format (YYYY-MM-DDTHH:MM:SSZ)
    # This prevents the Swift JSONDecoder from panicking on fractional seconds.
    @field_serializer('sent_at')
    def format_datetime(self, dt: datetime, _info):
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")