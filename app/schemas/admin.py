from pydantic import BaseModel


class ApplicationStats(BaseModel):
    total_applications: int
    by_status: dict[str, int]
    total_jobs: int
    open_jobs: int
    total_employers: int
    total_candidates: int


class UserAdminOut(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}
