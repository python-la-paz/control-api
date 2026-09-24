from datetime import datetime
from typing import List

from pymongo.collection import ReturnDocument

from app.core.database import db
from app.models.gift import GiftInDB, RedeemGiftInDB, SelfServiceGift
from app.utils.mongo_validator import PyObjectId


class GiftService:
    TABLE = db.gifts

    @classmethod
    def insert(cls, item: GiftInDB) -> GiftInDB:
        if hasattr(item, "id"):
            delattr(item, "id")
        if hasattr(item, "product_name"):  # Deprecated
            delattr(item, "product_name")
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

    @classmethod
    def get_all_gift_and_products(cls) -> List[GiftInDB]:
        query = [
            {
                "$lookup": {
                    "from": "products",
                    "localField": "product",
                    "foreignField": "_id",
                    "as": "product",
                },
            },
            {"$unwind": "$product"},
            {"$match": {"disabled": False}},
            {
                "$project": {
                    "_id": 1,
                    "name": 1,
                    "points": 1,
                    "product": "$product._id",
                    "product_name": "$product.name",
                },
            },
        ]
        items = cls.TABLE.aggregate(query)
        return [GiftInDB(**item) for item in items]

    @classmethod
    def get_all_virtual(cls) -> List[SelfServiceGift]:
        query = [
            {"$match": {"disabled": False}},
            {
                "$lookup": {
                    "from": "products",
                    "localField": "product",
                    "foreignField": "_id",
                    "as": "product",
                },
            },
            {"$unwind": "$product"},
            {
                "$match": {
                    "product.disabled": False,
                    "product.kind": {"$in": ["digital_file", "discount_code"]},
                    "$or": [
                        {"product.stock": None},
                        {"product.stock": {"$gt": 0}},
                    ],
                },
            },
            {
                "$project": {
                    "_id": 1,
                    "points": 1,
                    "multiple": 1,
                    "name": "$product.name",
                    "description": "$product.description",
                    "kind": "$product.kind",
                    "stock": "$product.stock",
                },
            },
        ]
        items = cls.TABLE.aggregate(query)
        return [SelfServiceGift(**item) for item in items]


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
        cls,
        participant_control_code: str,
    ) -> List[RedeemGiftInDB]:
        items = cls.TABLE.find(
            {"participant_control_code": participant_control_code, "disabled": False},
        )
        return [RedeemGiftInDB(**item) for item in items]

    @classmethod
    def get_redeem_gift_by_participant(
        cls,
        participant_control_code: str,
        gift: PyObjectId,
    ) -> List[RedeemGiftInDB]:
        items = cls.TABLE.find(
            {
                "participant_control_code": participant_control_code,
                "gift": gift,
                "disabled": False,
            },
        )
        if items is not None:
            return [RedeemGiftInDB(**item) for item in items]
        return []

    @classmethod
    def exist_participant_control_code(cls, participant_control_code: str) -> bool:
        items = cls.TABLE.count_documents(
            {"participant_control_code": participant_control_code, "disabled": False},
        )
        return items > 0
