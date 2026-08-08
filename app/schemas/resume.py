from datetime import datetime

from pydantic import BaseModel


class ResumeOut(BaseModel):
    id: int
    candidate_id: int
    filename: str
    size_bytes: int
    is_primary: bool
    uploaded_at: datetime
<<<<<<< HEAD

    model_config = {"from_attributes": True}
=======
<<<<<<< HEAD

    model_config = {"from_attributes": True}
=======
    url: str | None = None

    model_config = {"from_attributes": True}
>>>>>>> 7e52a1e (resume stored into aws_s3_buckets)
>>>>>>> 379ca77 (resumes stored in aws s3 bucket)
