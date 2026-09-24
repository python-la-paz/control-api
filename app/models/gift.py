from datetime import datetime
from typing import Optional

from pydantic import Field

from app.models.base import Base
from app.utils.mongo_validator import PyObjectId


class Gift(Base):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    product: PyObjectId = None
    product_name: Optional[str] = None
    points: int = 0
    multiple: bool = False


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
    product: Optional[PyObjectId] = None
    discount_code: Optional[str] = None
    download_url: Optional[str] = None
    multiple: bool = False


class SelfServiceGift(Base):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = ""
    description: str = ""
    kind: str = ""
    points: int = 0
    multiple: bool = False
    stock: Optional[int] = None


class RedeemGiftInDB(RedeemGift):
    disabled: Optional[bool] = False
    date_insert: Optional[datetime] = None
    date_update: Optional[datetime] = None
    username_insert: Optional[str] = None
    username_update: Optional[str] = None
