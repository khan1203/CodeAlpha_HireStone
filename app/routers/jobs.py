from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_employer
from app.models.user import User
from app.models.employer import Employer
from app.models.job import JobListing, JobType, JobStatus
from app.schemas.job import JobCreate, JobUpdate, JobOut, Paginated

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _employer_for_user(db: Session, user: User) -> Employer:
    employer = db.query(Employer).filter(Employer.user_id == user.id).first()
    if not employer:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Employer profile not found")
    return employer


@router.post("", response_model=JobOut, status_code=status.HTTP_201_CREATED)
def post_job(
    payload: JobCreate,
    user: User = Depends(require_employer),
    db: Session = Depends(get_db),
):
    employer = _employer_for_user(db, user)
    job = JobListing(employer_id=employer.id, **payload.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("/search", response_model=Paginated)
def search_jobs(
    q: str | None = None,
    location: str | None = None,
    job_type: JobType | None = None,
    remote: bool | None = None,
    salary_min: int | None = None,
    salary_max: int | None = None,
    employer_id: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(JobListing).filter(JobListing.status == JobStatus.OPEN)

    if q:
        like = f"%{q}%"
        query = query.filter(or_(JobListing.title.ilike(like), JobListing.description.ilike(like)))
    if location:
        query = query.filter(JobListing.location.ilike(f"%{location}%"))
    if job_type:
        query = query.filter(JobListing.job_type == job_type)
    if remote is not None:
        query = query.filter(JobListing.remote == remote)
    if salary_min is not None:
        query = query.filter(JobListing.salary_max >= salary_min)
    if salary_max is not None:
        query = query.filter(JobListing.salary_min <= salary_max)
    if employer_id:
        query = query.filter(JobListing.employer_id == employer_id)

    total = query.count()
    items = (
        query.order_by(JobListing.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return Paginated(total=total, page=page, page_size=page_size, items=items)


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(JobListing).filter(JobListing.id == job_id).first()
    if not job:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
    return job


@router.patch("/{job_id}", response_model=JobOut)
def update_job(
    job_id: int,
    payload: JobUpdate,
    user: User = Depends(require_employer),
    db: Session = Depends(get_db),
):
    employer = _employer_for_user(db, user)
    job = db.query(JobListing).filter(JobListing.id == job_id).first()
    if not job:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
    if job.employer_id != employer.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not your job listing")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(job, field, value)
    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    user: User = Depends(require_employer),
    db: Session = Depends(get_db),
):
    employer = _employer_for_user(db, user)
    job = db.query(JobListing).filter(JobListing.id == job_id).first()
    if not job:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
    if job.employer_id != employer.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not your job listing")
    db.delete(job)
    db.commit()
