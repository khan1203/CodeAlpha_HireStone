from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_employer
from app.models.user import User
from app.models.employer import Employer
from app.schemas.employer import EmployerOut, EmployerUpdate

router = APIRouter(prefix="/employers", tags=["employers"])


def _get_employer_or_404(db: Session, user_id: int) -> Employer:
    employer = db.query(Employer).filter(Employer.user_id == user_id).first()
    if not employer:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Employer profile not found")
    return employer


@router.get("/me", response_model=EmployerOut)
def get_my_profile(user: User = Depends(require_employer), db: Session = Depends(get_db)):
    return _get_employer_or_404(db, user.id)


@router.patch("/me", response_model=EmployerOut)
def update_my_profile(
    payload: EmployerUpdate,
    user: User = Depends(require_employer),
    db: Session = Depends(get_db),
):
    employer = _get_employer_or_404(db, user.id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(employer, field, value)
    db.commit()
    db.refresh(employer)
    return employer


@router.get("/{employer_id}", response_model=EmployerOut)
def get_employer_public(employer_id: int, db: Session = Depends(get_db)):
    employer = db.query(Employer).filter(Employer.id == employer_id).first()
    if not employer:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Employer not found")
    return employer
