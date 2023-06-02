from datetime import datetime
from pymongo.collection import ReturnDocument

from app.core.database import db
from app.models.combo import ComboInDB
from app.utils.mongo_validator import PyObjectId


class ComboService:
    TABLE = db.combos

    @classmethod
    def insert(cls, item: ComboInDB) -> ComboInDB:
        if hasattr(item, "id"):
            delattr(item, "id")
        item.date_insert = datetime.utcnow()
        item.date_update = item.date_insert
        inserted = cls.TABLE.insert_one(item.dict(by_alias=True))
        item.id = inserted.inserted_id
        return item

    @classmethod
    def delete(cls, id: PyObjectId) -> ComboInDB | None:
        deleted = cls.TABLE.find_one_and_update( {"_id": id}, {"$set": {"disabled": True}}, return_document=ReturnDocument.AFTER)
        if deleted is not None:
            return ComboInDB(**deleted)
        else:
            return None
    
    @classmethod
    def get(cls, id: PyObjectId) -> ComboInDB | None:
        item = cls.TABLE.find_one({"_id": id, "disabled": False})
        if item is not None:
            return ComboInDB(**item)
        return item
    
    @classmethod
    def get_all(cls) -> list[ComboInDB]:
        items = cls.TABLE.find({"disabled": False})
        return [ComboInDB(**item) for item in items]