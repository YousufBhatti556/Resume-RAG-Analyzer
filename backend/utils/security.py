from passlib.context import CryptContext

# 1. Hashing Algorithm set karo (bcrypt sabse secure hai)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Plain text password ko ek lambay ajeeb se hash mein badal deta hai.
    """
    return pwd_context.hash(password[:72])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check karta hai ke user ka diya hua password database wale hash se match hota hai ya nahi.
    """
    return pwd_context.verify(plain_password[:72], hashed_password)