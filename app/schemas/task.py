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
    
    # ✅ NEW: Support for private circles and applications
    circle_id: UUID | None = None
    requires_application: bool = False

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
    completion_code: str | None = None 
    
    # ✅ NEW fields
    circle_id: UUID | None = None
    requires_application: bool = False
    
    created_at: datetime
    creator_name: str
    creator_id: UUID
    accepted_by_id: UUID | None = None

class TaskAcceptResponse(BaseModel):
    task_id: UUID
    accepted_by: str
    status: str
    chat_unlocked: bool = True
    completion_code: str 


# ✅ NEW: Application Schemas
class TaskApplicationCreate(BaseModel):
    cover_message: str | None = None

class TaskApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    task_id: UUID
    applicant_id: UUID
    status: str
    cover_message: str | None = None
    applied_at: datetime
    # We will likely want to include applicant details (name, rating, skills) when returning lists