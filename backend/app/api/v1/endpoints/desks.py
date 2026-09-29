from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_current_user
from app.db.session import get_db
from app.models.desk import Desk, Zone
from app.models.user import User
from app.schemas.desk import DeskCreate, DeskResponse, DeskUpdate
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


@router.post("/batch", response_model=list[DeskResponse], status_code=status.HTTP_201_CREATED)
async def create_desks_batch(
    desks_in: list[DeskCreate],
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[Desk]:
    """Creates a batch of desks with auto-generated coordinates and QR hashes."""
    if not desks_in:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "EMPTY_BATCH", "message": "A lista de baias está vazia."},
        )

    codes = [d.code for d in desks_in]
    if len(codes) != len(set(codes)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "DUPLICATE_CODES_IN_BATCH", "message": "Códigos duplicados no lote."},
        )

    existing = await db.execute(select(Desk.code).where(Desk.code.in_(codes)))
    found = existing.scalars().all()
    if found:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "DESK_CODES_EXIST",
                "message": f"Baias já existentes: {', '.join(found)}",
            },
        )

    return await DeskService.create_desks_batch(db, desks_in)


@router.get("", response_model=list[DeskResponse])
async def list_desks(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    zone_id: int | None = Query(None, description="Filtrar por Zona"),
    floor: int | None = Query(None, description="Filtrar por Andar"),
) -> Sequence[Desk]:
    query = select(Desk)
    if zone_id is not None:
        query = query.where(Desk.zone_id == zone_id)
    elif floor is not None:
        query = query.join(Zone, Desk.zone_id == Zone.id).where(Zone.floor == floor)
    result = await db.execute(query.order_by(Desk.code))
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


@router.put("/{desk_id}", response_model=DeskResponse)
async def update_desk(
    desk_id: int,
    desk_in: DeskUpdate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Desk:
    try:
        return await DeskService.update_desk(db, desk_id, desk_in)
    except ValueError as e:
        err = str(e)
        if err == "DESK_NOT_FOUND":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "DESK_NOT_FOUND", "message": "Baia não encontrada."},
            ) from e
        if err == "DESK_CODE_EXISTS":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "DESK_CODE_EXISTS", "message": "Código da baia já cadastrado."},
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "DESK_UPDATE_FAILED", "message": err},
        ) from e


@router.delete("/{desk_id}", status_code=status.HTTP_200_OK)
async def delete_desk(
    desk_id: int,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    try:
        await DeskService.delete_desk(db, desk_id)
        return {"code": "DESK_DELETED", "message": "Baia removida com sucesso."}
    except ValueError as e:
        err = str(e)
        if err == "DESK_NOT_FOUND":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "DESK_NOT_FOUND", "message": "Baia não encontrada."},
            ) from e
        if err == "ACTIVE_BOOKINGS_EXIST":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "ACTIVE_BOOKINGS_EXIST",
                    "message": "Não é possível remover baia com reservas ativas.",
                },
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "DELETE_ERROR", "message": err},
        ) from e


@router.post("/{desk_id}/release", response_model=DeskResponse)
async def release_desk(
    desk_id: int,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Desk:
    """Administratively releases an occupied or reserved desk, terminating active bookings."""
    try:
        return await DeskService.release_desk(db, desk_id)
    except ValueError as e:
        err = str(e)
        if err == "DESK_NOT_FOUND":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "DESK_NOT_FOUND", "message": "Baia não encontrada."},
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "RELEASE_ERROR", "message": err},
        ) from e

