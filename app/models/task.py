# MARK: - models/task.py
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from datetime import datetime, timezone
import uuid
from app.database import Base

class GigTask(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String, nullable=False)
    budget = Column(Integer, nullable=False)
    is_negotiable = Column(Boolean, default=False)
    location = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    radius_metres = Column(Integer, default=10000)
    status = Column(String, default="Active")
    
    # ✅ Added the 6-digit completion code column
    completion_code = Column(String(6), nullable=True) 
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    accepted_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    creator = relationship("User", back_populates="tasks", foreign_keys=[creator_id])
    acceptor = relationship("User", back_populates="accepted_tasks", foreign_keys=[accepted_by_id])
    messages = relationship("ChatMessage", back_populates="task", cascade="all, delete-orphan")