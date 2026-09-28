from collections.abc import Sequence
from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models.booking import Booking
from app.models.desk import Desk
from app.schemas.booking import BookingCreate


def ensure_utc(dt: datetime) -> datetime:
    """Ensures datetime is timezone-aware in UTC across SQLite and PostgreSQL."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class BookingService:
    @staticmethod
    async def create_booking(
        db: AsyncSession,
        user_id: int,
        booking_in: BookingCreate,
    ) -> Booking:
        # Check desk existence
        desk_result = await db.execute(select(Desk).where(Desk.id == booking_in.desk_id))
        desk = desk_result.scalar_one_or_none()
        if not desk:
            raise ValueError("DESK_NOT_FOUND")

        # Collision detection: overlap with active reservations
        req_start = ensure_utc(booking_in.start_time)
        req_end = ensure_utc(booking_in.end_time)

        overlap_query = select(Booking).where(
            and_(
                Booking.desk_id == booking_in.desk_id,
                Booking.status.in_(["PENDENTE_CHECKIN", "CHECKED_IN"]),
                Booking.start_time < req_end,
                Booking.end_time > req_start,
            )
        )
        overlap_result = await db.execute(overlap_query)
        if overlap_result.scalar_one_or_none():
            raise ValueError("BOOKING_OVERLAP")

        deadline = req_start + timedelta(minutes=settings.CHECKIN_TOLERANCE_MINUTES)

        booking = Booking(
            desk_id=booking_in.desk_id,
            user_id=user_id,
            start_time=req_start,
            end_time=req_end,
            checkin_deadline=deadline,
            status="PENDENTE_CHECKIN",
            notes=booking_in.notes,
        )
        db.add(booking)
        await db.commit()
        await db.refresh(booking)
        return booking

    @staticmethod
    async def check_in(
        db: AsyncSession,
        booking_id: int,
        user_id: int,
        qr_code_hash: str,
    ) -> Booking:
        result = await db.execute(
            select(Booking).where(Booking.id == booking_id).options(selectinload(Booking.desk))
        )
        booking = result.scalar_one_or_none()
        if not booking:
            raise ValueError("BOOKING_NOT_FOUND")

        if booking.user_id != user_id:
            raise ValueError("BOOKING_FORBIDDEN")

        if booking.status != "PENDENTE_CHECKIN":
            raise ValueError(f"BOOKING_NOT_PENDING:{booking.status}")

        if not booking.desk or booking.desk.qr_code_hash != qr_code_hash:
            raise ValueError("INVALID_QR_CODE")

        now = datetime.now(timezone.utc)
        start_time = ensure_utc(booking.start_time)
        deadline = ensure_utc(booking.checkin_deadline)

        early_window = start_time - timedelta(minutes=settings.CHECKIN_EARLY_MINUTES)
        if now < early_window:
            raise ValueError("CHECKIN_TOO_EARLY")

        if now > deadline:
            raise ValueError("CHECKIN_WINDOW_EXPIRED")

        booking.status = "CHECKED_IN"
        booking.checked_in_at = now
        booking.desk.status = "OCUPADA"

        db.add(booking)
        db.add(booking.desk)
        await db.commit()
        await db.refresh(booking)
        return booking

    @staticmethod
    async def process_no_shows(db: AsyncSession) -> int:
        now = datetime.now(timezone.utc)
        query = (
            select(Booking)
            .where(Booking.status == "PENDENTE_CHECKIN")
            .options(selectinload(Booking.desk))
        )

        result = await db.execute(query)
        pending_bookings = result.scalars().all()

        expired_count = 0
        for b in pending_bookings:
            deadline = ensure_utc(b.checkin_deadline)
            if deadline <= now:
                b.status = "EXPIRADA_NO_SHOW"
                if b.desk and b.desk.status != "MANUTENCAO":
                    b.desk.status = "DISPONIVEL"
                    db.add(b.desk)
                db.add(b)
                expired_count += 1

        if expired_count > 0:
            await db.commit()
        return expired_count

    @staticmethod
    async def get_booking_by_id(db: AsyncSession, booking_id: int) -> Booking | None:
        result = await db.execute(select(Booking).where(Booking.id == booking_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_bookings(db: AsyncSession, user_id: int) -> Sequence[Booking]:
        result = await db.execute(
            select(Booking)
            .where(Booking.user_id == user_id)
            .order_by(Booking.start_time.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_active_occupancies(db: AsyncSession) -> Sequence[Booking]:
        """Returns all currently active or reserved bookings for the 3D canvas."""
        now = datetime.now(timezone.utc)
        result = await db.execute(
            select(Booking)
            .where(Booking.status.in_(["PENDENTE_CHECKIN", "CHECKED_IN"]))
            .options(selectinload(Booking.user), selectinload(Booking.desk))
        )
        all_active = result.scalars().all()

        active_now: list[Booking] = []
        for b in all_active:
            st = ensure_utc(b.start_time)
            et = ensure_utc(b.end_time)
            if st <= now + timedelta(hours=8) and et >= now:
                active_now.append(b)
        return active_now
