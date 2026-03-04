from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserSearchResult, FollowResponse, UserProfileResponse, ProfileUpdateRequest, UserMe
from app.services.user_service import search_users, follow_user, unfollow_user, get_user_profile
from app.services.auth_service import get_current_user
from app.models.user import User
from app.routers.auth import get_follower_count, get_following_count

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/search", response_model=list[UserSearchResult])
def search(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fuzzy name search using PostgreSQL pg_trgm."""
    return search_users(db, q, str(current_user.id))


# ✅ NEW: PUT /me endpoint MUST be placed before /{user_id}
@router.put("/me", response_model=UserMe)
def update_profile(
    request: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Update the SQLAlchemy model
    current_user.name = request.name
    
    # 2. Convert Pydantic models to dictionaries for the JSONB column
    current_user.skills = [skill.model_dump() for skill in request.skills]
    
    # 3. Commit to database
    try:
        db.commit()
        db.refresh(current_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update profile")

    # 4. Return the updated user (matching the UserMe schema expected by iOS)
    return UserMe(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        avatar_url=current_user.avatar_url,
        rating=current_user.rating,
        tasks_posted=current_user.tasks_posted,
        tasks_completed=current_user.tasks_completed,
        member_since=current_user.member_since,
        public_key=current_user.public_key,
        follower_count=get_follower_count(db, current_user.id),
        following_count=get_following_count(db, current_user.id),
        skills=current_user.skills
    )


@router.get("/{user_id}", response_model=UserProfileResponse)
def get_profile(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_profile(db, user_id, str(current_user.id))


@router.post("/{user_id}/follow", response_model=FollowResponse)
def follow(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return follow_user(db, current_user, user_id)


@router.delete("/{user_id}/follow", response_model=FollowResponse)
def unfollow(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return unfollow_user(db, current_user, user_id)