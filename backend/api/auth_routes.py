"""
MockPilot AI — Auth API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.database.models import get_db, User
from backend.models.schemas import UserCreate, UserLogin, Token, UserOut
from backend.auth.jwt_handler import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/signup", response_model=Token, status_code=201)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        email=payload.email,
        username=payload.username,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": user.id})
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": user.id})
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(db: Session = Depends(get_db),
       current_user: User = Depends(lambda: None)):  # replaced at runtime
    return current_user

@router.post("/guest", response_model=Token)
def guest_login(db: Session = Depends(get_db)):
    """Auto-create or return the shared guest user — no password needed."""
    from backend.auth.jwt_handler import hash_password
    GUEST_EMAIL = "guest@mockpilot.ai"
    GUEST_USER  = "guest"
    user = db.query(User).filter(User.email == GUEST_EMAIL).first()
    if not user:
        user = User(
            email=GUEST_EMAIL,
            username=GUEST_USER,
            hashed_password=hash_password("guest-no-password"),
            full_name="Guest",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    token = create_access_token({"sub": user.id})
    return Token(access_token=token, user=UserOut.model_validate(user))
