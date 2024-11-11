from datetime import datetime
from typing import List
from pymongo.collection import ReturnDocument

from app.core.database import db
from app.models.buy import BuyProductInDB
from app.utils.mongo_validator import PyObjectId


class BuyService:
    TABLE = db.buys

    @classmethod
    def insert(cls, item: BuyProductInDB) -> BuyProductInDB:
        if hasattr(item, "id"):
            delattr(item, "id")
        item.date_insert = datetime.utcnow()
        item.date_update = item.date_insert
        inserted = cls.TABLE.insert_one(item.dict(by_alias=True))
        item.id = inserted.inserted_id
        return item

    @classmethod
    def delete(cls, id: PyObjectId) -> BuyProductInDB | None:
        deleted = cls.TABLE.find_one_and_update(
            {"_id": id},
            {"$set": {"disabled": True}},
            return_document=ReturnDocument.AFTER,
        )
        if deleted is not None:
            return BuyProductInDB(**deleted)
        else:
            return None

    @classmethod
    def get(cls, id: PyObjectId) -> BuyProductInDB | None:
        item = cls.TABLE.find_one({"_id": id, "disabled": False})
        if item is not None:
            return BuyProductInDB(**item)
        return item

    @classmethod
    def get_all(cls) -> List[BuyProductInDB]:
        items = cls.TABLE.find({"disabled": False})
        return [BuyProductInDB(**item) for item in items]

    @classmethod
    def get_by_participant_control_code(cls, participant_control_code: str) -> List[BuyProductInDB]:
        items = cls.TABLE.find({"participant_control_code": participant_control_code, "disabled": False})
        return [BuyProductInDB(**item) for item in items]