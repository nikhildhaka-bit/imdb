import secrets
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Response
from sqlalchemy.orm import Session

from config import settings
from models import RefreshToken

ACCESS_COOKIE = "access_token"
REFRESH_COOKIE = "refresh_token"
CSRF_COOKIE = "csrf_token"
REFRESH_COOKIE_PATH = "/api/v1/auth/refresh"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def _encode(payload: dict, ttl: timedelta) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode({**payload, "iat": now, "exp": now + ttl}, settings.jwt_secret, algorithm="HS256")


def create_access_token(user_id: str) -> str:
    return _encode({"sub": user_id, "type": "access"}, timedelta(minutes=settings.access_token_ttl_minutes))


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])


def issue_refresh_token(db: Session, user_id: str) -> str:
    jti = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_ttl_days)
    db.add(RefreshToken(jti=jti, user_id=user_id, expires_at=expires_at))
    db.commit()
    return _encode({"sub": user_id, "type": "refresh", "jti": jti}, timedelta(days=settings.refresh_token_ttl_days))


def set_auth_cookies(response: Response, db: Session, user_id: str) -> None:
    access_token = create_access_token(user_id)
    refresh_token = issue_refresh_token(db, user_id)
    csrf_token = secrets.token_urlsafe(32)

    response.set_cookie(
        ACCESS_COOKIE, access_token, httponly=True, secure=settings.cookie_secure, samesite="lax",
        max_age=settings.access_token_ttl_minutes * 60, path="/",
    )
    response.set_cookie(
        REFRESH_COOKIE, refresh_token, httponly=True, secure=settings.cookie_secure, samesite="lax",
        max_age=settings.refresh_token_ttl_days * 24 * 3600, path=REFRESH_COOKIE_PATH,
    )
    # readable by JS on purpose — double-submit CSRF pattern relies on it not being httpOnly
    response.set_cookie(
        CSRF_COOKIE, csrf_token, httponly=False, secure=settings.cookie_secure, samesite="lax",
        max_age=settings.refresh_token_ttl_days * 24 * 3600, path="/",
    )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(ACCESS_COOKIE, path="/")
    response.delete_cookie(REFRESH_COOKIE, path=REFRESH_COOKIE_PATH)
    response.delete_cookie(CSRF_COOKIE, path="/")
