import jwt
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from auth.security import ACCESS_COOKIE, CSRF_COOKIE, decode_token
from database import get_db
from models import User


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get(ACCESS_COOKIE)
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    try:
        payload = decode_token(token)
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
    if payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token type")

    user = db.get(User, payload["sub"])
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    return user


def get_optional_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    try:
        return get_current_user(request, db)
    except HTTPException:
        return None


def require_csrf(request: Request) -> None:
    """Double-submit CSRF check for cookie-authenticated mutations (D3)."""
    cookie_value = request.cookies.get(CSRF_COOKIE)
    header_value = request.headers.get("X-CSRF-Token")
    if not cookie_value or not header_value or cookie_value != header_value:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "CSRF token missing or invalid")
