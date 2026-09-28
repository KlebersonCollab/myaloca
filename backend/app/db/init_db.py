from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.desk import Desk, Zone
from app.models.user import User
from app.services.desk_service import DeskService


async def init_initial_data(db: AsyncSession) -> None:
    # 1. Create Default Admin if no user exists
    user_res = await db.execute(select(User).limit(1))
    if not user_res.scalar_one_or_none():
        admin_user = User(
            email="admin@myaloca.com",
            full_name="Gestor Facilities",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            job_title="Facilities Lead",
            department="Operações",
            avatar_url="https://api.dicebear.com/7.x/bottts/svg?seed=Admin",
        )
        colab_user = User(
            email="colaborador@myaloca.com",
            full_name="Lucas Desenvolvedor",
            hashed_password=get_password_hash("colab123"),
            role="colaborador",
            job_title="Software Engineer",
            department="Engenharia",
            avatar_url="https://api.dicebear.com/7.x/bottts/svg?seed=Lucas",
        )
        db.add(admin_user)
        db.add(colab_user)
        await db.commit()

    # 2. Create Initial Zones & Sample Desks if none exist
    zone_res = await db.execute(select(Zone).limit(1))
    if not zone_res.scalar_one_or_none():
        zone1 = Zone(
            name="Zona Alpha - Open Space",
            floor=1,
            description="Bancadas colaborativas e monitores duplos",
        )
        zone2 = Zone(
            name="Zona Beta - Silenciosa",
            floor=1,
            description="Ambiente de foco profundo",
        )
        db.add(zone1)
        db.add(zone2)
        await db.commit()
        await db.refresh(zone1)
        await db.refresh(zone2)

        # Create sample 3D desks in an aligned grid layout for 3D visualization
        # Row 1 in Zone Alpha
        for i in range(1, 5):
            desk = Desk(
                code=f"A-0{i}",
                zone_id=zone1.id,
                pos_x=(i - 2.5) * 3.0,
                pos_y=0.0,
                pos_z=-2.0,
                rotation_y=0.0,
                has_monitor=True,
                has_docking_station=True,
                qr_code_hash=DeskService.generate_immutable_qr_hash(),
                status="DISPONIVEL",
            )
            db.add(desk)

        # Row 2 in Zone Alpha
        for i in range(1, 5):
            desk = Desk(
                code=f"A-0{i + 4}",
                zone_id=zone1.id,
                pos_x=(i - 2.5) * 3.0,
                pos_y=0.0,
                pos_z=2.0,
                rotation_y=180.0,
                has_monitor=True,
                has_docking_station=False,
                qr_code_hash=DeskService.generate_immutable_qr_hash(),
                status="DISPONIVEL",
            )
            db.add(desk)

        await db.commit()
