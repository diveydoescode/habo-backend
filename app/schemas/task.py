# MARK: - schemas/task.py
from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from uuid import UUID

class TaskCreate(BaseModel):
    title: str
    category: str
    description: str
    budget: int
    is_negotiable: bool = False
    latitude: float
    longitude: float
    radius_metres: int = 10000

    @field_validator("budget")
    @classmethod
    def budget_positive(cls, v):
        if v <= 0:
            raise ValueError("Budget must be greater than 0")
        return v

class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    category: str
    description: str
    budget: int
    is_negotiable: bool
    latitude: float
    longitude: float
    radius_metres: int
    status: str
    
    # ✅ Exposing the code to the frontend
    completion_code: str | None = None 
    
    created_at: datetime
    creator_name: str
    creator_id: UUID
    accepted_by_id: UUID | None = None

class TaskAcceptResponse(BaseModel):
    task_id: UUID
    accepted_by: str
    status: str
    chat_unlocked: bool = True
    completion_code: str # ✅ Added this so Swift gets it instantly upon accepting