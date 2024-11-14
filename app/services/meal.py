from datetime import datetime
from typing import List
from pymongo.collection import ReturnDocument

from app.core.database import db
from app.models.meal import RedeemMealInDB
from app.utils.mongo_validator import PyObjectId


class RedeemMealService:
    TABLE = db.redeem_meals

    @classmethod
    def insert(cls, item: RedeemMealInDB) -> RedeemMealInDB:
        if hasattr(item, "id"):
            delattr(item, "id")
        item.date_insert = datetime.utcnow()
        item.date_update = item.date_insert
        inserted = cls.TABLE.insert_one(item.dict(by_alias=True))
        item.id = inserted.inserted_id
        return item

    @classmethod
    def delete(cls, id: PyObjectId) -> RedeemMealInDB | None:
        deleted = cls.TABLE.find_one_and_update(
            {"_id": id},
            {"$set": {"disabled": True}},
            return_document=ReturnDocument.AFTER,
        )
        if deleted is not None:
            return RedeemMealInDB(**deleted)
        else:
            return None

    @classmethod
    def get(cls, id: PyObjectId) -> RedeemMealInDB | None:
        item = cls.TABLE.find_one({"_id": id, "disabled": False})
        if item is not None:
            return RedeemMealInDB(**item)
        return item

    @classmethod
    def get_all(cls) -> List[RedeemMealInDB]:
        items = cls.TABLE.find({"disabled": False})
        return [RedeemMealInDB(**item) for item in items]

    @classmethod
    def get_by_participant(cls, participant_control_code: str) -> List[RedeemMealInDB]:
        items = cls.TABLE.find(
            {"participant_control_code": participant_control_code, "disabled": False}
        )
        return [RedeemMealInDB(**item) for item in items]

    @classmethod
    def exist_participant_control_code(cls, participant_control_code: str) -> bool:
        items = cls.TABLE.count_documents(
            {"participant_control_code": participant_control_code, "disabled": False}
        )
        if items > 0:
            return True
        return False
