from datetime import datetime
from pymongo.collection import ReturnDocument

from app.core.database import db
from app.models.control import ControlInDB
from app.utils.mongo_validator import PyObjectId


class ControlService:
    TABLE = db.control

    @classmethod
    def insert(cls, item: ControlInDB) -> ControlInDB:
        if hasattr(item, "id"):
            delattr(item, "id")
        item.date_insert = datetime.utcnow()
        item.date_update = item.date_insert
        inserted = cls.TABLE.insert_one(item.dict(by_alias=True))
        item.id = inserted.inserted_id
        return item

    @classmethod
    def get_all(cls) -> list[ControlInDB]:
        items = cls.TABLE.find({"disabled": False})
        return [ControlInDB(**item) for item in items]

    @classmethod
    def get_all_by_participant(cls, participant_control_code: str) -> list[ControlInDB]:
        items = cls.TABLE.find(
            {"participant_control_code": participant_control_code, "disabled": False}
        )
        return [ControlInDB(**item) for item in items]

    @classmethod
    def count_checks(
        cls, participant_control_code: str, location: PyObjectId, control: str
    ) -> int:
        return cls.TABLE.count_documents(
            {
                "participant_control_code": participant_control_code,
                "location": location,
                "control": control,
                "disabled": False,
            }
        )
