from datetime import datetime

from pydantic import BaseModel


class ResumeOut(BaseModel):
    id: int
    candidate_id: int
    filename: str
    size_bytes: int
    is_primary: bool
    uploaded_at: datetime

    model_config = {"from_attributes": True}
