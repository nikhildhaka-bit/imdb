import logging
from datetime import datetime, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from auth.schemas import LoginIn, RegisterIn, UserOut
from auth.security import (
    REFRESH_COOKIE,
    clear_auth_cookies,
    decode_token,
    hash_password,
    set_auth_cookies,
    verify_password,
)
from database import get_db
from models import RefreshToken, User

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)


def _mask_email(email: str) -> str:
    """Never write raw emails to logs (PII) — keep just enough to spot patterns while debugging."""
    local, _, domain = email.partition("@")
    return f"{local[:2]}***@{domain}"


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterIn, response: Response, db: Session = Depends(get_db)):
    email = payload.email.lower()
    if db.query(User).filter(User.email == email).first():
        logger.warning(f"Registration rejected — email already in use: {_mask_email(email)}")
        raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email already exists")

    user = User(email=email, password_hash=hash_password(payload.password), display_name=payload.display_name)
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info(f"New user registered: user_id={user.id}")
    set_auth_cookies(response, db, user.id)
    return user


@router.post("/login", response_model=UserOut)
def login(payload: LoginIn, response: Response, db: Session = Depends(get_db)):
    email = payload.email.lower()
    user = db.query(User).filter(User.email == email).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        logger.warning(f"Failed login attempt for {_mask_email(email)}")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")

    logger.info(f"User {user.id} logged in")
    set_auth_cookies(response, db, user.id)
    return user


@router.post("/refresh", status_code=status.HTTP_204_NO_CONTENT)
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get(REFRESH_COOKIE)
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "No refresh token")

    try:
        payload = decode_token(token)
    except jwt.PyJWTError:
        clear_auth_cookies(response)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired refresh token")

    if payload.get("type") != "refresh":
        clear_auth_cookies(response)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token type")

    stored = db.get(RefreshToken, payload["jti"])
    now = datetime.now(timezone.utc)
    is_reused = stored is None or stored.revoked_at is not None or stored.expires_at.replace(tzinfo=timezone.utc) < now
    if is_reused:
        # Replay of an already-rotated (or unknown/expired) refresh token — revoke the whole chain.
        logger.warning(f"Refresh token reuse/expiry detected (jti={payload.get('jti')}) — revoking token chain")
        if stored is not None:
            db.query(RefreshToken).filter(RefreshToken.user_id == stored.user_id, RefreshToken.revoked_at.is_(None)).update(
                {"revoked_at": now}
            )
            db.commit()
        clear_auth_cookies(response)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token invalid or already used")

    stored.revoked_at = now
    db.commit()

    logger.debug(f"Rotated refresh token for user {payload['sub']}")
    set_auth_cookies(response, db, payload["sub"])


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get(REFRESH_COOKIE)
    if token:
        try:
            payload = decode_token(token)
            stored = db.get(RefreshToken, payload.get("jti"))
            if stored is not None:
                stored.revoked_at = datetime.now(timezone.utc)
                db.commit()
                logger.info(f"User {payload.get('sub')} logged out")
        except jwt.PyJWTError:
            logger.debug("Logout called with an already-invalid refresh token — clearing cookies anyway")
    clear_auth_cookies(response)
