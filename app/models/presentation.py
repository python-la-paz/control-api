from datetime import datetime
from typing import Literal, Optional

from pydantic import Field
from app.models.base import Base
from app.utils.mongo_validator import PyObjectId


class Presentation(Base):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = ""
    speaker: str = ""
    description: str = ""
    kind: Literal["talk", "workshop"] = "talk"
    points: int = 0
    location: PyObjectId = Field(alias="location", default=None)


class PresentationInDB(Presentation):
    disabled: Optional[bool] = False
    date_insert: Optional[datetime] = None
    date_update: Optional[datetime] = None
    username_insert: Optional[str] = None
    username_update: Optional[str] = None
