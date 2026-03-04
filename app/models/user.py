from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB  # ✅ Added JSONB import
from datetime import datetime, timezone
import uuid
from app.database import Base

followers_table = Table(
    "followers",
    Base.metadata,
    Column("follower_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column("following_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    avatar_url = Column(String, nullable=True)
    public_key = Column(String, nullable=True)
    rating = Column(Float, default=5.0)
    tasks_posted = Column(Integer, default=0)
    tasks_completed = Column(Integer, default=0)
    member_since = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    skills = Column(JSONB, default=list)  # ✅ Added skills column

    tasks = relationship("GigTask", back_populates="creator", foreign_keys="GigTask.creator_id")
    accepted_tasks = relationship("GigTask", back_populates="acceptor", foreign_keys="GigTask.accepted_by_id")

    following = relationship(
        "User",
        secondary=followers_table,
        primaryjoin=id == followers_table.c.follower_id,
        secondaryjoin=id == followers_table.c.following_id,
        backref="followers",
        lazy="dynamic",
    )