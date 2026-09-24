from datetime import datetime

from pymongo.collection import ReturnDocument

from app.core.database import db
from app.models.product import DiscountCode, ProductInDB
from app.utils.mongo_validator import PyObjectId


class ProductService:
    TABLE = db.products

    @classmethod
    def insert(cls, item: ProductInDB) -> ProductInDB:
        if hasattr(item, "id"):
            delattr(item, "id")
        if item.kind == "discount_code":
            item.stock = sum(1 for c in item.discount_codes if c.assigned_to is None)
        item.date_insert = datetime.utcnow()
        item.date_update = item.date_insert
        inserted = cls.TABLE.insert_one(item.dict(by_alias=True))
        item.id = inserted.inserted_id
        return item

    @classmethod
    def delete(cls, id: PyObjectId) -> ProductInDB | None:
        deleted = cls.TABLE.find_one_and_update(
            {"_id": id},
            {"$set": {"disabled": True}},
            return_document=ReturnDocument.AFTER,
        )
        if deleted is not None:
            return ProductInDB(**deleted)
        else:
            return None

    @classmethod
    def update(cls, id: PyObjectId, item: ProductInDB) -> ProductInDB | None:
        item.date_update = datetime.utcnow()
        if hasattr(item, "id"):
            delattr(item, "id")
        if hasattr(item, "date_insert"):
            delattr(item, "date_insert")
        if hasattr(item, "username_insert"):
            delattr(item, "username_insert")
        if hasattr(item, "disabled"):
            delattr(item, "disabled")
        # Codes and their stock are managed only through add_codes/assign_code
        exclude = {"discount_codes"}
        if item.kind == "discount_code":
            exclude.add("stock")
        updated = cls.TABLE.find_one_and_update(
            {"_id": id, "disabled": False},
            {"$set": item.dict(by_alias=True, exclude=exclude)},
            return_document=ReturnDocument.AFTER,
        )
        if updated is not None:
            return ProductInDB(**updated)
        else:
            return None

    @classmethod
    def get(cls, id: PyObjectId) -> ProductInDB | None:
        item = cls.TABLE.find_one({"_id": id, "disabled": False})
        if item is not None:
            return ProductInDB(**item)
        return item

    @classmethod
    def get_enable_to_buy(cls, id: PyObjectId) -> ProductInDB | None:
        item = cls.TABLE.find_one({"_id": id, "disabled": False, "able_to_buy": True})
        if item is not None:
            return ProductInDB(**item)
        return item

    @classmethod
    def get_all(cls) -> list[ProductInDB]:
        items = cls.TABLE.find({"disabled": False})
        return [ProductInDB(**item) for item in items]

    @classmethod
    def get_virtual_meal(cls) -> ProductInDB | None:
        item = cls.TABLE.find_one(
            {
                "disabled": False,
                "is_virtual_meal": True,
                "kind": {"$ne": "physical"},
                "$or": [{"stock": None}, {"stock": {"$gt": 0}}],
            },
        )
        if item is not None:
            return ProductInDB(**item)
        return None

    @classmethod
    def reserve_stock(cls, id: PyObjectId) -> bool:
        item = cls.TABLE.find_one({"_id": id, "disabled": False})
        if item is None:
            return False
        if item.get("stock") is None:
            return True
        updated = cls.TABLE.find_one_and_update(
            {"_id": id, "disabled": False, "stock": {"$gt": 0}},
            {"$inc": {"stock": -1}, "$set": {"date_update": datetime.utcnow()}},
        )
        return updated is not None

    @classmethod
    def release_stock(cls, id: PyObjectId) -> None:
        cls.TABLE.update_one(
            {"_id": id, "stock": {"$ne": None}},
            {"$inc": {"stock": 1}, "$set": {"date_update": datetime.utcnow()}},
        )

    @classmethod
    def add_codes(cls, id: PyObjectId, codes: list[str]) -> ProductInDB | None:
        item = cls.TABLE.find_one({"_id": id, "disabled": False})
        if item is None:
            return None
        current = item.get("discount_codes", [])
        existing = {c["code"] for c in current}
        new_codes = []
        for code in codes:
            code = code.strip()
            if code and code not in existing:
                existing.add(code)
                new_codes.append(DiscountCode(code=code).dict())
        if item.get("stock") is None:
            available = sum(1 for c in current if c.get("assigned_to") is None)
            cls.TABLE.update_one(
                {"_id": id, "stock": None},
                {"$set": {"stock": available}},
            )
        updated = cls.TABLE.find_one_and_update(
            {"_id": id, "disabled": False},
            {
                "$push": {"discount_codes": {"$each": new_codes}},
                "$inc": {"stock": len(new_codes)},
                "$set": {"date_update": datetime.utcnow()},
            },
            return_document=ReturnDocument.AFTER,
        )
        if updated is not None:
            return ProductInDB(**updated)
        return None

    @classmethod
    def assign_code(cls, id: PyObjectId, control_code: str) -> str | None:
        now = datetime.utcnow()
        # Positional $ targets the first unassigned code, so BEFORE tells us which one
        before = cls.TABLE.find_one_and_update(
            {
                "_id": id,
                "disabled": False,
                "stock": {"$gt": 0},
                "discount_codes": {"$elemMatch": {"assigned_to": None}},
            },
            {
                "$set": {
                    "discount_codes.$.assigned_to": control_code,
                    "discount_codes.$.date_assigned": now,
                    "date_update": now,
                },
                "$inc": {"stock": -1},
            },
            projection={"discount_codes": 1},
            return_document=ReturnDocument.BEFORE,
        )
        if before is None:
            return None
        return next(
            c["code"] for c in before["discount_codes"] if c.get("assigned_to") is None
        )

    @classmethod
    def release_code(cls, id: PyObjectId, code: str) -> None:
        cls.TABLE.update_one(
            {"_id": id, "discount_codes.code": code},
            {
                "$set": {
                    "discount_codes.$.assigned_to": None,
                    "discount_codes.$.date_assigned": None,
                    "date_update": datetime.utcnow(),
                },
                "$inc": {"stock": 1},
            },
        )
