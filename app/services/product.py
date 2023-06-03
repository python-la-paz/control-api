from datetime import datetime
from pymongo.collection import ReturnDocument

from app.core.database import db
from app.models.product import ProductInDB
from app.utils.mongo_validator import PyObjectId


class ProductService:
    TABLE = db.products

    @classmethod
    def insert(cls, item: ProductInDB) -> ProductInDB:
        if hasattr(item, "id"):
            delattr(item, "id")
        item.date_insert = datetime.utcnow()
        item.date_update = item.date_insert
        inserted = cls.TABLE.insert_one(item.dict(by_alias=True))
        item.id = inserted.inserted_id
        return item

    @classmethod
    def delete(cls, id: PyObjectId) -> ProductInDB | None:
        deleted = cls.TABLE.find_one_and_update( {"_id": id}, {"$set": {"disabled": True}}, return_document=ReturnDocument.AFTER)
        if deleted is not None:
            return ProductInDB(**deleted)
        else:
            return None
    
    @classmethod
    def update(cls, id:PyObjectId, item: ProductInDB) -> ProductInDB | None:
        item.date_update = datetime.utcnow()
        if hasattr(item, "id"):
            delattr(item, "id")
        if hasattr(item, "date_insert"):
            delattr(item, "date_insert")
        if hasattr(item, "username_insert"):
            delattr(item, "username_insert")
        if hasattr(item, "disabled"):
            delattr(item, "disabled")
        updated = cls.TABLE.find_one_and_update( {"_id": id, "disabled": False}, {"$set": item.dict(by_alias=True)}, return_document=ReturnDocument.AFTER)
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
    def get_all(cls) -> list[ProductInDB]:
        items = cls.TABLE.find({"disabled": False})
        return [ProductInDB(**item) for item in items]