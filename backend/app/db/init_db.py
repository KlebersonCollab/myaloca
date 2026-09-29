from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.booking import Booking
from app.models.building import Building, Company
from app.models.department import Department
from app.models.desk import Desk, Zone
from app.models.user import User
from app.services.desk_service import DeskService


async def init_initial_data(db: AsyncSession) -> None:
    # ============================================================
    # 1. Company (Empresa Sede)
    # ============================================================
    q_comp = select(Company).where(Company.code == "MYALOCA-HQ")
    company = (await db.execute(q_comp)).scalar_one_or_none()
    if not company:
        company = Company(
            name="MyAloca Corporate",
            code="MYALOCA-HQ",
            cnpj="12.345.678/0001-90",
            description="Sede corporativa principal e escritórios integrados",
            is_active=True,
        )
        db.add(company)
        await db.commit()
        await db.refresh(company)

    # ============================================================
    # 2. Building (Edifício Sede)
    # ============================================================
    q_bld = select(Building).where(Building.code == "TORRE-PAULISTA")
    building = (await db.execute(q_bld)).scalar_one_or_none()
    if not building:
        building = Building(
            company_id=company.id,
            name="Torre Paulista Sede",
            code="TORRE-PAULISTA",
            address="Av. Paulista, 1000 - Bela Vista",
            city="São Paulo - SP",
            total_floors=5,
            is_active=True,
        )
        db.add(building)
        await db.commit()
        await db.refresh(building)

    # ============================================================
    # 3. Corporate Departments
    # ============================================================
    demo_departments = [
        ("Engenharia", "ENG", "Desenvolvimento de software, DevOps e Infraestrutura"),
        ("Design", "DSG", "UI/UX, Product Design e Research"),
        ("Operações", "OPS", "Facilities, RH e Operações Administrativas"),
        ("Analytics", "DATA", "Ciência de dados, BI e Inteligência de Negócio"),
    ]
    dept_map: dict[str, Department] = {}
    for name, code, desc in demo_departments:
        q_dept = select(Department).where(Department.name == name)
        existing_dept = (await db.execute(q_dept)).scalar_one_or_none()
        if not existing_dept:
            existing_dept = Department(
                company_id=company.id,
                name=name,
                code=code,
                description=desc,
                is_active=True,
            )
            db.add(existing_dept)
            await db.commit()
            await db.refresh(existing_dept)
        dept_map[name] = existing_dept

    # ============================================================
    # 4. Default Demo Users with Department Linking
    # ============================================================
    demo_users = [
        {
            "email": "admin@myaloca.com",
            "full_name": "Carlos Gestor",
            "password": "admin123",
            "role": "admin",
            "job_title": "Facilities Lead",
            "department": "Operações",
            "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=Admin",
        },
        {
            "email": "colaborador@myaloca.com",
            "full_name": "Lucas Dev",
            "password": "colab123",
            "role": "colaborador",
            "job_title": "Software Engineer",
            "department": "Engenharia",
            "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=Lucas",
        },
        {
            "email": "mariana@myaloca.com",
            "full_name": "Mariana Silva",
            "password": "mariana123",
            "role": "colaborador",
            "job_title": "Product Designer",
            "department": "Design",
            "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=Mariana",
        },
        {
            "email": "rodrigo@myaloca.com",
            "full_name": "Rodrigo Lima",
            "password": "rodrigo123",
            "role": "colaborador",
            "job_title": "Data Scientist",
            "department": "Analytics",
            "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=Rodrigo",
        },
    ]

    for u_info in demo_users:
        q_user = select(User).where(User.email == u_info["email"])
        user = (await db.execute(q_user)).scalar_one_or_none()
        dept_obj = dept_map.get(u_info["department"])
        dept_id = dept_obj.id if dept_obj else None

        if not user:
            user = User(
                email=u_info["email"],
                full_name=u_info["full_name"],
                hashed_password=get_password_hash(u_info["password"]),
                role=u_info["role"],
                job_title=u_info["job_title"],
                department=u_info["department"],
                department_id=dept_id,
                avatar_url=u_info["avatar_url"],
            )
            db.add(user)
        else:
            if not user.department_id and dept_id:
                user.department_id = dept_id
                db.add(user)
    await db.commit()

    # ============================================================
    # 5. Zones with Custom Grid Dimensions per Floor
    # ============================================================
    # Floor 1: 6 columns x 4 rows (Open Space)
    q_z1 = select(Zone).where(Zone.floor == 1).limit(1)
    zone1 = (await db.execute(q_z1)).scalar_one_or_none()
    if not zone1:
        zone1 = Zone(
            building_id=building.id,
            name="1º Andar - Open Space Alpha",
            floor=1,
            description="Bancadas colaborativas e monitores duplos (grade 6x4)",
            grid_cols=6,
            grid_rows=4,
            is_active=True,
        )
        db.add(zone1)
        await db.commit()
        await db.refresh(zone1)

        # 8 Desks arranged across 2 rows of 4
        # Row 1 (pos_z = -1.2, dual monitors)
        for i in range(1, 5):
            pos_x = round((i - 2.5) * 2.4, 2)
            desk = Desk(
                code=f"A-0{i}",
                zone_id=zone1.id,
                pos_x=pos_x,
                pos_y=0.0,
                pos_z=-1.2,
                rotation_y=0.0,
                has_monitor=True,
                monitors_count=2,
                has_docking_station=True,
                extra_equipment="Monitor Duplo Dell 27",
                qr_code_hash=DeskService.generate_immutable_qr_hash(),
                status="DISPONIVEL",
            )
            db.add(desk)

        # Row 2 (pos_z = 1.2, single monitor)
        for i in range(1, 5):
            pos_x = round((i - 2.5) * 2.4, 2)
            desk = Desk(
                code=f"A-0{i + 4}",
                zone_id=zone1.id,
                pos_x=pos_x,
                pos_y=0.0,
                pos_z=1.2,
                rotation_y=180.0,
                has_monitor=True,
                monitors_count=1,
                has_docking_station=False,
                extra_equipment="Monitor Único 24",
                qr_code_hash=DeskService.generate_immutable_qr_hash(),
                status="DISPONIVEL",
            )
            db.add(desk)
        await db.commit()
    else:
        # Ensure building_id and grid_cols/grid_rows are populated
        if not zone1.building_id:
            zone1.building_id = building.id
        if not zone1.grid_cols:
            zone1.grid_cols = 6
        if not zone1.grid_rows:
            zone1.grid_rows = 4
        db.add(zone1)
        await db.commit()

    # Floor 2: 8 columns x 4 rows (Engenharia - dynamic 8 desks per row!)
    q_z2 = select(Zone).where(Zone.floor == 2).limit(1)
    zone2 = (await db.execute(q_z2)).scalar_one_or_none()
    if not zone2:
        zone2 = Zone(
            building_id=building.id,
            name="2º Andar - Engenharia & Produto",
            floor=2,
            description="Bancadas ágeis com layout estendido de 8 colunas por linha (grade 8x4)",
            grid_cols=8,
            grid_rows=4,
            is_active=True,
        )
        db.add(zone2)
        await db.commit()
        await db.refresh(zone2)

        # 8 Desks aligned along Row 1 of an 8-column grid: (c - 3.5) * 2.4
        for i in range(8):
            pos_x = round((i - 3.5) * 2.4, 2)
            m_count = 2 if i < 4 else 1
            desk = Desk(
                code=f"ENG-0{i + 1}",
                zone_id=zone2.id,
                pos_x=pos_x,
                pos_y=0.0,
                pos_z=-1.2,
                rotation_y=0.0,
                has_monitor=True,
                monitors_count=m_count,
                has_docking_station=True,
                extra_equipment="Setup Dev Pro" if m_count == 2 else "Setup Dev Standard",
                qr_code_hash=DeskService.generate_immutable_qr_hash(),
                status="DISPONIVEL",
            )
            db.add(desk)

        # Special meeting room and focus booth on Row 3
        db.add(
            Desk(
                code="SALA-AGIL-01",
                zone_id=zone2.id,
                pos_x=6.0,
                pos_y=0.0,
                pos_z=3.6,
                rotation_y=0.0,
                has_monitor=True,
                monitors_count=2,
                has_docking_station=True,
                extra_equipment="TV 65 + Sistema Zoom Rooms",
                space_type="SALA_REUNIAO",
                capacity=6,
                max_duration_minutes=60,
                required_role=None,
                qr_code_hash=DeskService.generate_immutable_qr_hash(),
                status="DISPONIVEL",
            )
        )
        db.add(
            Desk(
                code="CABINE-FOCUS-01",
                zone_id=zone2.id,
                pos_x=-6.0,
                pos_y=0.0,
                pos_z=3.6,
                rotation_y=0.0,
                has_monitor=False,
                monitors_count=0,
                has_docking_station=True,
                extra_equipment="Headset ANC + Microfone USB",
                space_type="CABINE_FOCUS",
                capacity=1,
                max_duration_minutes=30,
                required_role=None,
                qr_code_hash=DeskService.generate_immutable_qr_hash(),
                status="DISPONIVEL",
            )
        )
        await db.commit()
    else:
        if not zone2.building_id:
            zone2.building_id = building.id
        if not zone2.grid_cols or zone2.grid_cols == 6:
            zone2.grid_cols = 8
        if not zone2.grid_rows:
            zone2.grid_rows = 4
        db.add(zone2)
        await db.commit()

    # Floor 3: 6 columns x 3 rows (Diretoria executiva)
    q_z3 = select(Zone).where(Zone.floor == 3).limit(1)
    zone3 = (await db.execute(q_z3)).scalar_one_or_none()
    if not zone3:
        zone3 = Zone(
            building_id=building.id,
            name="3º Andar - Diretoria & Operações",
            floor=3,
            description="Ambiente executivo e sala de conselho (grade 6x3)",
            grid_cols=6,
            grid_rows=3,
            is_active=True,
        )
        db.add(zone3)
        await db.commit()
        await db.refresh(zone3)

        for i in range(1, 5):
            pos_x = round((i - 2.5) * 2.4, 2)
            desk = Desk(
                code=f"DIR-0{i}",
                zone_id=zone3.id,
                pos_x=pos_x,
                pos_y=0.0,
                pos_z=-1.2,
                rotation_y=0.0,
                has_monitor=True,
                monitors_count=2,
                has_docking_station=True,
                is_standing_desk=True,
                extra_equipment="Mesa Elétrica Regulável + Ultrawide 38",
                qr_code_hash=DeskService.generate_immutable_qr_hash(),
                status="DISPONIVEL",
            )
            db.add(desk)

        db.add(
            Desk(
                code="SALA-BOARD-01",
                zone_id=zone3.id,
                pos_x=4.8,
                pos_y=0.0,
                pos_z=2.4,
                rotation_y=0.0,
                has_monitor=True,
                monitors_count=2,
                has_docking_station=True,
                extra_equipment="Painel LED 85 + Videoconferência Polycom",
                space_type="SALA_REUNIAO",
                capacity=12,
                max_duration_minutes=120,
                required_role="gestor",
                qr_code_hash=DeskService.generate_immutable_qr_hash(),
                status="DISPONIVEL",
            )
        )
        await db.commit()
    else:
        if not zone3.building_id:
            zone3.building_id = building.id
        if not zone3.grid_cols:
            zone3.grid_cols = 6
        if not zone3.grid_rows:
            zone3.grid_rows = 3
        db.add(zone3)
        await db.commit()

    # ============================================================
    # 6. Sample Active Bookings
    # ============================================================
    booking_res = await db.execute(
        select(Booking).where(Booking.status.in_(["PENDENTE_CHECKIN", "CHECKED_IN"])).limit(1)
    )
    if not booking_res.scalar_one_or_none():
        user_lucas = (
            await db.execute(select(User).where(User.email == "colaborador@myaloca.com"))
        ).scalar_one_or_none()
        user_mariana = (
            await db.execute(select(User).where(User.email == "mariana@myaloca.com"))
        ).scalar_one_or_none()

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

        if user_mariana and len(all_desks) >= 2:
            all_desks[1].status = "RESERVADA"
            b2 = Booking(
                desk_id=all_desks[1].id,
                user_id=user_mariana.id,
                start_time=now + timedelta(minutes=10),
                end_time=today_end,
                checkin_deadline=now + timedelta(minutes=40),
                status="PENDENTE_CHECKIN",
                notes="Alinhamento e Sprint Planning",
            )
            db.add(b2)
            db.add(all_desks[1])

        await db.commit()
