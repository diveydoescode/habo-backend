from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from uuid import UUID

# ✅ NEW: Skill schema
class UserSkill(BaseModel):
    name: str
    proficiency: int

# ✅ NEW: Profile update request schema
class ProfileUpdateRequest(BaseModel):
    name: str
    skills: list[UserSkill]

class UserBase(BaseModel):
    name: str
    email: EmailStr
    avatar_url: str | None = None

class UserPublic(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    rating: float
    tasks_posted: int
    tasks_completed: int
    member_since: datetime
    public_key: str | None = None
    follower_count: int = 0
    following_count: int = 0
    skills: list[UserSkill] | None = []  # ✅ Added skills

class UserMe(UserPublic):
    pass

class GoogleLoginRequest(BaseModel):
    id_token: str
    public_key: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserMe

class FollowResponse(BaseModel):
    following: bool
    follower_count: int

class UserSearchResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: EmailStr
    avatar_url: str | None = None
    rating: float
    follower_count: int = 0

class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: EmailStr
    avatar_url: str | None = None
    rating: float
    tasks_posted: int
    tasks_completed: int
    member_since: datetime
    public_key: str | None = None
    follower_count: int = 0
    following_count: int = 0
    is_following: bool = False
    skills: list[UserSkill] | None = []  # ✅ Added skills