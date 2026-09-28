from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_current_user
from app.db.session import get_db
from app.models.desk import Zone
from app.models.user import User
from app.schemas.desk import ZoneCreate, ZoneResponse
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
) -> Sequence[Zone]:
    return await DeskService.get_zones(db)
