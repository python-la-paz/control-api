from datetime import datetime
from typing import Optional

from pydantic import Field

from app.models.base import Base
from app.utils.mongo_validator import PyObjectId


class RedeemMeal(Base):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    participant_control_code: str = ""
    date: datetime = None
    user_control: str = ""
    product: Optional[PyObjectId] = None
    discount_code: Optional[str] = None
    download_url: Optional[str] = None


class RedeemMealInDB(RedeemMeal):
    disabled: Optional[bool] = False
    date_insert: Optional[datetime] = None
    date_update: Optional[datetime] = None
    username_insert: Optional[str] = None
    username_update: Optional[str] = None
