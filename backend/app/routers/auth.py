from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from jose import JWTError
from sqlalchemy import func
from sqlmodel import Session, select

from app.config import settings
from app.db import get_session
from app.deps import get_current_user
from app.models import User
from app.schemas import MessageResponse, UserCreate, UserLogin, UserRead
from app.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _resolved_cookie_domain() -> str | None:
    domain = (settings.cookie_domain or "").strip()
    if not domain:
        return None

    normalized = domain.lstrip(".").lower()
    if normalized in {"localhost", "127.0.0.1", "::1", "testserver"}:
        # Local/test hosts should use host-only cookies (no explicit domain attr).
        return None

    return domain


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    cookie_domain = _resolved_cookie_domain()
    common = {
        "httponly": True,
        "secure": settings.cookie_secure,
        "samesite": "none" if settings.cookie_secure else "lax",
        "path": "/",
    }
    if cookie_domain:
        common["domain"] = cookie_domain

    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=settings.access_token_expire_minutes * 60,
        **common,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        **common,
    )


def _clear_auth_cookies(response: Response) -> None:
    cookie_domain = _resolved_cookie_domain()
    if cookie_domain:
        response.delete_cookie("access_token", domain=cookie_domain, path="/")
        response.delete_cookie("refresh_token", domain=cookie_domain, path="/")

    # Also clear host-only cookies to avoid stale values in local/test clients.
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate, session: Session = Depends(get_session)) -> User:
    normalized_email = str(payload.email).lower()
    existing = session.exec(select(User).where(func.lower(User.email) == normalized_email)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(name=payload.name, email=normalized_email, password_hash=hash_password(payload.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login", response_model=UserRead)
def login(payload: UserLogin, response: Response, session: Session = Depends(get_session)) -> User:
    normalized_email = str(payload.email).lower()
    user = session.exec(select(User).where(func.lower(User.email) == normalized_email)).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access = create_access_token(str(user.id))
    refresh = create_refresh_token(str(user.id))
    _set_auth_cookies(response, access, refresh)
    return user


@router.post("/refresh", response_model=MessageResponse)
def refresh_token(request: Request, response: Response, session: Session = Depends(get_session)):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")

    try:
        payload = decode_refresh_token(refresh_token)
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    _set_auth_cookies(response, create_access_token(str(user.id)), create_refresh_token(str(user.id)))
    return MessageResponse(message="Token refreshed")


@router.post("/logout", response_model=MessageResponse)
def logout(response: Response) -> MessageResponse:
    _clear_auth_cookies(response)
    return MessageResponse(message="Logged out")


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
