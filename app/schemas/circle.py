# MARK: - schemas/circle.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID

class CircleCreate(BaseModel):
    name: str

class CircleJoinRequest(BaseModel):
    invite_code: str # The 45-second TOTP code

class CircleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    admin_id: UUID
    created_at: datetime

class InviteCodeResponse(BaseModel):
    code: str
    expires_in_seconds: int # Tells the frontend exactly how much time is left on the pie chart