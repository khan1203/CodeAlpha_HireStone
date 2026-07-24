import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.deps import require_candidate
from app.models.user import User
from app.models.candidate import Candidate
from app.models.resume import Resume
from app.schemas.resume import ResumeOut

router = APIRouter(prefix="/resumes", tags=["resumes"])

ALLOWED_EXT = {".pdf", ".doc", ".docx"}


def _candidate_for_user(db: Session, user: User) -> Candidate:
    candidate = db.query(Candidate).filter(Candidate.user_id == user.id).first()
    if not candidate:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Candidate profile not found")
    return candidate


@router.post("", response_model=ResumeOut, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
):
    candidate = _candidate_for_user(db, user)

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Unsupported file type '{ext}'. Allowed: {sorted(ALLOWED_EXT)}")

    contents = await file.read()
    max_bytes = settings.max_resume_size_mb * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"File exceeds {settings.max_resume_size_mb}MB limit")

    os.makedirs(settings.upload_dir, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(settings.upload_dir, stored_name)
    with open(filepath, "wb") as f:
        f.write(contents)

    is_first = db.query(Resume).filter(Resume.candidate_id == candidate.id).count() == 0

    resume = Resume(
        candidate_id=candidate.id,
        filename=file.filename,
        filepath=filepath,
        size_bytes=len(contents),
        is_primary=is_first,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


@router.get("", response_model=list[ResumeOut])
def list_my_resumes(user: User = Depends(require_candidate), db: Session = Depends(get_db)):
    candidate = _candidate_for_user(db, user)
    return db.query(Resume).filter(Resume.candidate_id == candidate.id).all()


@router.patch("/{resume_id}/primary", response_model=ResumeOut)
def set_primary(resume_id: int, user: User = Depends(require_candidate), db: Session = Depends(get_db)):
    candidate = _candidate_for_user(db, user)
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.candidate_id == candidate.id).first()
    if not resume:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume not found")

    db.query(Resume).filter(Resume.candidate_id == candidate.id).update({"is_primary": False})
    resume.is_primary = True
    db.commit()
    db.refresh(resume)
    return resume


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(resume_id: int, user: User = Depends(require_candidate), db: Session = Depends(get_db)):
    candidate = _candidate_for_user(db, user)
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.candidate_id == candidate.id).first()
    if not resume:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume not found")

    if os.path.exists(resume.filepath):
        os.remove(resume.filepath)
    db.delete(resume)
    db.commit()
