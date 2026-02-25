from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User, followers_table
from fastapi import HTTPException


def search_users(db: Session, query: str, current_user_id: str, limit: int = 20) -> list[dict]:
    """Fuzzy search using PostgreSQL pg_trgm similarity scoring."""
    if len(query) < 2:
        return []

    results = (
        db.query(User, func.similarity(User.name, query).label("sim"))
        .filter(User.id != current_user_id)
        .filter(func.similarity(User.name, query) > 0.1)
        .order_by(func.similarity(User.name, query).desc())
        .limit(limit)
        .all()
    )

    output = []
    for user, sim in results:
        follower_count = db.query(followers_table).filter(
            followers_table.c.following_id == user.id
        ).count()
        output.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "avatar_url": user.avatar_url,
            "rating": user.rating,
            "follower_count": follower_count,
        })
    return output


def follow_user(db: Session, current_user: User, target_id: str) -> dict:
    target = db.query(User).filter(User.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if str(current_user.id) == target_id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    if current_user.following.filter(User.id == target_id).first():
        raise HTTPException(status_code=400, detail="Already following")
    current_user.following.append(target)
    db.commit()
    return {"following": True, "follower_count": target.followers.count()}


def unfollow_user(db: Session, current_user: User, target_id: str) -> dict:
    target = db.query(User).filter(User.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    followed = current_user.following.filter(User.id == target_id).first()
    if not followed:
        raise HTTPException(status_code=400, detail="Not following this user")
    current_user.following.remove(target)
    db.commit()
    return {"following": False, "follower_count": target.followers.count()}


def get_user_profile(db: Session, user_id: str, current_user_id: str) -> dict:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    current = db.query(User).filter(User.id == current_user_id).first()
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "avatar_url": user.avatar_url,
        "rating": user.rating,
        "tasks_posted": user.tasks_posted,
        "tasks_completed": user.tasks_completed,
        "member_since": user.member_since,
        "public_key": user.public_key,
        "follower_count": user.followers.count(),
        "following_count": user.following.count(),
        "is_following": current.following.filter(User.id == user_id).first() is not None,
    }
