from datetime import datetime

from pydantic import BaseModel, ConfigDict


# Zone Schemas
class ZoneBase(BaseModel):
    name: str
    floor: int = 1
    description: str | None = None
    is_active: bool = True


class ZoneCreate(ZoneBase):
    pass


class ZoneUpdate(BaseModel):
    name: str | None = None
    floor: int | None = None
    description: str | None = None
    is_active: bool | None = None


class ZoneResponse(ZoneBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Desk Schemas
class DeskBase(BaseModel):
    code: str
    zone_id: int
    pos_x: float = 0.0
    pos_y: float = 0.0
    pos_z: float = 0.0
    rotation_y: float = 0.0
    has_monitor: bool = False
    has_docking_station: bool = False
    is_standing_desk: bool = False


class DeskCreate(DeskBase):
    pass


class DeskUpdate(BaseModel):
    code: str | None = None
    zone_id: int | None = None
    status: str | None = None
    pos_x: float | None = None
    pos_y: float | None = None
    pos_z: float | None = None
    rotation_y: float | None = None
    has_monitor: bool | None = None
    has_docking_station: bool | None = None
    is_standing_desk: bool | None = None


class DeskResponse(DeskBase):
    id: int
    status: str
    qr_code_hash: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DeskWithOccupantResponse(DeskResponse):
    occupant_name: str | None = None
    occupant_avatar: str | None = None
    occupant_photo: str | None = None
    booking_id: int | None = None
