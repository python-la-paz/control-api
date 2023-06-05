from datetime import datetime
from pymongo.collection import ReturnDocument

from app.core.database import db
from app.models.participant import ParticipantInDB
from app.utils.mongo_validator import PyObjectId


class ParticipantService:
    TABLE = db.participants

    @classmethod
    def insert(cls, item: ParticipantInDB) -> ParticipantInDB:
        if hasattr(item, "id"):
            delattr(item, "id")
        item.date_insert = datetime.utcnow()
        item.date_update = item.date_insert
        inserted = cls.TABLE.insert_one(item.dict(by_alias=True))
        item.id = inserted.inserted_id
        return item

    @classmethod
    def delete(cls, id: PyObjectId) -> ParticipantInDB | None:
        deleted = cls.TABLE.find_one_and_update(
            {"_id": id},
            {"$set": {"disabled": True}},
            return_document=ReturnDocument.AFTER,
        )
        if deleted is not None:
            return ParticipantInDB(**deleted)
        else:
            return None

    @classmethod
    def get(cls, id: PyObjectId) -> ParticipantInDB | None:
        item = cls.TABLE.find_one({"_id": id, "disabled": False})
        if item is not None:
            return ParticipantInDB(**item)
        return item

    @classmethod
    def get_all(cls) -> list[ParticipantInDB]:
        items = cls.TABLE.find({"disabled": False})
        return [ParticipantInDB(**item) for item in items]

    @classmethod
    def get_by_control_code(cls, control_code: str) -> ParticipantInDB | None | bool:
        finds = cls.TABLE.find({"control_code": control_code, "disabled": False})
        items = []
        for find in finds:
            items.append(ParticipantInDB(**find))

        if len(items) == 1:
            return items[0]
        elif len(items) > 1:
            return False
        else:
            return None

    @classmethod
    def add_points(cls, id: PyObjectId, points: int) -> ParticipantInDB | None:
        updated = cls.TABLE.find_one_and_update(
            {"_id": id, "disabled": False},
            {"$inc": {"points": points}, "$set": {"date_update": datetime.utcnow()}},
            return_document=ReturnDocument.AFTER,
        )
        if updated is not None:
            return ParticipantInDB(**updated)
        else:
            return None

    @classmethod
    def subtract_points(cls, id: PyObjectId, points: int) -> ParticipantInDB | None:
        updated = cls.TABLE.find_one_and_update(
            {"_id": id, "disabled": False},
            {"$inc": {"points": -points}, "$set": {"date_update": datetime.utcnow()}},
            return_document=ReturnDocument.AFTER,
        )
        if updated is not None:
            return ParticipantInDB(**updated)
        else:
            return None
    
    @classmethod
    def get_by_ci(cls, ci: str) -> ParticipantInDB | None:
        item = cls.TABLE.find_one({"ci": ci, "disabled": False})
        if item is not None:
            return ParticipantInDB(**item)
        return item

    @classmethod
    def exist_control_code (cls, control_code: str) -> bool:
        item = cls.TABLE.find_one({"control_code": control_code, "disabled": False})
        if item is not None:
            return True
        return False
    
    @classmethod
    def finish_registration (cls, id: PyObjectId, control_code: str) -> ParticipantInDB | None:
        updated = cls.TABLE.find_one_and_update(
            {"_id": id, "disabled": False},
            {"$set": {"control_code": control_code, "registration": True, "date_update": datetime.utcnow()}},
            return_document=ReturnDocument.AFTER,
        )
        if updated is not None:
            return ParticipantInDB(**updated)
        else:
            return None