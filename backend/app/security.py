from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str) -> str:
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    return _create_token(subject, expires_delta, settings.jwt_secret_key, "access")


def create_refresh_token(subject: str) -> str:
    expires_delta = timedelta(days=settings.refresh_token_expire_days)
    return _create_token(subject, expires_delta, settings.jwt_refresh_secret_key, "refresh")


def _create_token(subject: str, expires_delta: timedelta, secret: str, token_type: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    return jwt.encode(payload, secret, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    return _decode_token(token, settings.jwt_secret_key, "access")


def decode_refresh_token(token: str) -> dict:
    return _decode_token(token, settings.jwt_refresh_secret_key, "refresh")


def _decode_token(token: str, secret: str, expected_type: str) -> dict:
    payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
    if payload.get("type") != expected_type:
        raise JWTError("Invalid token type")
    return payload
