from datetime import datetime
from typing import List, Literal, Optional

from pydantic import Field

from app.models.base import Base
from app.utils.mongo_validator import PyObjectId


class DiscountCode(Base):
    code: str
    assigned_to: Optional[str] = None
    date_assigned: Optional[datetime] = None


class Product(Base):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = ""
    description: str = ""
    able_to_buy: bool = False
    price: float = 0.0
    currency: str = ""
    kind: Literal["physical", "digital_file", "discount_code"] = "physical"
    # None means unlimited stock
    stock: Optional[int] = None
    file_url: str = ""
    is_virtual_meal: bool = False
    discount_codes: List[DiscountCode] = []


class ProductInDB(Product):
    disabled: Optional[bool] = False
    date_insert: Optional[datetime] = None
    date_update: Optional[datetime] = None
    username_insert: Optional[str] = None
    username_update: Optional[str] = None
