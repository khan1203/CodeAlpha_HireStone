from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.employer import Employer
from app.models.candidate import Candidate
from app.schemas.auth import RegisterEmployer, RegisterCandidate, Token, LoginRequest
from app.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register/employer", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_employer(payload: RegisterEmployer, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")

    user = User(email=payload.email, hashed_password=hash_password(payload.password), role=UserRole.EMPLOYER)
    db.add(user)
    db.flush()

    employer = Employer(
        user_id=user.id,
        company_name=payload.company_name,
        company_website=payload.company_website,
        description=payload.description,
    )
    db.add(employer)
    db.commit()

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return Token(access_token=token, role=user.role)


@router.post("/register/candidate", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_candidate(payload: RegisterCandidate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")

    user = User(email=payload.email, hashed_password=hash_password(payload.password), role=UserRole.CANDIDATE)
    db.add(user)
    db.flush()

    candidate = Candidate(
        user_id=user.id,
        full_name=payload.full_name,
        phone=payload.phone,
        headline=payload.headline,
    )
    db.add(candidate)
    db.commit()

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return Token(access_token=token, role=user.role)


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account disabled")

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return Token(access_token=token, role=user.role)
