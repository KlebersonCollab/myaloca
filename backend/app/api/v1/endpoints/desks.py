from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_current_user
from app.db.session import get_db
from app.models.desk import Desk
from app.models.user import User
from app.schemas.desk import DeskCreate, DeskResponse
from app.services.desk_service import DeskService

router = APIRouter()


@router.post("", response_model=DeskResponse, status_code=status.HTTP_201_CREATED)
async def create_desk(
    desk_in: DeskCreate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Desk:
    # Check duplicate code
    result = await db.execute(select(Desk).where(Desk.code == desk_in.code))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "DESK_CODE_EXISTS",
                "message": f"Baia com código '{desk_in.code}' já existe.",
            },
        )

    try:
        desk = await DeskService.create_desk(db, desk_in)
        return desk
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "DESK_CREATION_FAILED", "message": str(e)},
        ) from e


@router.get("", response_model=list[DeskResponse])
async def list_desks(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    zone_id: int | None = Query(None, description="Filtrar por Zona"),
) -> Sequence[Desk]:
    query = select(Desk)
    if zone_id is not None:
        query = query.where(Desk.zone_id == zone_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{desk_id}", response_model=DeskResponse)
async def get_desk(
    desk_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Desk:
    desk = await DeskService.get_desk_by_id(db, desk_id)
    if not desk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "DESK_NOT_FOUND", "message": "Baia não encontrada."},
        )
    return desk


@router.get("/{desk_id}/qrcode")
async def get_desk_qr_code(
    desk_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    desk = await DeskService.get_desk_by_id(db, desk_id)
    if not desk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "DESK_NOT_FOUND", "message": "Baia não encontrada."},
        )

    # Payload includes the immutable cryptographic hash
    qr_payload = f"myaloca://desk/{desk.id}?hash={desk.qr_code_hash}&code={desk.code}"
    image_bytes = DeskService.generate_qr_image(qr_payload)

    return Response(
        content=image_bytes,
        media_type="image/png",
        headers={"Content-Disposition": f'inline; filename="qrcode-{desk.code}.png"'},
    )
