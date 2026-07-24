from datetime import datetime

from pydantic import BaseModel

from app.models.application import ApplicationStatus


class ApplicationCreate(BaseModel):
    job_id: int
    resume_id: int
    cover_letter: str | None = None


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus


class ApplicationOut(BaseModel):
    id: int
    job_id: int
    candidate_id: int
    resume_id: int | None
    cover_letter: str | None
    status: ApplicationStatus
    applied_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
