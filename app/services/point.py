from datetime import datetime

from pymongo.collection import ReturnDocument

from app.core.database import db
from app.models.point import PointInDB
from app.utils.mongo_validator import PyObjectId


class PointService:
    TABLE = db.points

    @classmethod
    def insert(cls, item: PointInDB) -> PointInDB:
        if hasattr(item, "id"):
            delattr(item, "id")
        item.date_insert = datetime.utcnow()
        item.date_update = item.date_insert
        inserted = cls.TABLE.insert_one(item.dict(by_alias=True))
        item.id = inserted.inserted_id
        return item

    @classmethod
    def delete(cls, id: PyObjectId) -> PointInDB | None:
        deleted = cls.TABLE.find_one_and_update(
            {"_id": id},
            {"$set": {"disabled": True}},
            return_document=ReturnDocument.AFTER,
        )
        if deleted is not None:
            return PointInDB(**deleted)
        else:
            return None

    @classmethod
    def get(cls, id: PyObjectId) -> PointInDB | None:
        item = cls.TABLE.find_one({"_id": id, "disabled": False})
        if item is not None:
            return PointInDB(**item)
        return item

    @classmethod
    def get_all(cls) -> list[PointInDB]:
        items = cls.TABLE.find({"disabled": False})
        return [PointInDB(**item) for item in items]

    @classmethod
    def get_by_participant_and_presentation(
        cls,
        participant_control_code: str,
        presentation_id: PyObjectId,
    ) -> PointInDB | None:
        item = cls.TABLE.find_one(
            {
                "participant_control_code": participant_control_code,
                "presentation": presentation_id,
                "disabled": False,
                "is_participation": False,
            },
        )
        if item is not None:
            return PointInDB(**item)
        return item

    @classmethod
    def exist_by_participant_and_checkpoint(
        cls,
        participant_control_code: str,
        checkpoint_link_id: PyObjectId,
    ) -> bool:
        items = cls.TABLE.count_documents(
            {
                "participant_control_code": participant_control_code,
                "checkpoint_link": checkpoint_link_id,
                "disabled": False,
            },
        )
        return items > 0

    @classmethod
    def exist_participant_control_code(cls, participant_control_code: str) -> bool:
        items = cls.TABLE.count_documents(
            {"participant_control_code": participant_control_code, "disabled": False},
        )
        return items > 0
