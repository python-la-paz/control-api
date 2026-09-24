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
    participation_points: int = 0
    attendance_checkpoints: int = 1
    min_checkpoint_duration: int = 5
    location: PyObjectId = Field(alias="location", default=None)

    def checkpoint_points(self) -> dict[int, int]:
        base, remainder = divmod(
            self.points,
            self.attendance_checkpoints,
        )

        return {
            checkpoint: base
            + (1 if checkpoint > self.attendance_checkpoints - remainder else 0)
            for checkpoint in range(1, self.attendance_checkpoints + 1)
        }

    def checkpoint_point(self, checkpoint: int) -> int:
        return self.checkpoint_points().get(checkpoint, 0)


class PresentationInDB(Presentation):
    disabled: Optional[bool] = False
    date_insert: Optional[datetime] = None
    date_update: Optional[datetime] = None
    username_insert: Optional[str] = None
    username_update: Optional[str] = None
