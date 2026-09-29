from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.desk import Zone


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    cnpj: Mapped[str | None] = mapped_column(String(20), nullable=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    buildings: Mapped[list["Building"]] = relationship(
        "Building", back_populates="company", cascade="all, delete-orphan"
    )


class Building(Base):
    __tablename__ = "buildings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("companies.id"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    total_floors: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    company: Mapped[Company | None] = relationship("Company", back_populates="buildings")
    zones: Mapped[list["Zone"]] = relationship(
        "Zone", back_populates="building", cascade="all, delete-orphan"
    )
