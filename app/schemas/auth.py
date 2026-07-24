from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class RegisterEmployer(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    company_name: str
    company_website: str | None = None
    description: str | None = None


class RegisterCandidate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str
    phone: str | None = None
    headline: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole


class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}
