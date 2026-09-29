from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    code: str | None = Field(None, max_length=50)
    description: str | None = Field(None, max_length=255)
    company_id: int | None = None
    is_active: bool = True


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100)
    code: str | None = Field(None, max_length=50)
    description: str | None = Field(None, max_length=255)
    company_id: int | None = None
    is_active: bool | None = None


class DepartmentResponse(DepartmentBase):
    id: int
    created_at: datetime
    users_count: int = 0

    model_config = ConfigDict(from_attributes=True)
