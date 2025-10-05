from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.storage.model import User

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fake_users_db = {}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserSignup(BaseModel):
    email: str
    password: str
    phone: Optional[str] = None
    age: Optional[int] = None
    height_cm: Optional[float] = None
    blood_group: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# OTP removed: no longer generating or validating one-time codes

@router.post("/signup", status_code=201)
def signup(user: UserSignup, db: Session = Depends(get_db)):
    # check existing
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    # create new user (no OTP)
    new_user = User(
        email=user.email,
        password_hash=hash_password(user.password),
        phone=user.phone,
        age=user.age,
        height_cm=user.height_cm,
        blood_group=user.blood_group,
        is_verified=1,
        otp_code=None,
        otp_expires=None
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully.", "id": new_user.id, "email": new_user.email}

# OTP routes removed

# Resend OTP route removed

@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.email == user.email).first()
    if not u or not verify_password(user.password, u.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": u.email})
    return {"access_token": token}

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
security = HTTPBearer()

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")
    u = db.query(User).filter(User.email == email).first()
    if not u:
        raise HTTPException(status_code=401, detail="Invalid token")
    return u

class UserProfileOut(BaseModel):
    id: int
    email: str
    phone: Optional[str] = None
    age: Optional[int] = None
    height_cm: Optional[float] = None
    blood_group: Optional[str] = None

@router.get("/me", response_model=UserProfileOut)
def me(current: User = Depends(get_current_user)):
    return UserProfileOut(
        id=current.id,
        email=current.email,
        phone=current.phone,
        age=current.age,
        height_cm=current.height_cm,
        blood_group=current.blood_group,
    )
