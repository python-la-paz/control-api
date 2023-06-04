from datetime import datetime
from typing import List
from pymongo.collection import ReturnDocument

from app.core.database import db
from app.models.combo import ComboInDB, RedeemComboInDB
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
    def update(cls, id:PyObjectId, item: ComboInDB) -> ComboInDB | None:
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
            return ComboInDB(**updated)
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
    
class RedeemComboService:
    TABLE = db.redeem_combos

    @classmethod
    def insert(cls, item: RedeemComboInDB) -> RedeemComboInDB:
        if hasattr(item, "id"):
            delattr(item, "id")
        item.date_insert = datetime.utcnow()
        item.date_update = item.date_insert
        inserted = cls.TABLE.insert_one(item.dict(by_alias=True))
        item.id = inserted.inserted_id
        return item
    
    @classmethod
    def get_all(cls) -> List[RedeemComboInDB]:
        items = cls.TABLE.find({"disabled": False})
        return [RedeemComboInDB(**item) for item in items]

    @classmethod
    def search_by_participant_and_combo(cls, participant_control_code: str, combo_id: PyObjectId) -> List[RedeemComboInDB]:
        items = cls.TABLE.find({"participant_control_code": participant_control_code, "combo": combo_id ,  "disabled": False})
        return [RedeemComboInDB(**item) for item in items]
    
    @classmethod
    def search_by_participant(cls, participant_control_code: str) -> List[RedeemComboInDB]:
        items = cls.TABLE.find({"participant_control_code": participant_control_code, "disabled": False})
        return [RedeemComboInDB(**item) for item in items]
