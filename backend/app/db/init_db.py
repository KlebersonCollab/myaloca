from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.booking import Booking
from app.models.desk import Desk, Zone
from app.models.user import User
from app.services.desk_service import DeskService


async def init_initial_data(db: AsyncSession) -> None:
    # 1. Create Default Users if missing
    demo_users = [
        User(
            email="admin@myaloca.com",
            full_name="Carlos Gestor",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            job_title="Facilities Lead",
            department="Operações",
            avatar_url="https://api.dicebear.com/7.x/bottts/svg?seed=Admin",
        ),
        User(
            email="colaborador@myaloca.com",
            full_name="Lucas Dev",
            hashed_password=get_password_hash("colab123"),
            role="colaborador",
            job_title="Software Engineer",
            department="Engenharia",
            avatar_url="https://api.dicebear.com/7.x/bottts/svg?seed=Lucas",
        ),
        User(
            email="mariana@myaloca.com",
            full_name="Mariana Silva",
            hashed_password=get_password_hash("mariana123"),
            role="colaborador",
            job_title="Product Designer",
            department="Design",
            avatar_url="https://api.dicebear.com/7.x/bottts/svg?seed=Mariana",
        ),
        User(
            email="rodrigo@myaloca.com",
            full_name="Rodrigo Lima",
            hashed_password=get_password_hash("rodrigo123"),
            role="colaborador",
            job_title="Data Scientist",
            department="Analytics",
            avatar_url="https://api.dicebear.com/7.x/bottts/svg?seed=Rodrigo",
        ),
    ]
    for u in demo_users:
        query = select(User).where(User.email == u.email)
        existing = (await db.execute(query)).scalar_one_or_none()
        if not existing:
            db.add(u)
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
                pos_x=(i - 2.5) * 3.2,
                pos_y=0.0,
                pos_z=-2.2,
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
                pos_x=(i - 2.5) * 3.2,
                pos_y=0.0,
                pos_z=2.2,
                rotation_y=180.0,
                has_monitor=True,
                has_docking_station=False,
                qr_code_hash=DeskService.generate_immutable_qr_hash(),
                status="DISPONIVEL",
            )
            db.add(desk)

        await db.commit()

    # 2.1 Ensure Floor 2 and Floor 3 Zones & Desks exist
    floor2_res = await db.execute(select(Zone).where(Zone.floor == 2).limit(1))
    if not floor2_res.scalar_one_or_none():
        zone_floor2 = Zone(
            name="2º Andar - Engenharia & Produto",
            floor=2,
            description="Bancadas ágeis com monitores duplos e alta conectividade",
        )
        db.add(zone_floor2)
        await db.commit()
        await db.refresh(zone_floor2)

        for i in range(1, 5):
            desk = Desk(
                code=f"ENG-0{i}",
                zone_id=zone_floor2.id,
                pos_x=(i - 2.5) * 3.0,
                pos_y=0.0,
                pos_z=0.0,
                rotation_y=0.0,
                has_monitor=True,
                has_docking_station=True,
                qr_code_hash=DeskService.generate_immutable_qr_hash(),
                status="DISPONIVEL",
            )
            db.add(desk)
        await db.commit()

    floor3_res = await db.execute(select(Zone).where(Zone.floor == 3).limit(1))
    if not floor3_res.scalar_one_or_none():
        zone_floor3 = Zone(
            name="3º Andar - Diretoria & Operações",
            floor=3,
            description="Ambiente corporativo executivo e salas de reunião",
        )
        db.add(zone_floor3)
        await db.commit()
        await db.refresh(zone_floor3)

        for i in range(1, 5):
            desk = Desk(
                code=f"DIR-0{i}",
                zone_id=zone_floor3.id,
                pos_x=(i - 2.5) * 3.0,
                pos_y=0.0,
                pos_z=0.0,
                rotation_y=0.0,
                has_monitor=True,
                has_docking_station=True,
                qr_code_hash=DeskService.generate_immutable_qr_hash(),
                status="DISPONIVEL",
            )
            db.add(desk)
        await db.commit()

    # Ensure demo meeting rooms and focus booth exist
    z2 = (await db.execute(select(Zone).where(Zone.floor == 2).limit(1))).scalar_one_or_none()
    if z2:
        q_agil = select(Desk).where(Desk.code == "SALA-AGIL-01")
        agil = (await db.execute(q_agil)).scalar_one_or_none()
        if not agil:
            db.add(
                Desk(
                    code="SALA-AGIL-01",
                    zone_id=z2.id,
                    pos_x=6.0,
                    pos_y=0.0,
                    pos_z=4.0,
                    rotation_y=0.0,
                    has_monitor=True,
                    has_docking_station=True,
                    space_type="SALA_REUNIAO",
                    capacity=6,
                    max_duration_minutes=60,
                    required_role=None,
                    qr_code_hash=DeskService.generate_immutable_qr_hash(),
                    status="DISPONIVEL",
                )
            )
        q_focus = select(Desk).where(Desk.code == "CABINE-FOCUS-01")
        focus = (await db.execute(q_focus)).scalar_one_or_none()
        if not focus:
            db.add(
                Desk(
                    code="CABINE-FOCUS-01",
                    zone_id=z2.id,
                    pos_x=-6.0,
                    pos_y=0.0,
                    pos_z=4.0,
                    rotation_y=0.0,
                    has_monitor=False,
                    has_docking_station=True,
                    space_type="CABINE_FOCUS",
                    capacity=1,
                    max_duration_minutes=30,
                    required_role=None,
                    qr_code_hash=DeskService.generate_immutable_qr_hash(),
                    status="DISPONIVEL",
                )
            )
        await db.commit()

    z3 = (await db.execute(select(Zone).where(Zone.floor == 3).limit(1))).scalar_one_or_none()
    if z3:
        q_board = select(Desk).where(Desk.code == "SALA-BOARD-01")
        board = (await db.execute(q_board)).scalar_one_or_none()
        if not board:
            db.add(
                Desk(
                    code="SALA-BOARD-01",
                    zone_id=z3.id,
                    pos_x=6.0,
                    pos_y=0.0,
                    pos_z=4.0,
                    rotation_y=0.0,
                    has_monitor=True,
                    has_docking_station=True,
                    space_type="SALA_REUNIAO",
                    capacity=12,
                    max_duration_minutes=120,
                    required_role="gestor",
                    qr_code_hash=DeskService.generate_immutable_qr_hash(),
                    status="DISPONIVEL",
                )
            )
            await db.commit()

    # 3. Create Sample Active Bookings if none exist
    booking_res = await db.execute(
        select(Booking).where(Booking.status.in_(["PENDENTE_CHECKIN", "CHECKED_IN"])).limit(1)
    )
    if not booking_res.scalar_one_or_none():
        # Get users and desks
        user_lucas = (
            await db.execute(select(User).where(User.email == "colaborador@myaloca.com"))
        ).scalar_one_or_none()
        if not user_lucas:
            user_lucas = (await db.execute(select(User).limit(1))).scalar_one_or_none()

        desks_result = await db.execute(select(Desk).order_by(Desk.id))
        all_desks = list(desks_result.scalars().all())

        now = datetime.now(timezone.utc)
        today_start = now - timedelta(hours=2)
        today_end = now + timedelta(hours=6)

        if user_lucas and len(all_desks) >= 1:
            all_desks[0].status = "OCUPADA"
            b1 = Booking(
                desk_id=all_desks[0].id,
                user_id=user_lucas.id,
                start_time=today_start,
                end_time=today_end,
                checkin_deadline=today_start + timedelta(minutes=30),
                checked_in_at=today_start + timedelta(minutes=10),
                status="CHECKED_IN",
                notes="Desenvolvimento de Features",
            )
            db.add(b1)
            db.add(all_desks[0])

        if len(all_desks) >= 2:
            user_mariana = (
                await db.execute(select(User).where(User.email == "mariana@myaloca.com"))
            ).scalar_one_or_none()
            assigned_user_id = user_mariana.id if user_mariana else user_lucas.id
            all_desks[1].status = "RESERVADA"
            b2 = Booking(
                desk_id=all_desks[1].id,
                user_id=assigned_user_id,
                start_time=now + timedelta(minutes=10),
                end_time=today_end,
                checkin_deadline=now + timedelta(minutes=40),
                status="PENDENTE_CHECKIN",
                notes="Alinhamento e Sprint Planning",
            )
            db.add(b2)
            db.add(all_desks[1])

        await db.commit()
