from datetime import datetime, timedelta

from jose import JWTError, jwt

from backend.config import get_settings

ALGORITHM = "HS256"


def _ensure_secret() -> str:
    """
    Read the JWT secret from settings every time, so it always reflects the
    current environment / .env configuration.
    """
    settings = get_settings()
    secret = settings.jwt_secret
    # Only fail if it's empty / missing; default in Settings is your real key
    if not secret:
        raise RuntimeError(
            "JWT secret is not set. Define JWT_SECRET in your environment or .env file."
        )
    return secret


def create_access_token(data: dict):
    """
    Create a signed JWT containing the provided payload.
    """
    to_encode = data.copy()
    settings = get_settings()
    expire = datetime.utcnow() + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, _ensure_secret(), algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str):
    """
    Verify token signature and expiry. Returns payload or None.
    """
    try:
        payload = jwt.decode(token, _ensure_secret(), algorithms=[ALGORITHM])
        return payload if payload.get("user_id") else None
    except JWTError:
        return None