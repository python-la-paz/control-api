from datetime import datetime
from typing import List, Literal, Optional

from pydantic import Field
from app.models.base import Base
from app.utils.mongo_validator import PyObjectId


class Participant(Base):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    mail: str = ""
    name: str = ""
    birthday: datetime = None
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
    combos: List[PyObjectId] = []
    locations: List[PyObjectId] = []
    role: Literal["user", "organizer", "speaker"] = "user"
    points: int = 0


class ParticipantInDB(Participant):
    disabled: Optional[bool] = False
    date_insert: Optional[datetime] = None
    date_update: Optional[datetime] = None
    username_insert: Optional[str] = None
    username_update: Optional[str] = None