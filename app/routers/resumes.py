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
from app.services.storage import upload_file_to_s3, delete_file_from_s3, get_presigned_url

router = APIRouter(prefix="/resumes", tags=["resumes"])

ALLOWED_EXT = {".pdf", ".doc", ".docx"}
CONTENT_TYPES = {
    ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def _candidate_for_user(db: Session, user: User) -> Candidate:
    candidate = db.query(Candidate).filter(Candidate.user_id == user.id).first()
    if not candidate:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Candidate profile not found")
    return candidate


def _attach_url(resume: Resume) -> Resume:
    resume.url = get_presigned_url(resume.s3_key)
    return resume


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

    s3_key = f"resumes/{candidate.id}/{uuid.uuid4().hex}{ext}"
    upload_file_to_s3(contents, s3_key, content_type=CONTENT_TYPES.get(ext, "application/octet-stream"))

    is_first = db.query(Resume).filter(Resume.candidate_id == candidate.id).count() == 0

    resume = Resume(
        candidate_id=candidate.id,
        filename=file.filename,
        s3_key=s3_key,
        size_bytes=len(contents),
        is_primary=is_first,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return _attach_url(resume)


@router.get("", response_model=list[ResumeOut])
def list_my_resumes(user: User = Depends(require_candidate), db: Session = Depends(get_db)):
    candidate = _candidate_for_user(db, user)
    resumes = db.query(Resume).filter(Resume.candidate_id == candidate.id).all()
    return [_attach_url(r) for r in resumes]


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
    return _attach_url(resume)


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(resume_id: int, user: User = Depends(require_candidate), db: Session = Depends(get_db)):
    candidate = _candidate_for_user(db, user)
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.candidate_id == candidate.id).first()
    if not resume:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume not found")

    delete_file_from_s3(resume.s3_key)
    db.delete(resume)
    db.commit()