from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator


class BookingBase(BaseModel):
    desk_id: int
    start_time: datetime
    end_time: datetime
    notes: str | None = None


class BookingCreate(BookingBase):
    @model_validator(mode="after")
    def validate_time_range(self) -> "BookingCreate":
        if self.start_time >= self.end_time:
            raise ValueError("O horário de início deve ser anterior ao horário de término.")
        return self


class BookingCheckIn(BaseModel):
    qr_code_hash: str


class BookingResponse(BookingBase):
    id: int
    user_id: int
    checkin_deadline: datetime
    checked_in_at: datetime | None = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BookingDetailResponse(BookingResponse):
    desk_code: str | None = None
    user_name: str | None = None
    user_avatar: str | None = None
