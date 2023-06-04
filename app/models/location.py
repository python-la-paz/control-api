from datetime import datetime
from typing import Optional

from pydantic import Field
from app.models.base import Base
from app.utils.mongo_validator import PyObjectId


class Location(Base):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = ""
    value: str = ""


class LocationInDB(Location):
    disabled: Optional[bool] = False
    date_insert: Optional[datetime] = None
    date_update: Optional[datetime] = None
    username_insert: Optional[str] = None
    username_update: Optional[str] = None
