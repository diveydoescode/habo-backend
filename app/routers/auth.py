from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.schemas.user import GoogleLoginRequest, AuthResponse, UserMe
from app.services.auth_service import (
    verify_google_token, get_or_create_user,
    create_access_token, get_current_user,
)
from app.models.user import User, followers_table

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_follower_count(db: Session, user_id) -> int:
    return db.query(func.count()).select_from(followers_table).filter(
        followers_table.c.following_id == user_id
    ).scalar() or 0


def get_following_count(db: Session, user_id) -> int:
    return db.query(func.count()).select_from(followers_table).filter(
        followers_table.c.follower_id == user_id
    ).scalar() or 0


@router.post("/login", response_model=AuthResponse)
async def google_login(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    google_data = await verify_google_token(payload.id_token)
    email = google_data.get("email")
    name = google_data.get("name", email.split("@")[0])
    avatar_url = google_data.get("picture")

    user = get_or_create_user(db, email, name, avatar_url, payload.public_key)
    token = create_access_token(str(user.id))

    return AuthResponse(
        access_token=token,
        user=UserMe(
            id=user.id,
            name=user.name,
            email=user.email,
            avatar_url=user.avatar_url,
            rating=user.rating,
            tasks_posted=user.tasks_posted,
            tasks_completed=user.tasks_completed,
            member_since=user.member_since,
            public_key=user.public_key,
            follower_count=get_follower_count(db, user.id),
            following_count=get_following_count(db, user.id),
        ),
    )


@router.get("/me", response_model=UserMe)
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
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
    )