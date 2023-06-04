from datetime import datetime
from typing import Optional

from pydantic import Field
from app.models.base import Base
from app.utils.mongo_validator import PyObjectId


class Gift(Base):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    product: PyObjectId = None
    points: int = 0


class GiftInDB(Gift):
    disabled: Optional[bool] = False
    date_insert: Optional[datetime] = None
    date_update: Optional[datetime] = None
    username_insert: Optional[str] = None
    username_update: Optional[str] = None


class RedeemGift(Base):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    participant_control_code: str = ""
    gift: PyObjectId = None
    date: datetime = None
    user_control: str = ""

class RedeemGiftInDB(RedeemGift):
    disabled: Optional[bool] = False
    date_insert: Optional[datetime] = None
    date_update: Optional[datetime] = None
    username_insert: Optional[str] = None
    username_update: Optional[str] = None