import io
import secrets
from collections.abc import Sequence

import qrcode
from qrcode.image.pil import PilImage
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.desk import Desk, Zone
from app.schemas.desk import DeskCreate, ZoneCreate


class DeskService:
    @staticmethod
    def generate_immutable_qr_hash() -> str:
        """Generates a cryptographically strong immutable 48-char hex token."""
        return secrets.token_hex(24)

    @staticmethod
    def generate_qr_image(qr_payload: str) -> bytes:
        """Generates PNG image bytes from a QR Code payload."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_payload)
        qr.make(fit=True)

        img: PilImage = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    @staticmethod
    async def create_zone(db: AsyncSession, zone_in: ZoneCreate) -> Zone:
        zone = Zone(
            name=zone_in.name,
            floor=zone_in.floor,
            description=zone_in.description,
            is_active=zone_in.is_active,
        )
        db.add(zone)
        await db.commit()
        await db.refresh(zone)
        return zone

    @staticmethod
    async def get_zones(db: AsyncSession) -> Sequence[Zone]:
        result = await db.execute(select(Zone).where(Zone.is_active.is_(True)))
        return result.scalars().all()

    @staticmethod
    async def create_desk(db: AsyncSession, desk_in: DeskCreate) -> Desk:
        qr_hash = DeskService.generate_immutable_qr_hash()
        desk = Desk(
            code=desk_in.code,
            zone_id=desk_in.zone_id,
            pos_x=desk_in.pos_x,
            pos_y=desk_in.pos_y,
            pos_z=desk_in.pos_z,
            rotation_y=desk_in.rotation_y,
            has_monitor=desk_in.has_monitor,
            has_docking_station=desk_in.has_docking_station,
            is_standing_desk=desk_in.is_standing_desk,
            qr_code_hash=qr_hash,
            status="DISPONIVEL",
        )
        db.add(desk)
        await db.commit()
        await db.refresh(desk)
        return desk

    @staticmethod
    async def get_desks_by_zone(db: AsyncSession, zone_id: int) -> Sequence[Desk]:
        result = await db.execute(select(Desk).where(Desk.zone_id == zone_id))
        return result.scalars().all()

    @staticmethod
    async def get_desk_by_id(db: AsyncSession, desk_id: int) -> Desk | None:
        result = await db.execute(select(Desk).where(Desk.id == desk_id))
        return result.scalar_one_or_none()
