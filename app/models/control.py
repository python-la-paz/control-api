from datetime import datetime
from typing import Literal, Optional

from pydantic import Field
from app.models.base import Base
from app.utils.mongo_validator import PyObjectId


class Control(Base):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    participant_control_code: str = ""
    location: PyObjectId = None
    location_name: str = ""
    control: Literal["in", "out"]
    date: datetime = None
    user_control: str = ""


class ControlInDB(Control):
    disabled: Optional[bool] = False
    date_insert: Optional[datetime] = None
    date_update: Optional[datetime] = None
    username_insert: Optional[str] = None
    username_update: Optional[str] = None
