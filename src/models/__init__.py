from pydantic import BaseModel, SecretStr
from datetime import date


class Player(BaseModel):
    MundaneId: int
    Persona: str
    KingdomId: int
    ParkId: int


class AttendanceGet(BaseModel):
    host_park_id: int
    date: date  # The date of the event, not date entered
    event_calendar_detail_id: int = 0
    submitted: bool | None = None


class AttendanceRecord(AttendanceGet):
    player: Player
    class_id: int
    class_name: str
    attending_in_person: bool


class AttendanceSubmission(AttendanceGet):
    credit_data: dict


class LoginInfo(BaseModel):
    username: str
    password: SecretStr
