from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.booking import Booking
from app.models.desk import Desk
from app.models.user import User
from app.schemas.booking import BookingCheckIn, BookingCreate, BookingResponse
from app.schemas.desk import DeskWithOccupantResponse
from app.services.booking_service import BookingService
from app.services.desk_service import DeskService

router = APIRouter()


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_in: BookingCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Booking:
    try:
        booking = await BookingService.create_booking(db, current_user.id, booking_in)
        return booking
    except ValueError as e:
        err_msg = str(e)
        if err_msg == "BOOKING_OVERLAP":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "BOOKING_OVERLAP",
                    "message": "A baia selecionada já possui reserva ativa no período informado.",
                },
            ) from e
        if err_msg == "DESK_NOT_FOUND":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "DESK_NOT_FOUND", "message": "Baia não encontrada."},
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "BOOKING_ERROR", "message": err_msg},
        ) from e


@router.post("/{booking_id}/checkin", response_model=BookingResponse)
async def checkin_booking(
    booking_id: int,
    checkin_in: BookingCheckIn,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Booking:
    try:
        booking = await BookingService.check_in(
            db,
            booking_id=booking_id,
            user_id=current_user.id,
            qr_code_hash=checkin_in.qr_code_hash,
        )
        return booking
    except ValueError as e:
        err_code = str(e)
        if err_code == "INVALID_QR_CODE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_QR_CODE",
                    "message": "QR Code inválido ou não pertencente a esta baia física.",
                },
            ) from e
        if err_code == "CHECKIN_TOO_EARLY":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "CHECKIN_TOO_EARLY",
                    "message": "Check-in só é permitido até 15 minutos antes do início.",
                },
            ) from e
        if err_code == "CHECKIN_WINDOW_EXPIRED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "CHECKIN_WINDOW_EXPIRED",
                    "message": "Janela de tolerância para check-in expirou.",
                },
            ) from e
        if err_code == "BOOKING_NOT_FOUND":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "BOOKING_NOT_FOUND", "message": "Reserva não encontrada."},
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "CHECKIN_ERROR", "message": err_code},
        ) from e


@router.get("/me", response_model=list[BookingResponse])
async def list_my_bookings(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Sequence[Booking]:
    return await BookingService.get_user_bookings(db, current_user.id)


@router.get("/3d-office", response_model=list[DeskWithOccupantResponse])
async def get_3d_office_layout(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    zone_id: int | None = None,
) -> list[DeskWithOccupantResponse]:
    """Returns desks with 3D coordinates and current occupant avatar/photo."""
    all_desks = await DeskService.get_desks_by_zone(db, zone_id) if zone_id else (
        (await db.execute(select(Desk))).scalars().all()
    )
    active_occupancies = await BookingService.get_active_occupancies(db)
    occupancy_map: dict[int, Booking] = {b.desk_id: b for b in active_occupancies}

    response_list: list[DeskWithOccupantResponse] = []
    for d in all_desks:
        booking = occupancy_map.get(d.id)
        occupant_name = None
        occupant_avatar = None
        occupant_photo = None
        b_id = None
        desk_status = d.status

        if booking and booking.user:
            occupant_name = booking.user.full_name
            occupant_avatar = booking.user.avatar_url
            occupant_photo = booking.user.photo_url
            b_id = booking.id
            desk_status = "OCUPADA" if booking.status == "CHECKED_IN" else "RESERVADA"

        response_list.append(
            DeskWithOccupantResponse(
                id=d.id,
                code=d.code,
                zone_id=d.zone_id,
                pos_x=d.pos_x,
                pos_y=d.pos_y,
                pos_z=d.pos_z,
                rotation_y=d.rotation_y,
                has_monitor=d.has_monitor,
                has_docking_station=d.has_docking_station,
                is_standing_desk=d.is_standing_desk,
                status=desk_status,
                qr_code_hash=d.qr_code_hash,
                created_at=d.created_at,
                occupant_name=occupant_name,
                occupant_avatar=occupant_avatar,
                occupant_photo=occupant_photo,
                booking_id=b_id,
            )
        )
    return response_list
