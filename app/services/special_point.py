from datetime import datetime
from typing import List
from pymongo.collection import ReturnDocument

from app.core.database import db
from app.models.special_point import SpecialPointInDB, SpecialPointRedeemInDB
from app.utils.mongo_validator import PyObjectId


class SpecialPointService:
    TABLE = db.special_points
    TABLE_REDEEM = db.special_points_redeem

    @classmethod
    def insert(cls, item: SpecialPointInDB) -> SpecialPointInDB:
        if hasattr(item, "id"):
            delattr(item, "id")
        item.date_insert = datetime.utcnow()
        item.date_update = item.date_insert
        inserted = cls.TABLE.insert_one(item.dict(by_alias=True))
        item.id = inserted.inserted_id
        return item

    @classmethod
    def delete(cls, id: PyObjectId) -> SpecialPointInDB | None:
        deleted = cls.TABLE.find_one_and_update(
            {"_id": id},
            {"$set": {"disabled": True}},
            return_document=ReturnDocument.AFTER,
        )
        if deleted is not None:
            return SpecialPointInDB(**deleted)
        else:
            return None

    @classmethod
    def get(cls, id: PyObjectId) -> SpecialPointInDB | None:
        item = cls.TABLE.find_one({"_id": id, "disabled": False})
        if item is not None:
            return SpecialPointInDB(**item)
        return item

    @classmethod
    def get_all(cls) -> list[SpecialPointInDB]:
        items = cls.TABLE.find({"disabled": False})
        return [SpecialPointInDB(**item) for item in items]

    @classmethod
    def insert_redeem(cls, item: SpecialPointRedeemInDB) -> SpecialPointRedeemInDB:
        if hasattr(item, "id"):
            delattr(item, "id")
        item.date_insert = datetime.utcnow()
        item.date_update = item.date_insert
        inserted = cls.TABLE_REDEEM.insert_one(item.dict(by_alias=True))
        item.id = inserted.inserted_id
        return item

    @classmethod
    def get_redeems(
        cls, participant_control_code: str, id: PyObjectId
    ) -> List[SpecialPointRedeemInDB] | None:
        item = cls.TABLE_REDEEM.find(
            {
                "participant_control_code": participant_control_code,
                "special_point": id,
                "disabled": False,
            }
        )
        if item is not None:
            return [SpecialPointRedeemInDB(**i) for i in item]
        return item

    @classmethod
    def exist_participant_control_code(cls, participant_control_code: str) -> bool:
        items = cls.TABLE_REDEEM.count_documents(
            {"participant_control_code": participant_control_code, "disabled": False}
        )
        if items > 0:
            return True
        return False
