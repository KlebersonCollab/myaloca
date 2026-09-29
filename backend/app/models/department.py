from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.building import Company
    from app.models.user import User


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("companies.id"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    code: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    company: Mapped["Company | None"] = relationship("Company", backref="departments")
    users: Mapped[list["User"]] = relationship("User", back_populates="department_rel")
