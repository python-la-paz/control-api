from datetime import datetime
from pymongo.collection import ReturnDocument

from app.core.database import db
from app.models.presentation import PresentationInDB
from app.utils.mongo_validator import PyObjectId


class PresentationService:
    TABLE = db.presentations

    @classmethod
    def insert(cls, item: PresentationInDB) -> PresentationInDB:
        if hasattr(item, "id"):
            delattr(item, "id")
        item.date_insert = datetime.utcnow()
        item.date_update = item.date_insert
        inserted = cls.TABLE.insert_one(item.dict(by_alias=True))
        item.id = inserted.inserted_id
        return item

    @classmethod
    def delete(cls, id: PyObjectId) -> PresentationInDB | None:
        deleted = cls.TABLE.find_one_and_update(
            {"_id": id},
            {"$set": {"disabled": True}},
            return_document=ReturnDocument.AFTER,
        )
        if deleted is not None:
            return PresentationInDB(**deleted)
        else:
            return None

    @classmethod
    def get(cls, id: PyObjectId) -> PresentationInDB | None:
        item = cls.TABLE.find_one({"_id": id, "disabled": False})
        if item is not None:
            return PresentationInDB(**item)
        return item

    @classmethod
    def get_all(cls) -> list[PresentationInDB]:
        items = cls.TABLE.find({"disabled": False})
        return [PresentationInDB(**item) for item in items]

    @classmethod
    def update_presentation(
        cls, id: PyObjectId, points: int = 0
    ) -> PresentationInDB | None:
        item = cls.TABLE.find_one_and_update(
            {"_id": id, "disabled": False},
            {"$set": {"points": points}},
            return_document=ReturnDocument.AFTER,
        )
        if item is not None:
            return PresentationInDB(**item)
        return item
