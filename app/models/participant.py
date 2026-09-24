from datetime import date, datetime
from typing import List, Literal, Optional

from pydantic import Field

from app.models.base import Base
from app.utils.mongo_validator import PyObjectId


class Participant(Base):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    mail: str = ""
    name: str = ""
    birthday: datetime
    gender: str = ""
    ci: str = ""
    profession: str = ""
    work_place: str = ""
    residence_place: str = ""
    photo: str = ""
    phone: str = ""
    t_shirt_size: str = ""
    food_restriction: str = ""
    control_code: str = ""
    registration: bool = False
    date_registration: Optional[datetime] = None
    combos: List[PyObjectId] = []
    locations: List[PyObjectId] = []
    combos_items: List[str] = []
    locations_items: List[str] = []
    role: Literal["user", "organizer", "speaker"] = "user"
    points: int = 0


class ParticipantInDB(Participant):
    disabled: Optional[bool] = False
    date_insert: Optional[datetime] = None
    date_update: Optional[datetime] = None
    username_insert: Optional[str] = None
    username_update: Optional[str] = None


class RevokeRegistration(Base):
    control_code: str = ""
    ci: str = ""
    participant_id = PyObjectId


class RevokeRegistrationInDB(RevokeRegistration):
    disabled: Optional[bool] = False
    date_insert: Optional[datetime] = None
    date_update: Optional[datetime] = None
    username_insert: Optional[str] = None
    username_update: Optional[str] = None


class SelfServiceParticipant(Base):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    control_code: str = ""
    qr_code: str = ""


class SelfServiceResult(Base):
    control_code: str = ""
    message: str = ""
    points: int = 0


class SelfServiceRedeem(SelfServiceResult):
    product_name: str = ""
    discount_code: Optional[str] = None
    download_url: Optional[str] = None


class SelfServiceRegisterRequest(Base):
    ci: str
    birthday: date


class SelfServiceCheckRequest(Base):
    control_code: str


class SelfServiceRedeemRequest(Base):
    control_code: str
    ci: str
    gift: PyObjectId | None = None
