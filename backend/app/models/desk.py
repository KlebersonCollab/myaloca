from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.building import Building


class Zone(Base):
    __tablename__ = "zones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    building_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("buildings.id"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    floor: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    building: Mapped["Building | None"] = relationship("Building", back_populates="zones")
    desks: Mapped[list["Desk"]] = relationship(
        "Desk", back_populates="zone", cascade="all, delete-orphan"
    )


class Desk(Base):
    __tablename__ = "desks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    zone_id: Mapped[int] = mapped_column(Integer, ForeignKey("zones.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="DISPONIVEL", nullable=False)

    # 3D spatial coordinates and rotation
    pos_x: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    pos_y: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    pos_z: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rotation_y: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Equipment flags
    has_monitor: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_docking_station: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_standing_desk: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Space Type & Booking Policies
    space_type: Mapped[str] = mapped_column(String(30), default="BAIA", nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    required_role: Mapped[str | None] = mapped_column(String(30), nullable=True, default=None)
    max_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)

    # Immutable QR Code verification hash
    qr_code_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    zone: Mapped[Zone] = relationship("Zone", back_populates="desks")
