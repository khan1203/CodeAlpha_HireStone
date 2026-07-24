from datetime import datetime

from pydantic import BaseModel


class EmployerOut(BaseModel):
    id: int
    company_name: str
    company_website: str | None
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class EmployerUpdate(BaseModel):
    company_name: str | None = None
    company_website: str | None = None
    description: str | None = None
