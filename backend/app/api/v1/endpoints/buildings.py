from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_current_user
from app.db.session import get_db
from app.models.building import Building, Company
from app.models.user import User
from app.schemas.building import (
    BuildingCreate,
    BuildingResponse,
    BuildingUpdate,
    CompanyCreate,
    CompanyResponse,
    CompanyUpdate,
)
from app.services.building_service import BuildingService

router = APIRouter()


# ==========================================
# Company Endpoints
# ==========================================
@router.post(
    "/companies",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Companies"],
)
async def create_company(
    company_in: CompanyCreate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Company:
    try:
        return await BuildingService.create_company(db, company_in)
    except ValueError as e:
        err = str(e)
        if err == "COMPANY_CODE_EXISTS":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "COMPANY_CODE_EXISTS",
                    "message": "Código da empresa já cadastrado.",
                },
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "COMPANY_CREATION_FAILED", "message": err},
        ) from e


@router.get(
    "/companies",
    response_model=list[CompanyResponse],
    tags=["Companies"],
)
async def list_companies(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Sequence[Company]:
    return await BuildingService.get_companies(db)


@router.get(
    "/companies/{company_id}",
    response_model=CompanyResponse,
    tags=["Companies"],
)
async def get_company(
    company_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Company:
    company = await BuildingService.get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "COMPANY_NOT_FOUND", "message": "Empresa não encontrada."},
        )
    return company


@router.put(
    "/companies/{company_id}",
    response_model=CompanyResponse,
    tags=["Companies"],
)
async def update_company(
    company_id: int,
    company_in: CompanyUpdate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Company:
    try:
        return await BuildingService.update_company(db, company_id, company_in)
    except ValueError as e:
        err = str(e)
        if err == "COMPANY_NOT_FOUND":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "COMPANY_NOT_FOUND", "message": "Empresa não encontrada."},
            ) from e
        if err == "COMPANY_CODE_EXISTS":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "COMPANY_CODE_EXISTS",
                    "message": "Código da empresa já cadastrado.",
                },
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "COMPANY_UPDATE_FAILED", "message": err},
        ) from e


@router.delete(
    "/companies/{company_id}",
    status_code=status.HTTP_200_OK,
    tags=["Companies"],
)
async def delete_company(
    company_id: int,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    try:
        await BuildingService.delete_company(db, company_id)
        return {"code": "COMPANY_DELETED", "message": "Empresa removida com sucesso."}
    except ValueError as e:
        err = str(e)
        if err == "COMPANY_NOT_FOUND":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "COMPANY_NOT_FOUND", "message": "Empresa não encontrada."},
            ) from e
        if err == "COMPANY_HAS_BUILDINGS":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "COMPANY_HAS_BUILDINGS",
                    "message": "Não é possível remover empresa que possui prédios associados.",
                },
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "COMPANY_DELETE_FAILED", "message": err},
        ) from e


# ==========================================
# Building Endpoints
# ==========================================
@router.post(
    "/buildings",
    response_model=BuildingResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Buildings"],
)
async def create_building(
    building_in: BuildingCreate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Building:
    try:
        return await BuildingService.create_building(db, building_in)
    except ValueError as e:
        err = str(e)
        if err == "BUILDING_CODE_EXISTS":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "BUILDING_CODE_EXISTS",
                    "message": "Código do prédio já cadastrado.",
                },
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "BUILDING_CREATION_FAILED", "message": err},
        ) from e


@router.get(
    "/buildings",
    response_model=list[BuildingResponse],
    tags=["Buildings"],
)
async def list_buildings(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    company_id: int | None = None,
) -> Sequence[Building]:
    return await BuildingService.get_buildings(db, company_id=company_id)


@router.get(
    "/buildings/{building_id}",
    response_model=BuildingResponse,
    tags=["Buildings"],
)
async def get_building(
    building_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Building:
    building = await BuildingService.get_building_by_id(db, building_id)
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "BUILDING_NOT_FOUND", "message": "Prédio não encontrado."},
        )
    return building


@router.put(
    "/buildings/{building_id}",
    response_model=BuildingResponse,
    tags=["Buildings"],
)
async def update_building(
    building_id: int,
    building_in: BuildingUpdate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Building:
    try:
        return await BuildingService.update_building(db, building_id, building_in)
    except ValueError as e:
        err = str(e)
        if err == "BUILDING_NOT_FOUND":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "BUILDING_NOT_FOUND", "message": "Prédio não encontrado."},
            ) from e
        if err == "BUILDING_CODE_EXISTS":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "BUILDING_CODE_EXISTS",
                    "message": "Código do prédio já cadastrado.",
                },
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "BUILDING_UPDATE_FAILED", "message": err},
        ) from e


@router.delete(
    "/buildings/{building_id}",
    status_code=status.HTTP_200_OK,
    tags=["Buildings"],
)
async def delete_building(
    building_id: int,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    try:
        await BuildingService.delete_building(db, building_id)
        return {"code": "BUILDING_DELETED", "message": "Prédio removido com sucesso."}
    except ValueError as e:
        err = str(e)
        if err == "BUILDING_NOT_FOUND":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "BUILDING_NOT_FOUND", "message": "Prédio não encontrado."},
            ) from e
        if err == "BUILDING_HAS_ZONES":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "BUILDING_HAS_ZONES",
                    "message": "Não é possível remover prédio que possui pavimentos associados.",
                },
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "BUILDING_DELETE_FAILED", "message": err},
        ) from e
