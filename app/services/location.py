from datetime import datetime
from pymongo.collection import ReturnDocument

from app.core.database import db
from app.models.location import LocationInDB
from app.utils.mongo_validator import PyObjectId


class LocationService:
    TABLE = db.locations

    @classmethod
    def insert(cls, item: LocationInDB) -> LocationInDB:
        if hasattr(item, "id"):
            delattr(item, "id")
        item.date_insert = datetime.utcnow()
        item.date_update = item.date_insert
        inserted = cls.TABLE.insert_one(item.dict(by_alias=True))
        item.id = inserted.inserted_id
        return item

    @classmethod
    def delete(cls, id: PyObjectId) -> LocationInDB | None:
        deleted = cls.TABLE.find_one_and_update(
            {"_id": id},
            {"$set": {"disabled": True}},
            return_document=ReturnDocument.AFTER,
        )
        if deleted is not None:
            return LocationInDB(**deleted)
        else:
            return None

    @classmethod
    def get(cls, id: PyObjectId) -> LocationInDB | None:
        item = cls.TABLE.find_one({"_id": id, "disabled": False})
        if item is not None:
            return LocationInDB(**item)
        return item

    @classmethod
    def get_all(cls) -> list[LocationInDB]:
        items = cls.TABLE.find({"disabled": False})
        return [LocationInDB(**item) for item in items]
