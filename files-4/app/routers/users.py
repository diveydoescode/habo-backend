from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserSearchResult, FollowResponse, UserProfileResponse
from app.services.user_service import search_users, follow_user, unfollow_user, get_user_profile
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/search", response_model=list[UserSearchResult])
def search(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fuzzy name search using PostgreSQL pg_trgm."""
    return search_users(db, q, str(current_user.id))


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
