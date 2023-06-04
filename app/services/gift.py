from datetime import datetime
from typing import List
from pymongo.collection import ReturnDocument

from app.core.database import db
from app.models.gift import GiftInDB, RedeemGiftInDB
from app.utils.mongo_validator import PyObjectId


class GiftService:
    TABLE = db.gifts

    @classmethod
    def insert(cls, item: GiftInDB) -> GiftInDB:
        if hasattr(item, "id"):
            delattr(item, "id")
        item.date_insert = datetime.utcnow()
        item.date_update = item.date_insert
        inserted = cls.TABLE.insert_one(item.dict(by_alias=True))
        item.id = inserted.inserted_id
        return item

    @classmethod
    def delete(cls, id: PyObjectId) -> GiftInDB | None:
        deleted = cls.TABLE.find_one_and_update(
            {"_id": id},
            {"$set": {"disabled": True}},
            return_document=ReturnDocument.AFTER,
        )
        if deleted is not None:
            return GiftInDB(**deleted)
        else:
            return None

    @classmethod
    def get(cls, id: PyObjectId) -> GiftInDB | None:
        item = cls.TABLE.find_one({"_id": id, "disabled": False})
        if item is not None:
            return GiftInDB(**item)
        return item

    @classmethod
    def get_all(cls) -> List[GiftInDB]:
        items = cls.TABLE.find({"disabled": False})
        return [GiftInDB(**item) for item in items]


class RedeemGiftService:
    TABLE = db.redeem_gifts

    @classmethod
    def insert(cls, item: RedeemGiftInDB) -> RedeemGiftInDB:
        if hasattr(item, "id"):
            delattr(item, "id")
        item.date_insert = datetime.utcnow()
        item.date_update = item.date_insert
        inserted = cls.TABLE.insert_one(item.dict(by_alias=True))
        item.id = inserted.inserted_id
        return item

    @classmethod
    def get(cls, id: PyObjectId) -> RedeemGiftInDB | None:
        item = cls.TABLE.find_one({"_id": id, "disabled": False})
        if item is not None:
            return RedeemGiftInDB(**item)
        return item

    @classmethod
    def get_all(cls) -> List[RedeemGiftInDB]:
        items = cls.TABLE.find({"disabled": False})
        return [RedeemGiftInDB(**item) for item in items]

    @classmethod
    def get_all_by_participant(
        cls, participant_control_code: str
    ) -> List[RedeemGiftInDB]:
        items = cls.TABLE.find(
            {"participant_control_code": participant_control_code, "disabled": False}
        )
        return [RedeemGiftInDB(**item) for item in items]
