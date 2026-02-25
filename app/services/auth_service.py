from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.config import get_settings
import httpx

settings = get_settings()
bearer_scheme = HTTPBearer()

ALGORITHM = "HS256"
TOKEN_EXPIRE_DAYS = 30
GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"


def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=TOKEN_EXPIRE_DAYS)
    return jwt.encode(
        {"sub": user_id, "exp": expire},
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )


async def verify_google_token(id_token: str) -> dict:
    """Verify Google ID token using Google's public endpoint."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(GOOGLE_TOKENINFO_URL, params={"id_token": id_token})
    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid Google ID token")
    data = resp.json()
    if "error" in data:
        raise HTTPException(status_code=401, detail=data.get("error_description", "Token error"))
    return data


def get_or_create_user(db: Session, email: str, name: str, avatar_url: str | None, public_key: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.public_key = public_key   # Refresh key on every login (supports key rotation)
        db.commit()
        db.refresh(user)
        return user
    user = User(name=name, email=email, avatar_url=avatar_url, public_key=public_key)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expired or invalid")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
