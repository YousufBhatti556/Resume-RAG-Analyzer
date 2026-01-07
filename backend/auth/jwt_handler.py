import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from dotenv import load_dotenv

load_dotenv()

# Configuration - .env file mein ye values honi chahiye
SECRET_KEY = os.getenv("JWT_SECRET") 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # Token 24 ghante tak valid rahega

def create_access_token(data: dict):
    """
    User ID aur expiration time mila kar ek encrypted token banata hai.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str):
    """
    Token ko check karta hai ke wo asli hai ya expire toh nahi ho gaya.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload if payload.get("user_id") else None
    except JWTError:
        return None