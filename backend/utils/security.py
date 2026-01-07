from passlib.context import CryptContext

# Use pbkdf2_sha256 which is stable and pure-Python (no external bcrypt backend needed)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plain text password using a secure one-way algorithm.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that a plain text password matches the stored hash.
    """
    return pwd_context.verify(plain_password, hashed_password)