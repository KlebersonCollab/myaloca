import io
import secrets
from collections.abc import Sequence
from datetime import datetime, timezone

import qrcode
from qrcode.image.pil import PilImage
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking
from app.models.desk import Desk, Zone
from app.schemas.desk import DeskCreate, DeskUpdate, ZoneCreate, ZoneUpdate


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
            building_id=zone_in.building_id,
            description=zone_in.description,
            grid_cols=zone_in.grid_cols,
            grid_rows=zone_in.grid_rows,
            is_active=zone_in.is_active,
        )
        db.add(zone)
        await db.commit()
        await db.refresh(zone)
        return zone

    @staticmethod
    async def get_zones(
        db: AsyncSession,
        floor: int | None = None,
        building_id: int | None = None,
    ) -> Sequence[Zone]:
        query = select(Zone).where(Zone.is_active.is_(True))
        if floor is not None:
            query = query.where(Zone.floor == floor)
        if building_id is not None:
            query = query.where(Zone.building_id == building_id)
        result = await db.execute(query.order_by(Zone.floor, Zone.name))
        return result.scalars().all()

    @staticmethod
    async def get_zone_by_id(db: AsyncSession, zone_id: int) -> Zone | None:
        result = await db.execute(select(Zone).where(Zone.id == zone_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_zone(db: AsyncSession, zone_id: int, zone_in: ZoneUpdate) -> Zone:
        zone = await DeskService.get_zone_by_id(db, zone_id)
        if not zone:
            raise ValueError("ZONE_NOT_FOUND")

        update_data = zone_in.model_dump(exclude_unset=True)
        if "name" in update_data and update_data["name"] != zone.name:
            existing = (
                await db.execute(select(Zone).where(Zone.name == update_data["name"]))
            ).scalar_one_or_none()
            if existing:
                raise ValueError("ZONE_NAME_EXISTS")

        old_cols = zone.grid_cols or 6
        old_rows = zone.grid_rows or 4
        new_cols = update_data.get("grid_cols", old_cols)
        new_rows = update_data.get("grid_rows", old_rows)
        grid_changed = (new_cols != old_cols) or (new_rows != old_rows)

        for field, val in update_data.items():
            setattr(zone, field, val)

        if grid_changed:
            q_desks = select(Desk).where(Desk.zone_id == zone_id)
            desks = (await db.execute(q_desks)).scalars().all()

            occupied_cells: set[tuple[int, int]] = set()
            for d in desks:
                # 1. Reverse-engineer logical (col, row) in the old grid
                old_c = round((d.pos_x / 2.4) + (old_cols - 1) / 2)
                old_r = round((d.pos_z / 2.4) + (old_rows - 1) / 2)

                # 2. Clamp into bounds of new grid
                target_c = max(0, min(new_cols - 1, old_c))
                target_r = max(0, min(new_rows - 1, old_r))

                # 3. Collision resolution: if cell is already occupied, find nearest free cell
                if (target_r, target_c) in occupied_cells:
                    best_cell = None
                    min_dist = float("inf")
                    for r in range(new_rows):
                        for c in range(new_cols):
                            if (r, c) not in occupied_cells:
                                dist = (r - old_r) ** 2 + (c - old_c) ** 2
                                if dist < min_dist:
                                    min_dist = dist
                                    best_cell = (r, c)
                    if best_cell:
                        target_r, target_c = best_cell

                occupied_cells.add((target_r, target_c))

                # 4. Re-calculate new centered coordinates for the new grid
                d.pos_x = round((target_c - (new_cols - 1) / 2) * 2.4, 2)
                d.pos_z = round((target_r - (new_rows - 1) / 2) * 2.4, 2)
                db.add(d)

        db.add(zone)
        await db.commit()
        await db.refresh(zone)
        return zone

    @staticmethod
    async def delete_zone(db: AsyncSession, zone_id: int) -> None:
        zone = await DeskService.get_zone_by_id(db, zone_id)
        if not zone:
            raise ValueError("ZONE_NOT_FOUND")

        # Check if zone has desks
        q_desks = select(Desk).where(Desk.zone_id == zone_id).limit(1)
        has_desks = (await db.execute(q_desks)).scalar_one_or_none()
        if has_desks:
            raise ValueError("ZONE_HAS_DESKS")

        await db.delete(zone)
        await db.commit()

    @staticmethod
    async def create_desk(db: AsyncSession, desk_in: DeskCreate) -> Desk:
        qr_hash = DeskService.generate_immutable_qr_hash()
        monitors_count = (
            desk_in.monitors_count
            if desk_in.monitors_count is not None
            else (1 if desk_in.has_monitor else 0)
        )
        has_monitor = monitors_count > 0
        desk = Desk(
            code=desk_in.code,
            zone_id=desk_in.zone_id,
            pos_x=desk_in.pos_x,
            pos_y=desk_in.pos_y,
            pos_z=desk_in.pos_z,
            rotation_y=desk_in.rotation_y,
            has_monitor=has_monitor,
            monitors_count=monitors_count,
            has_docking_station=desk_in.has_docking_station,
            is_standing_desk=desk_in.is_standing_desk,
            extra_equipment=desk_in.extra_equipment,
            space_type=desk_in.space_type,
            capacity=desk_in.capacity,
            required_role=desk_in.required_role,
            max_duration_minutes=desk_in.max_duration_minutes,
            qr_code_hash=qr_hash,
            status="DISPONIVEL",
        )
        db.add(desk)
        await db.commit()
        await db.refresh(desk)
        return desk

    @staticmethod
    async def create_desks_batch(db: AsyncSession, desks_in: list[DeskCreate]) -> list[Desk]:
        created_desks: list[Desk] = []
        for desk_in in desks_in:
            qr_hash = DeskService.generate_immutable_qr_hash()
            monitors_count = (
                desk_in.monitors_count
                if desk_in.monitors_count is not None
                else (1 if desk_in.has_monitor else 0)
            )
            has_monitor = monitors_count > 0
            desk = Desk(
                code=desk_in.code,
                zone_id=desk_in.zone_id,
                pos_x=desk_in.pos_x,
                pos_y=desk_in.pos_y,
                pos_z=desk_in.pos_z,
                rotation_y=desk_in.rotation_y,
                has_monitor=has_monitor,
                monitors_count=monitors_count,
                has_docking_station=desk_in.has_docking_station,
                is_standing_desk=desk_in.is_standing_desk,
                extra_equipment=desk_in.extra_equipment,
                space_type=desk_in.space_type,
                capacity=desk_in.capacity,
                required_role=desk_in.required_role,
                max_duration_minutes=desk_in.max_duration_minutes,
                qr_code_hash=qr_hash,
                status="DISPONIVEL",
            )
            db.add(desk)
            created_desks.append(desk)

        await db.commit()
        for d in created_desks:
            await db.refresh(d)
        return created_desks

    @staticmethod
    async def get_desks_by_zone(db: AsyncSession, zone_id: int) -> Sequence[Desk]:
        result = await db.execute(select(Desk).where(Desk.zone_id == zone_id))
        return result.scalars().all()

    @staticmethod
    async def get_desk_by_id(db: AsyncSession, desk_id: int) -> Desk | None:
        result = await db.execute(select(Desk).where(Desk.id == desk_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_desk(db: AsyncSession, desk_id: int, desk_in: DeskUpdate) -> Desk:
        desk = await DeskService.get_desk_by_id(db, desk_id)
        if not desk:
            raise ValueError("DESK_NOT_FOUND")

        update_data = desk_in.model_dump(exclude_unset=True)
        if "code" in update_data and update_data["code"] != desk.code:
            existing = (
                await db.execute(select(Desk).where(Desk.code == update_data["code"]))
            ).scalar_one_or_none()
            if existing:
                raise ValueError("DESK_CODE_EXISTS")

        for field, val in update_data.items():
            setattr(desk, field, val)

        if "monitors_count" in update_data and "has_monitor" not in update_data:
            desk.has_monitor = desk.monitors_count > 0
        elif "has_monitor" in update_data and "monitors_count" not in update_data:
            if not desk.has_monitor:
                desk.monitors_count = 0
            elif desk.monitors_count == 0:
                desk.monitors_count = 1

        db.add(desk)
        await db.commit()
        await db.refresh(desk)
        return desk

    @staticmethod
    async def delete_desk(db: AsyncSession, desk_id: int) -> None:
        desk = await DeskService.get_desk_by_id(db, desk_id)
        if not desk:
            raise ValueError("DESK_NOT_FOUND")

        # Check for active bookings
        active_statuses = ["PENDENTE_CHECKIN", "CHECKED_IN"]
        q_active = (
            select(Booking)
            .where(Booking.desk_id == desk_id, Booking.status.in_(active_statuses))
            .limit(1)
        )
        has_active = (await db.execute(q_active)).scalar_one_or_none()
        if has_active:
            raise ValueError("ACTIVE_BOOKINGS_EXIST")

        # Delete past or non-active bookings related to this desk
        await db.execute(delete(Booking).where(Booking.desk_id == desk_id))

        # Delete desk
        await db.delete(desk)
        await db.commit()

    @staticmethod
    async def release_desk(db: AsyncSession, desk_id: int) -> Desk:
        desk = await DeskService.get_desk_by_id(db, desk_id)
        if not desk:
            raise ValueError("DESK_NOT_FOUND")

        now = datetime.now(timezone.utc)
        active_statuses = ["PENDENTE_CHECKIN", "CHECKED_IN"]
        q_active = select(Booking).where(
            Booking.desk_id == desk_id,
            Booking.status.in_(active_statuses),
        )
        res = await db.execute(q_active)
        active_bookings = res.scalars().all()

        for b in active_bookings:
            if b.status == "CHECKED_IN":
                if b.end_time.tzinfo is None:
                    b_end = b.end_time.replace(tzinfo=timezone.utc)
                else:
                    b_end = b.end_time.astimezone(timezone.utc)

                if b.start_time.tzinfo is None:
                    b_start = b.start_time.replace(tzinfo=timezone.utc)
                else:
                    b_start = b.start_time.astimezone(timezone.utc)

                if now < b_end:
                    b.end_time = max(b_start, now)
                b.status = "FINALIZADA"
            else:
                b.status = "CANCELADA_USUARIO"
            db.add(b)

        if desk.status != "MANUTENCAO":
            desk.status = "DISPONIVEL"
        db.add(desk)
        await db.commit()
        await db.refresh(desk)
        return desk
