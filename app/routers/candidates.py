from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_candidate
from app.models.user import User
from app.models.candidate import Candidate
from app.schemas.candidate import CandidateOut, CandidateUpdate

router = APIRouter(prefix="/candidates", tags=["candidates"])


def _get_candidate_or_404(db: Session, user_id: int) -> Candidate:
    candidate = db.query(Candidate).filter(Candidate.user_id == user_id).first()
    if not candidate:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Candidate profile not found")
    return candidate


@router.get("/me", response_model=CandidateOut)
def get_my_profile(user: User = Depends(require_candidate), db: Session = Depends(get_db)):
    return _get_candidate_or_404(db, user.id)


@router.patch("/me", response_model=CandidateOut)
def update_my_profile(
    payload: CandidateUpdate,
    user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
):
    candidate = _get_candidate_or_404(db, user.id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(candidate, field, value)
    db.commit()
    db.refresh(candidate)
    return candidate
