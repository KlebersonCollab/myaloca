from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.building import Building, Company
from app.models.desk import Zone
from app.schemas.building import (
    BuildingCreate,
    BuildingUpdate,
    CompanyCreate,
    CompanyUpdate,
)


class BuildingService:
    # ==========================================
    # Company Methods
    # ==========================================
    @staticmethod
    async def create_company(db: AsyncSession, company_in: CompanyCreate) -> Company:
        existing = (
            await db.execute(select(Company).where(Company.code == company_in.code))
        ).scalar_one_or_none()
        if existing:
            raise ValueError("COMPANY_CODE_EXISTS")

        company = Company(
            name=company_in.name,
            code=company_in.code,
            cnpj=company_in.cnpj,
            description=company_in.description,
            is_active=company_in.is_active,
        )
        db.add(company)
        await db.commit()
        await db.refresh(company)
        return company

    @staticmethod
    async def get_companies(db: AsyncSession) -> Sequence[Company]:
        result = await db.execute(select(Company).order_by(Company.name))
        return result.scalars().all()

    @staticmethod
    async def get_company_by_id(db: AsyncSession, company_id: int) -> Company | None:
        result = await db.execute(select(Company).where(Company.id == company_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_company(
        db: AsyncSession, company_id: int, company_in: CompanyUpdate
    ) -> Company:
        company = await BuildingService.get_company_by_id(db, company_id)
        if not company:
            raise ValueError("COMPANY_NOT_FOUND")

        update_data = company_in.model_dump(exclude_unset=True)
        if "code" in update_data and update_data["code"] != company.code:
            existing = (
                await db.execute(select(Company).where(Company.code == update_data["code"]))
            ).scalar_one_or_none()
            if existing:
                raise ValueError("COMPANY_CODE_EXISTS")

        for field, val in update_data.items():
            setattr(company, field, val)

        db.add(company)
        await db.commit()
        await db.refresh(company)
        return company

    @staticmethod
    async def delete_company(db: AsyncSession, company_id: int) -> None:
        company = await BuildingService.get_company_by_id(db, company_id)
        if not company:
            raise ValueError("COMPANY_NOT_FOUND")

        # Check if company has buildings
        q = select(Building).where(Building.company_id == company_id).limit(1)
        has_buildings = (await db.execute(q)).scalar_one_or_none()
        if has_buildings:
            raise ValueError("COMPANY_HAS_BUILDINGS")

        await db.delete(company)
        await db.commit()

    # ==========================================
    # Building Methods
    # ==========================================
    @staticmethod
    async def create_building(db: AsyncSession, building_in: BuildingCreate) -> Building:
        existing = (
            await db.execute(select(Building).where(Building.code == building_in.code))
        ).scalar_one_or_none()
        if existing:
            raise ValueError("BUILDING_CODE_EXISTS")

        building = Building(
            name=building_in.name,
            code=building_in.code,
            company_id=building_in.company_id,
            address=building_in.address,
            city=building_in.city,
            total_floors=building_in.total_floors,
            is_active=building_in.is_active,
        )
        db.add(building)
        await db.commit()
        await db.refresh(building)
        return building

    @staticmethod
    async def get_buildings(
        db: AsyncSession, company_id: int | None = None
    ) -> Sequence[Building]:
        query = select(Building).order_by(Building.name)
        if company_id is not None:
            query = query.where(Building.company_id == company_id)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_building_by_id(db: AsyncSession, building_id: int) -> Building | None:
        result = await db.execute(select(Building).where(Building.id == building_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_building(
        db: AsyncSession, building_id: int, building_in: BuildingUpdate
    ) -> Building:
        building = await BuildingService.get_building_by_id(db, building_id)
        if not building:
            raise ValueError("BUILDING_NOT_FOUND")

        update_data = building_in.model_dump(exclude_unset=True)
        if "code" in update_data and update_data["code"] != building.code:
            existing = (
                await db.execute(select(Building).where(Building.code == update_data["code"]))
            ).scalar_one_or_none()
            if existing:
                raise ValueError("BUILDING_CODE_EXISTS")

        for field, val in update_data.items():
            setattr(building, field, val)

        db.add(building)
        await db.commit()
        await db.refresh(building)
        return building

    @staticmethod
    async def delete_building(db: AsyncSession, building_id: int) -> None:
        building = await BuildingService.get_building_by_id(db, building_id)
        if not building:
            raise ValueError("BUILDING_NOT_FOUND")

        # Check if building has zones/floors
        q = select(Zone).where(Zone.building_id == building_id).limit(1)
        has_zones = (await db.execute(q)).scalar_one_or_none()
        if has_zones:
            raise ValueError("BUILDING_HAS_ZONES")

        await db.delete(building)
        await db.commit()
