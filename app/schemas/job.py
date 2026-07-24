from datetime import datetime

from pydantic import BaseModel, Field

from app.models.job import JobType, JobStatus


class JobCreate(BaseModel):
    title: str
    description: str
    location: str | None = None
    remote: bool = False
    job_type: JobType = JobType.FULL_TIME
    salary_min: int | None = None
    salary_max: int | None = None
    expires_at: datetime | None = None


class JobUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    location: str | None = None
    remote: bool | None = None
    job_type: JobType | None = None
    status: JobStatus | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    expires_at: datetime | None = None


class JobOut(BaseModel):
    id: int
    employer_id: int
    title: str
    description: str
    location: str | None
    remote: bool
    job_type: JobType
    status: JobStatus
    salary_min: int | None
    salary_max: int | None
    created_at: datetime
    expires_at: datetime | None

    model_config = {"from_attributes": True}


class JobSearchParams(BaseModel):
    q: str | None = None
    location: str | None = None
    job_type: JobType | None = None
    remote: bool | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    employer_id: int | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class Paginated(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[JobOut]
