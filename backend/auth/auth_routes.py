from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, constr
from backend.database.deps import get_db
from backend.database.models import User
from backend.utils.security import hash_password, verify_password
from backend.auth.jwt_handler import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

# Pydantic schemas
class UserSignup(BaseModel):
    email: EmailStr
    # Enforce reasonable length without bcrypt's 72-byte limit
    password: constr(min_length=8, max_length=128)

class UserLogin(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=128)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Signup route
@router.post("/signup", response_model=TokenResponse)
def signup(user: UserSignup, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        email=user.email,
        password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"user_id": new_user.id})
    return {"access_token": token}

# Login route
@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    print(f"Logging in user: {user.email}") # Debug print
    
    db_user = db.query(User).filter(User.email == user.email).first()
    
    if not db_user:
        print("User not found in DB") # Debug print
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Yahan check karo password verification phat toh nahi rahi
    try:
        is_valid = verify_password(user.password, db_user.password)
    except Exception as e:
        print(f"Hashing error: {e}")
        raise HTTPException(status_code=500, detail="Password verification failed")

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"user_id": db_user.id})
    return {"access_token": token}