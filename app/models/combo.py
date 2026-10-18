from datetime import datetime
from typing import List, Optional

from pydantic import Field

from app.models.base import Base
from app.utils.mongo_validator import PyObjectId


class Products(Base):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = ""


class Combo(Base):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = ""
    description: str = ""
    products: List[PyObjectId] = []
    products_items: List[Products] = []


class ComboInDB(Combo):
    disabled: Optional[bool] = False
    date_insert: Optional[datetime] = None
    date_update: Optional[datetime] = None
    username_insert: Optional[str] = None
    username_update: Optional[str] = None


class RedeemCombo(Base):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    participant_control_code: str = ""
    combo: PyObjectId = None
    products: List[PyObjectId] = []
    date: datetime = None
    user_control: str = ""
    message: str = ""


class RedeemComboInDB(RedeemCombo):
    disabled: Optional[bool] = False
    date_insert: Optional[datetime] = None
    date_update: Optional[datetime] = None
    username_insert: Optional[str] = None


class RedeemComboRequest(Base):
    participant_control_code: str = ""
    combo_id: PyObjectId = None
    products_id: List[PyObjectId] = []
