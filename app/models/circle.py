# MARK: - models/circle.py
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
from app.database import Base

class Circle(Base):
    __tablename__ = "circles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    totp_secret = Column(String, nullable=False) # Stores the Base32 secret for TOTP math
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    admin = relationship("User", foreign_keys=[admin_id])
    members = relationship("CircleMember", back_populates="circle", cascade="all, delete-orphan")
    tasks = relationship("GigTask", back_populates="circle")

class CircleMember(Base):
    __tablename__ = "circle_members"
    
    circle_id = Column(UUID(as_uuid=True), ForeignKey("circles.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role = Column(String, default="member") # 'admin' or 'member'
    joined_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    circle = relationship("Circle", back_populates="members")
    user = relationship("User")






