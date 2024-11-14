from datetime import datetime
from pymongo.collection import ReturnDocument

from app.core.database import db
from app.models.participant import ParticipantInDB
from app.utils.mongo_validator import PyObjectId


class ParticipantService:
    TABLE = db.participants
    REVOKE_TABLE = db.revoke
    @classmethod
    def insert(cls, item: ParticipantInDB) -> ParticipantInDB:
        if hasattr(item, "id"):
            delattr(item, "id")
        if hasattr(item, "combos_items"):
            delattr(item, "combos_items")
        if hasattr(item, "locations_items"):
            delattr(item, "locations_items")
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
    def get_all_ids(cls) -> list[str]:
        """Get array of ids"""
        items = cls.TABLE.find({"disabled": False})
        return [str(item["_id"]) for item in items]

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
    def get_by_control_code_full(
        cls, control_code: str
    ) -> ParticipantInDB | None | bool:
        query = [
            {
                "$lookup": {
                    "from": "locations",
                    "localField": "locations",
                    "foreignField": "_id",
                    "as": "locations_info",
                }
            },
            {
                "$lookup": {
                    "from": "combos",
                    "localField": "combos",
                    "foreignField": "_id",
                    "as": "combos_info",
                }
            },
            {"$match": {"disabled": False, "control_code": control_code}},
            {
                "$project": {
                    "_id": 1,
                    "name": 1,
                    "gender": 1,
                    "t_shirt_size": 1,
                    "food_restriction": 1,
                    "registration": 1,
                    "phone": 1,
                    "role": 1,
                    "combos": 1,
                    "points": 1,
                    "locations": 1,
                    "locations_items": {
                        "$map": {
                            "input": "$locations_info",
                            "as": "locations",
                            "in": "$$locations.name",
                        }
                    },
                    "combos_items": {
                        "$map": {
                            "input": "$combos_info",
                            "as": "combos",
                            "in": "$$combos.name",
                        }
                    },
                }
            },
        ]
        items = cls.TABLE.aggregate(query)
        result = [ParticipantInDB(**item) for item in items]
        if len(result) == 1:
            return result[0]
        elif len(result) > 1:
            return False
        else:
            return None

    @classmethod
    def get_by_control_ci(cls, ci: str) -> ParticipantInDB | None | bool:
        finds = cls.TABLE.find({"ci": ci, "disabled": False})
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
    def exist_control_code(cls, control_code: str) -> bool:
        item = cls.TABLE.find_one({"control_code": control_code, "disabled": False})
        if item is not None:
            return True
        return False

    @classmethod
    def finish_registration(
        cls, id: PyObjectId, control_code: str
    ) -> ParticipantInDB | None:
        updated = cls.TABLE.find_one_and_update(
            {"_id": id, "disabled": False},
            {
                "$set": {
                    "control_code": control_code,
                    "registration": True,
                    "date_update": datetime.utcnow(),
                }
            },
            return_document=ReturnDocument.AFTER,
        )
        if updated is not None:
            return ParticipantInDB(**updated)
        else:
            return None

    @classmethod
    def insert_many(cls, items: list[ParticipantInDB], delete_id=True) -> list[PyObjectId]:
        for item in items:
            if hasattr(item, "id") and delete_id:
                delattr(item, "id")
            if hasattr(item, "locations_items"):
                delattr(item, "locations_items")
            if hasattr(item, "combos_items"):
                delattr(item, "combos_items")
            item.date_insert = datetime.utcnow()
            item.date_update = item.date_insert
        inserted = cls.TABLE.insert_many([item.dict(by_alias=True) for item in items])
        return inserted.inserted_ids
    
    @classmethod
    def finish_unregistration(cls, id: PyObjectId, user:str) -> ParticipantInDB | None:
        updated = cls.TABLE.find_one_and_update(
            {"_id": id, "disabled": False},
            {
                "$set": {
                    "control_code": "",
                    "registration": False,
                    "date_update": datetime.utcnow(),
                    "username_update": user
                }
            },
            return_document=ReturnDocument.AFTER,
        )
        if updated is not None:
            return ParticipantInDB(**updated)
        else:
            return None
        
    @classmethod
    def save_revoke(cls, id: PyObjectId, control_code: str, ci: str, user:str) -> bool:
        cls.REVOKE_TABLE.insert_one({
            "participant_id": id,
            "control_code": control_code,
            "ci": ci,
            "date_insert": datetime.utcnow(),
            "username_insert": user
        })
        return True