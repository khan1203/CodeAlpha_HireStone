from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_candidate, require_employer
from app.models.user import User
from app.models.candidate import Candidate
from app.models.employer import Employer
from app.models.job import JobListing, JobStatus
from app.models.resume import Resume
from app.models.application import Application
from app.schemas.application import ApplicationCreate, ApplicationOut, ApplicationStatusUpdate
from app.services.notifications import notify_employer_new_application, notify_candidate_status_change

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def apply_to_job(
    payload: ApplicationCreate,
    user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
):
    candidate = db.query(Candidate).filter(Candidate.user_id == user.id).first()
    if not candidate:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Candidate profile not found")

    job = db.query(JobListing).filter(JobListing.id == payload.job_id).first()
    if not job or job.status != JobStatus.OPEN:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found or not open")

    resume = db.query(Resume).filter(Resume.id == payload.resume_id, Resume.candidate_id == candidate.id).first()
    if not resume:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume not found")

    application = Application(
        job_id=job.id,
        candidate_id=candidate.id,
        resume_id=resume.id,
        cover_letter=payload.cover_letter,
    )
    db.add(application)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Already applied to this job")
    db.refresh(application)

    employer = db.query(Employer).filter(Employer.id == job.employer_id).first()
    if employer:
        notify_employer_new_application(employer.user.email, job.title, candidate.full_name)

    return application


@router.get("/mine", response_model=list[ApplicationOut])
def my_applications(user: User = Depends(require_candidate), db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.user_id == user.id).first()
    if not candidate:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Candidate profile not found")
    return db.query(Application).filter(Application.candidate_id == candidate.id).all()


@router.get("/job/{job_id}", response_model=list[ApplicationOut])
def applications_for_job(job_id: int, user: User = Depends(require_employer), db: Session = Depends(get_db)):
    employer = db.query(Employer).filter(Employer.user_id == user.id).first()
    if not employer:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Employer profile not found")

    job = db.query(JobListing).filter(JobListing.id == job_id).first()
    if not job or job.employer_id != employer.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not your job listing")

    return db.query(Application).filter(Application.job_id == job_id).all()


@router.patch("/{application_id}/status", response_model=ApplicationOut)
def update_status(
    application_id: int,
    payload: ApplicationStatusUpdate,
    user: User = Depends(require_employer),
    db: Session = Depends(get_db),
):
    employer = db.query(Employer).filter(Employer.user_id == user.id).first()
    if not employer:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Employer profile not found")

    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Application not found")

    job = db.query(JobListing).filter(JobListing.id == application.job_id).first()
    if job.employer_id != employer.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not your job listing")

    application.status = payload.status
    db.commit()
    db.refresh(application)

    candidate = db.query(Candidate).filter(Candidate.id == application.candidate_id).first()
    if candidate:
        notify_candidate_status_change(candidate.user.email, job.title, application.status.value)

    return application
