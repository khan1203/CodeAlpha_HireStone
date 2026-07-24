from datetime import datetime

from pydantic import BaseModel


class CandidateOut(BaseModel):
    id: int
    full_name: str
    phone: str | None
    headline: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CandidateUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    headline: str | None = None
