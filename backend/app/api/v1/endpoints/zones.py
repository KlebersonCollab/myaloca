from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_current_user
from app.db.session import get_db
from app.models.desk import Zone
from app.models.user import User
from app.schemas.desk import ZoneCreate, ZoneResponse, ZoneUpdate
from app.services.desk_service import DeskService

router = APIRouter()


@router.post("", response_model=ZoneResponse, status_code=status.HTTP_201_CREATED)
async def create_zone(
    zone_in: ZoneCreate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Zone:
    try:
        zone = await DeskService.create_zone(db, zone_in)
        return zone
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "ZONE_CREATION_FAILED", "message": str(e)},
        ) from e


@router.get("", response_model=list[ZoneResponse])
async def list_zones(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    floor: int | None = None,
    building_id: int | None = None,
) -> Sequence[Zone]:
    return await DeskService.get_zones(db, floor=floor, building_id=building_id)


@router.get("/{zone_id}", response_model=ZoneResponse)
async def get_zone(
    zone_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Zone:
    zone = await DeskService.get_zone_by_id(db, zone_id)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "ZONE_NOT_FOUND", "message": "Pavimento/Setor não encontrado."},
        )
    return zone


@router.put("/{zone_id}", response_model=ZoneResponse)
async def update_zone(
    zone_id: int,
    zone_in: ZoneUpdate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Zone:
    try:
        return await DeskService.update_zone(db, zone_id, zone_in)
    except ValueError as e:
        err = str(e)
        if err == "ZONE_NOT_FOUND":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "ZONE_NOT_FOUND", "message": "Pavimento/Setor não encontrado."},
            ) from e
        if err == "ZONE_NAME_EXISTS":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "ZONE_NAME_EXISTS", "message": "Nome do pavimento já em uso."},
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "ZONE_UPDATE_FAILED", "message": err},
        ) from e


@router.delete("/{zone_id}", status_code=status.HTTP_200_OK)
async def delete_zone(
    zone_id: int,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    try:
        await DeskService.delete_zone(db, zone_id)
        return {"code": "ZONE_DELETED", "message": "Pavimento removido com sucesso."}
    except ValueError as e:
        err = str(e)
        if err == "ZONE_NOT_FOUND":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "ZONE_NOT_FOUND", "message": "Pavimento não encontrado."},
            ) from e
        if err == "ZONE_HAS_DESKS":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "ZONE_HAS_DESKS",
                    "message": "Não é possível remover pavimento que possui baias cadastradas.",
                },
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "ZONE_DELETE_FAILED", "message": err},
        ) from e
