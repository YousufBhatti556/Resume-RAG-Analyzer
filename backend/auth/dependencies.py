from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from backend.auth.jwt_handler import ALGORITHM, _ensure_secret
from backend.database.deps import get_db
from backend.database.models import User

# Ye line batati hai ke token kahan se uthana hai (Login route se)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Token ko decode karo
        secret = _ensure_secret()
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Database mein check karo ke user hai ya nahi
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user