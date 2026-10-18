from datetime import datetime

from pydantic import Field

from app.models.base import Base
from app.utils.mongo_validator import PyObjectId


class PresentationCheckpointLink(Base):
    id: PyObjectId | None = Field(alias="_id", default=None)
    presentation: PyObjectId | None = Field(alias="presentation", default=None)
    checkpoint: int = 0
    points: int = 0
    code: str = Field(min_length=5, max_length=8, pattern=r"^[A-Za-z0-9]+$")
    min_duration: int = 5
    active: bool = True
    start_duration: datetime | None = None
    end_duration: datetime | None = None


class PresentationCheckpointLinkInDB(PresentationCheckpointLink):
    disabled: bool | None = False
    date_insert: datetime | None = None
    date_update: datetime | None = None
    username_insert: str = ""
    username_update: str = ""
