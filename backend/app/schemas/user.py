from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str = "colaborador"
    avatar_url: str | None = None
    photo_url: str | None = None
    job_title: str | None = None
    department: str | None = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: str | None = None
    avatar_url: str | None = None
    photo_url: str | None = None
    job_title: str | None = None
    department: str | None = None
    password: str | None = None


class AdminUserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: str = "colaborador"
    avatar_url: str | None = None
    photo_url: str | None = None
    job_title: str | None = None
    department: str | None = None
    is_active: bool = True


class AdminUserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    role: str | None = None
    avatar_url: str | None = None
    photo_url: str | None = None
    job_title: str | None = None
    department: str | None = None
    is_active: bool | None = None
    password: str | None = None



class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str | None = None
