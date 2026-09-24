from datetime import datetime
from typing import Optional

from pydantic import Field

from app.models.base import Base
from app.utils.mongo_validator import PyObjectId


class SpecialPoint(Base):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    points: int = 0
    description: str = ""
    limit: int = 0


class SpecialPointInDB(SpecialPoint):
    disabled: Optional[bool] = False
    date_insert: Optional[datetime] = None
    date_update: Optional[datetime] = None
    username_insert: Optional[str] = None
    username_update: Optional[str] = None


class SpecialPointRedeem(Base):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    special_point: PyObjectId = None
    points: int = 0
    participant_control_code: str = ""
    date: datetime = None
    user_control: str = ""


class SpecialPointRedeemInDB(SpecialPointRedeem):
    disabled: Optional[bool] = False
    date_insert: Optional[datetime] = None
    date_update: Optional[datetime] = None
    username_insert: Optional[str] = None
    username_update: Optional[str] = None
