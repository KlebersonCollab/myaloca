from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ==========================================
# Company Schemas
# ==========================================
class CompanyBase(BaseModel):
    name: str = Field(..., max_length=150)
    code: str = Field(..., max_length=50)
    cnpj: str | None = Field(None, max_length=20)
    description: str | None = Field(None, max_length=255)
    is_active: bool = True


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: str | None = Field(None, max_length=150)
    code: str | None = Field(None, max_length=50)
    cnpj: str | None = Field(None, max_length=20)
    description: str | None = Field(None, max_length=255)
    is_active: bool | None = None


class CompanyResponse(CompanyBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Building Schemas
# ==========================================
class BuildingBase(BaseModel):
    name: str = Field(..., max_length=150)
    code: str = Field(..., max_length=50)
    company_id: int | None = None
    address: str | None = Field(None, max_length=255)
    city: str | None = Field(None, max_length=100)
    total_floors: int = Field(default=1, ge=1, le=120)
    is_active: bool = True


class BuildingCreate(BuildingBase):
    pass


class BuildingUpdate(BaseModel):
    name: str | None = Field(None, max_length=150)
    code: str | None = Field(None, max_length=50)
    company_id: int | None = None
    address: str | None = Field(None, max_length=255)
    city: str | None = Field(None, max_length=100)
    total_floors: int | None = Field(None, ge=1, le=120)
    is_active: bool | None = None


class BuildingResponse(BuildingBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
