from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_admin
from app.models.user import User
from app.models.employer import Employer
from app.models.candidate import Candidate
from app.models.job import JobListing, JobStatus
from app.models.application import Application, ApplicationStatus
from app.schemas.admin import ApplicationStats, UserAdminOut

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/users", response_model=list[UserAdminOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.patch("/users/{user_id}/deactivate", response_model=UserAdminOut)
def deactivate_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}/activate", response_model=UserAdminOut)
def activate_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user


@router.get("/stats", response_model=ApplicationStats)
def application_stats(db: Session = Depends(get_db)):
    total_applications = db.query(Application).count()

    status_counts = (
        db.query(Application.status, func.count(Application.id))
        .group_by(Application.status)
        .all()
    )
    by_status = {s.value: c for s, c in status_counts}
    for s in ApplicationStatus:
        by_status.setdefault(s.value, 0)

    total_jobs = db.query(JobListing).count()
    open_jobs = db.query(JobListing).filter(JobListing.status == JobStatus.OPEN).count()
    total_employers = db.query(Employer).count()
    total_candidates = db.query(Candidate).count()

    return ApplicationStats(
        total_applications=total_applications,
        by_status=by_status,
        total_jobs=total_jobs,
        open_jobs=open_jobs,
        total_employers=total_employers,
        total_candidates=total_candidates,
    )
